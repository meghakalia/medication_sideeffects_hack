
# openai api use to get alternative names

# get popular subreditts 

# organize data in json

# ask questions. 

import praw 
from time import sleep
import ast
from openai import OpenAI
import os
import openai
import re
import json

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']


reddit_client_id = os.environ['REDDIT_CLIENT_ID']
reddit_secret_key = os.environ['REDDIT_CLIENT_SECRET']

user_agent = "Scraper 1.0 by /u/python_engineer"
reddit = praw.Reddit (
client_id=reddit_client_id,
client_secret=reddit_secret_key,
user_agent=user_agent
)


topic = "Accutane"
subreddits = reddit.subreddits.search(topic)

# for subreddit in subreddits:
#   print(f"Subreddit: {subreddit.display_name}, Subscribers: {subreddit.subscribers}")

def filter_side_effect_comments(comments, keywords):
    filtered_comments = []
    
    for comment in comments:
        if any(keyword.lower() in comment.lower() for keyword in keywords):
            filtered_comments.append(comment)
    
    return filtered_comments
# Function to get all comments from a specific post
def get_comments_from_post(post_id):
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=None)  # Expand 'more' comments
    
    # Create a list to store the comments
    comments_list = []
    
    for comment in submission.comments.list():  # Fetch all comments
        comments_list.append(comment.body)  # Append the text of each comment
    
    return comments_list


def get_posts_with_most_comments(subreddit_name, num_posts=10):
    subreddit = reddit.subreddit(subreddit_name)
    
    # Fetch the top/hot posts (can modify this to fetch more if needed)
    posts = subreddit.hot(limit=100)  # You can change 'hot' to 'top', 'new', etc.
    
    # Create a list of posts and their comment counts
    post_list = []
    
    for post in posts:
        post_list.append({
            'title': post.title,
            'score': post.score,
            'url': post.url,
            'comments': post.num_comments,
            'created': post.created_utc,
            'id': post.id
        })
    
    # Sort the posts by the number of comments in descending order
    sorted_posts = sorted(post_list, key=lambda x: x['comments'], reverse=True)
    
    # Return the top 'num_posts' with the most comments
    return sorted_posts[:num_posts]

def find_highest_commented_post(subreddit_name, limit=100):
    subreddit = reddit.subreddit(subreddit_name)
    
    # Fetch 'hot' posts (or use 'top', 'new', etc.)
    posts = subreddit.hot(limit=limit)
    
    highest_commented_post = None
    max_comments = 0
    
    for post in posts:
        if post.num_comments > max_comments:
            max_comments = post.num_comments
            highest_commented_post = post
    
    return highest_commented_post, max_comments

 
def print_comments_from_post(post):
    # Ensure all comments are loaded
    post.comments.replace_more(limit=None)
    
    final_comments = []
    for comment in post.comments.list():
        if comment.author and comment.author.name != 'AutoModerator':
            final_comments.append(comment.body)
            # print(comment.body)
            sleep(0.005)
            

        # print(f"Comment by {comment.author}: {comment.body}\n")
    return final_comments,''.join(final_comments)

# # Example usage
# subreddit_name = 'Accutane'  # Replace with the subreddit you want to search
# highest_commented_post, max_comments = find_highest_commented_post(subreddit_name)

# # Print the details of the post with the most comments
# if highest_commented_post:
#     # print(f"Title: {highest_commented_post.title}")
#     # print(f"Comments: {max_comments}")
#     # print(f"Score: {highest_commented_post.score}")
#     # print(f"URL: {highest_commented_post.url}\n")
    
#     # Print all the comments in the thread
#     print("Comments:\n")
#     comment_list, comments =  print_comments_from_post(highest_commented_post)
#     # print(comments)
# else:
#     print("No posts found.")




def parse_resp(resp):
    matches = re.findall(r'```json(.*?)```', resp, re.DOTALL)
    if matches:
        return ast.literal_eval(matches[0].strip())

def find_side_effects(text, side_effect):

    prompt = f"""Did you find the '{side_effect}' in the following text and return relevant sentences:\n\n{text}.
    Arrange your response under sections as follows: 
    in a json file format as follows(encapsulate your output in triple backticks):
    ```json{{
        "symptom": "{side_effect}",
        "symptom present or not": "..." 
    }}```

    Output:"""

    client = OpenAI()

    response = openai.chat.completions.create(
    model="gpt-4o",  # Specify GPT-4 model
    messages=[
        {"role": "system", "content": "You are a helpful retrieval system."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=1000,  # Maximum tokens to be returned in the response
    temperature=0.0  # Temperature controls randomness. Lower is more deterministic.
    )

    return response.choices[0].message.content
    
# data = json.loads(find_side_effects(text, side_effect))
# data = parse_resp(find_side_effects(text, side_effect))

# print(find_side_effects(text, side_effect))
# Function to get all post information into a single string

# abby's code 
# Function to get top posts from a list of subreddits
def get_top_posts_from_subreddits(subreddits, num_posts=10):
    top_posts = []
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        posts = subreddit.hot(limit=100)  # Fetch hot posts, adjust to 'top' or 'new'
        
        # Collect post data and append it to the list
        for post in posts:
            top_posts.append({
                'title': post.title,
                'score': post.score,
                'url': post.url,
                'comments': post.num_comments,
                'created': post.created_utc,
                'id': post.id,
                'subreddit': subreddit_name
            })
    
    # Sort all posts by the number of comments in descending order
    sorted_posts = sorted(top_posts, key=lambda x: x['comments'], reverse=True)
    
    # Return only the top `num_posts` across all subreddits
    return sorted_posts[:num_posts]

# Function to assemble information for a single post
def append_multiple_strings(strings):
    """Append multiple strings together into a single string."""
    return ''.join(strings)

def assemble_post_info(post_data):
    post_info_parts = []  # List to hold parts of the string
    post_info_parts.append(f"Post Title: {post_data['title']}")
    post_info_parts.append(f"Subreddit: {post_data['subreddit']}")
    post_info_parts.append(f"URL: {post_data['url']}")
    post_info_parts.append(f"Number of Filtered Comments: {len(post_data['comments'])}")
    post_info_parts.append("Filtered Comments:\n")

    for idx, comment in enumerate(post_data['comments']):
        post_info_parts.append(f"{idx + 1}: {comment}\n")

    return append_multiple_strings(post_info_parts)  # Use the new function here

def get_all_post_info(subreddits, num_posts=10, symptoms=None):
    if symptoms is None:
        keywords = ['side effect', 'side effects', 'unexpected', 'normal', 'weird', 
                    'reaction']
    else:
        keywords = ['side effect', 'side effects', 'unexpected', 'normal', 'weird', 
                    'reaction']
        for words in symptoms:
            keywords.append(words)

    # Get top commented posts from subreddits
    top_commented_posts = get_top_posts_from_subreddits(subreddits, num_posts)
    
    # Dictionary to store filtered comments from each post
    filtered_comments_by_post = {}

    # Loop over the top posts and fetch comments
    for post in top_commented_posts:
        #print(f"Fetching comments from post: {post['title']} (Subreddit: {post['subreddit']})")
        
        # Get all comments from the post
        comments = get_comments_from_post(post['id'])
        
        # Filter comments for side effect mentions
        filtered_comments = filter_side_effect_comments(comments, keywords)
        
        # Store the filtered comments in the dictionary, keyed by post ID
        if filtered_comments:
            filtered_comments_by_post[post['id']] = {
                'title': post['title'],
                'subreddit': post['subreddit'],
                'url': post['url'],
                'comments': filtered_comments
            }

    # Assemble all information into a single string
    all_post_info = ""
    for post_id, post_data in filtered_comments_by_post.items():
        all_post_info += assemble_post_info(post_data) + "\n\n"  # Add double newline for separation

    return all_post_info  # Return the complete information string


subreddits = ['Accutane']
complete_info = get_all_post_info(subreddits, num_posts=10, symptoms = "dryness")  # Get all post info

text = complete_info
side_effect = 'muscular pain'

# print(get_all_post_info(subreddits))
# print(find_side_effects(complete_info, "dryness"))


# print()
def reddit_side_effects(drug, side_effect):

    # read the data reddit 
    text = get_all_post_info(drug, num_posts=10, symptoms = side_effect)  # Get all post info

    # get from reddit 
    data = parse_resp(find_side_effects(text, side_effect))

    return data

print(reddit_side_effects(["Accutane"], "dryness"))

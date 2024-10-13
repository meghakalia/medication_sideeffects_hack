import praw 
import openai
import os
import re
import ast

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


# Function to get top posts from a list of subreddits
def get_top_posts_from_subreddits(subreddits, num_posts=10):
    top_posts = []
    
    # for subreddit_name in subreddits:
    subreddit_name = subreddits
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
    

# the main function
def reddit_side_effects(drug, side_effect):

    # read the data reddit 
    text = get_all_post_info(drug, num_posts=10, symptoms = side_effect)  # Get all post info

    # get from reddit 
    data = parse_resp(find_side_effects(text, side_effect))

    return data

# print(reddit_side_effects("Accutane", "dryness"))

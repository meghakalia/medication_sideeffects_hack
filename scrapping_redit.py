
# openai api use to get alternative names

# get popular subreditts 

# organize data in json

# ask questions. 

import praw 

from openai import OpenAI
import os
import openai

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

for subreddit in subreddits:
  print(f"Subreddit: {subreddit.display_name}, Subscribers: {subreddit.subscribers}")


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
    
    for comment in post.comments.list():
        print(f"Comment by {comment.author}: {comment.body}\n")

# Example usage
subreddit_name = 'Accutane'  # Replace with the subreddit you want to search
highest_commented_post, max_comments = find_highest_commented_post(subreddit_name)

# Print the details of the post with the most comments
if highest_commented_post:
    print(f"Title: {highest_commented_post.title}")
    print(f"Comments: {max_comments}")
    print(f"Score: {highest_commented_post.score}")
    print(f"URL: {highest_commented_post.url}\n")
    
    # Print all the comments in the thread
    print("Comments:\n")
    print_comments_from_post(highest_commented_post)
else:
    print("No posts found.")

# subreddit_name = 'Accutane'  # Replace with the subreddit you want to scrape
# top_commented_posts = get_posts_with_most_comments(subreddit_name)


# get the comments 
# openai.api_key  = os.environ['OPENAI_API_KEY']

# use LLM to organize the data





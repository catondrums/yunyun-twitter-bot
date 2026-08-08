import json
import random
import time
import os
import tweepy

# Load OAuth 2.0 user access token
user_access_token = os.environ["X_OAUTH_TOKEN"]

# Connect to X using OAuth 2.0 User Context
client = tweepy.Client(user_access_token)

# Load all tweets
with open("tweets.json", "r", encoding="utf-8") as f:
    tweets = json.load(f)

# Load the remaining tweet IDs
with open("state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

remaining = state["remaining"]

# If the previous cycle is finished, start a new one
if not remaining:
    remaining = [tweet["id"] for tweet in tweets]
    random.shuffle(remaining)

# Pick one random unused tweet
tweet_id = remaining.pop()

# Find the tweet's text
tweet = next(tweet for tweet in tweets if tweet["id"] == tweet_id)
text = tweet["text"]

print(f"Posting: {text}")

# Post to X using OAuth 2.0 User Context
for attempt in range(3):
    try:
        response = client.create_tweet(
            text=text,
            user_auth=False
        )
        break
    except tweepy.TwitterServerError as e:
        if attempt < 2:
            wait_time = 2 ** attempt
            print(f"X server error. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            raise
        

print(f"Posted successfully! Tweet ID: {response.data['id']}")

# Only save the updated state after X successfully accepted the post

state["remaining"] = remaining

with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)

print(f"{len(remaining)} tweets remaining in this cycle.")

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

# Keep trying tweets until one is successfully posted
while remaining:
    # Pick one random unused tweet
    tweet_id = remaining.pop()

    # Find the tweet's text
    tweet = next(tweet for tweet in tweets if tweet["id"] == tweet_id)
    text = tweet["text"]

    print(f"Posting: {text}")

    # Try posting, with retries for temporary X server errors
    for attempt in range(3):
        try:
            response = client.create_tweet(
                text=text,
                user_auth=False
            )

            print(f"Posted successfully! Tweet ID: {response.data['id']}")

            # Save state immediately after successful post
            state["remaining"] = remaining

            with open("state.json", "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)

            print(f"{len(remaining)} tweets remaining in this cycle.")
            raise SystemExit(0)

        except tweepy.Forbidden as e:
            error_text = e.response.text if e.response is not None else str(e)

            # X rejects duplicate tweet content with HTTP 403.
            # Discard this tweet and move to the next one.
            if "duplicate content" in error_text.lower():
                print("X rejected this tweet as a duplicate.")
                print("Skipping it and trying the next tweet.")
                break

            # Other 403 errors are unexpected and should stop the workflow.
            print("X returned a 403 Forbidden error!")
            print("Response:", error_text)
            raise

        except tweepy.TwitterServerError as e:
            print("X returned a server error!")
            print("Status:", e.response.status_code)
            print("Response:", e.response.text)

            if attempt < 2:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

# If we get here, every remaining tweet was rejected/skipped.
# Start a fresh cycle next time.
state["remaining"] = []

with open("state.json", "w", encoding="utf-8") as f:
    json.dump(state, f, indent=2)

print("No usable tweets remained. The next run will start a new cycle.")
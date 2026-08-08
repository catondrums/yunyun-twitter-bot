import os

# Allow OAuthlib to accept our local HTTP callback
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import tweepy
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("X_CLIENT_ID")
CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")

print("Client ID loaded:", CLIENT_ID is not None)
print("Client Secret loaded:", CLIENT_SECRET is not None)

REDIRECT_URI = "http://localhost:3000/callback"

SCOPES = [
    "tweet.read",
    "tweet.write",
    "users.read",
    "offline.access"
]

oauth2_user_handler = tweepy.OAuth2UserHandler(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES
)

print("\nGenerating authorization URL...")

authorization_url = oauth2_user_handler.get_authorization_url()

print("\nOPEN THIS URL:")
print(authorization_url)

print("\nAfter you authorize the app, X will redirect you.")
print("Copy the ENTIRE URL from your browser and paste it below.")

callback_url = input("\nCallback URL: ")

token = oauth2_user_handler.fetch_token(callback_url)

print("\nAuthentication successful!")
print("Access token received.")

with open("oauth_token.txt", "w") as f:
    f.write(token["access_token"])

print("Saved user access token to oauth_token.txt")
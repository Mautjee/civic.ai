from dotenv import load_dotenv
import tweepy
import os

# Load environment variables
load_dotenv()

def test_twitter_connection():
    # Get credentials from environment variables
    consumer_key = os.getenv("TWITTER_API_KEY").strip()
    consumer_secret = os.getenv("TWITTER_API_SECRET").strip()
    access_token = os.getenv("TWITTER_ACCESS_TOKEN").strip()
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET").strip()
    
    # Initialize Twitter client
    client = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    # Try to post a test tweet
    test_tweet = "🧪 Testing Twitter connection from ETHGlobal War Reporter... Stand by for live coverage! #test"
    response = client.create_tweet(text=test_tweet)
    
    print("✅ Test tweet successful!")
    print(f"Tweet ID: {response.data['id']}")
    return True

if __name__ == "__main__":
    test_twitter_connection()
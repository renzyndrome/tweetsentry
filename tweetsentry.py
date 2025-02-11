import os
import time
import json
import urllib.parse
import requests
import tweepy
from dotenv import load_dotenv
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init()

# Load environment variables
load_dotenv()


class TwitterWatcher:
    """Main class for TweetSentry that handles monitoring and status detection"""

    def __init__(self):
        # Load Twitter API credentials
        self.client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'))
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.last_tweet_id = None

        # API endpoints
        self.base_url = "https://api.twitter.com/2"

    def get_user_info(self, username):
        """Get user information using Twitter API v2"""
        url = f"{self.base_url}/users/by/username/{username}"

        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        params = {"user.fields": "protected,verified,public_metrics,withheld"}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if 'errors' in data:
                error = data['errors'][0]
                if error.get('title') == 'Not Found Error':
                    if 'suspended' in error.get('detail', '').lower():
                        print(f"{Fore.RED}Account @{username} has been banned{Style.RESET_ALL}")
                        return None, "BANNED"
                    else:
                        print(f"{Fore.RED}User @{username} not found{Style.RESET_ALL}")
                        return None, None
                else:
                    print(f"{Fore.RED}Error: {error.get('detail', 'Unknown error')}{Style.RESET_ALL}")
                    return None, None

            if 'data' not in data:
                print(f"{Fore.RED}No data returned for @{username}{Style.RESET_ALL}")
                return None, None

            user_data = data['data']
            status = []

            if user_data.get('protected'):
                status.append("PRIVATE")
            if user_data.get('verified'):
                status.append("VERIFIED")
            if user_data.get('withheld'):
                status.append("WITHHELD")

            # Get tweets to check for sensitive content
            user_id = user_data.get('id')
            if user_id:
                tweets = self.client.get_users_tweets(
                    user_id,
                    max_results=5,
                    tweet_fields=['possibly_sensitive']
                )
                if tweets.data and any(tweet.possibly_sensitive for tweet in tweets.data):
                    status.append("SENSITIVE")

            status_str = " | ".join(status) if status else "PUBLIC"

            print(f"\n{Fore.CYAN}Account Information for @{username}:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Status: {status_str}{Style.RESET_ALL}")

            metrics = user_data.get('public_metrics', {})
            if metrics:
                print(f"{Fore.CYAN}Followers: {metrics.get('followers_count', 0)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Following: {metrics.get('following_count', 0)}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Tweet Count: {metrics.get('tweet_count', 0)}{Style.RESET_ALL}")

            return user_data.get('id'), status_str

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}Error getting user information: {e}{Style.RESET_ALL}")
            return None, None

    def get_latest_tweets(self, user_id, max_results=5):
        """Get latest tweets from user"""
        try:
            tweets = self.client.get_users_tweets(
                user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'text', 'public_metrics', 'possibly_sensitive']
            )
            if tweets.data and any(tweet.possibly_sensitive for tweet in tweets.data):
                print(f"{Fore.YELLOW}Warning: This account has tweets marked as sensitive content{Style.RESET_ALL}")
            return tweets.data if tweets.data else []
        except Exception as e:
            print(f"{Fore.RED}Error fetching tweets: {e}{Style.RESET_ALL}")
            return []

    def watch_account(self, username, interval=60):
        """Watch a Twitter account for new tweets"""
        print(f"{Fore.CYAN}Starting to watch @{username}'s tweets...{Style.RESET_ALL}")

        # Get user information and status
        user_id, status = self.get_user_info(username)

        if not user_id:
            if status == "BANNED":
                print(f"{Fore.RED}Cannot watch banned account.{Style.RESET_ALL}")
            return

        if "PRIVATE" in status:
            print(f"{Fore.YELLOW}Note: This is a private account. You may not see tweets unless you're an approved follower.{Style.RESET_ALL}")

        while True:
            try:
                tweets = self.get_latest_tweets(user_id)
                if tweets:
                    newest_tweet = tweets[0]

                    # If this is the first run or we have a new tweet
                    if self.last_tweet_id is None or newest_tweet.id != self.last_tweet_id:
                        self.last_tweet_id = newest_tweet.id

                        # Only print if it's not the first run
                        if self.last_tweet_id is not None:
                            print(f"\n{Fore.GREEN}New tweet detected!{Style.RESET_ALL}")
                            print(f"{Fore.YELLOW}Time: {newest_tweet.created_at}{Style.RESET_ALL}")

                            # Show tweet metrics
                            metrics = getattr(newest_tweet, 'public_metrics', {})
                            if metrics:
                                print(f"{Fore.CYAN}Likes: {metrics.get('like_count', 0)} | "
                                      f"Retweets: {metrics.get('retweet_count', 0)} | "
                                      f"Replies: {metrics.get('reply_count', 0)}{Style.RESET_ALL}")

                            print(f"{Fore.WHITE}{newest_tweet.text}{Style.RESET_ALL}\n")

                time.sleep(interval)

            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}Stopping tweet watcher...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
                time.sleep(interval)


def main():
    watcher = TwitterWatcher()
    username = input("Enter the Twitter/X username to watch (without @): ").strip()
    interval = input("Enter check interval in seconds (default: 180): ")

    try:
        interval = int(interval) if interval else 180
    except ValueError:
        print(f"{Fore.YELLOW}Invalid interval, using default: 180 seconds{Style.RESET_ALL}")
        interval = 180

    watcher.watch_account(username, interval)


if __name__ == "__main__":
    main()

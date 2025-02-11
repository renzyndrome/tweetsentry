import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

client = tweepy.Client(
    bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
    wait_on_rate_limit=True
)

def check_user(username):
    print(f"\nChecking @{username}...")
    try:
        # Get user with additional fields to check for sensitive content
        user = client.get_user(
            username=username,
            user_fields=['protected', 'withheld', 'description', 'possibly_sensitive']
        )
        print(f'Success! User found:')
        print(f'Response: {user}')
        
        if user.data:
            # Check if user data contains sensitive content markers
            user_data = user.data
            is_sensitive = getattr(user_data, 'possibly_sensitive', False)
            if is_sensitive:
                print(f"{username} has sensitive content")
            
            # Print other useful user information
            print(f"Protected: {getattr(user_data, 'protected', False)}")
            print(f"Withheld: {getattr(user_data, 'withheld', False)}")
            
        return user
    except tweepy.HTTPException as e:
        print(f'Error type: {type(e)}')
        print(f'Status code: {e.response.status_code if hasattr(e, "response") else "N/A"}')
        print(f'Error message: {e.api_errors if hasattr(e, "api_errors") else str(e)}')
        return None

# Test suspended account
check_user('toponlysearch')

# Test non-existent account
check_user('thisisanonexistentaccount123456789')

# Test active account
check_user('elonmusk')

# Test sensitive profile
check_user('Cocoyogii')

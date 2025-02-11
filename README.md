# TweetSentry 🛡️

> Real-time Twitter/X Account Monitor and Tweet Detector

A Python-based monitoring tool designed to:
1. **Detect New Tweets**: Continuously monitor a Twitter/X profile for new tweets in real-time
2. **Track Account Status**: Check and display account status (Public, Private, Banned, Sensitive, etc.)

## Key Features

- **Real-time Tweet Detection**
  - Instantly notifies when new tweets are posted
  - Shows tweet metrics (Likes, Retweets, Replies)
  - Displays tweet timestamp and content

- **Account Status Monitoring**
  - PUBLIC: Standard accessible account
  - PRIVATE: Protected tweets
  - BANNED: Suspended/banned account
  - SENSITIVE: Contains sensitive content
  - VERIFIED: Blue verified account
  - WITHHELD: Restricted in certain regions

## Prerequisites

- Python 3.6+
- Twitter API credentials (API v2)

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd tweetsentry
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Twitter API credentials:
```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

## Usage

Run the script:
```bash
python tweetsentry.py
```

You'll be prompted to:
1. Enter a Twitter/X username (without @)
2. Specify check interval in seconds (default: 180 - 3 minutes)

The script will then:
- Display account information
- Show account status (Public/Private/Verified/Banned)
- Monitor for new tweets
- Display tweet metrics and content
- Warn about sensitive content

To stop monitoring, press Ctrl+C.

## Example Output

```
Enter the Twitter/X username to watch (without @): username
Enter check interval in seconds (default: 180): 30

Account Information for @username:
Status: PUBLIC | VERIFIED
Followers: 1000
Following: 500
Tweet Count: 1234

New tweet detected!
Time: 2025-02-11 03:59:04+00:00
Likes: 10 | Retweets: 5 | Replies: 2
This is the tweet content!
```

## Error Handling

The script handles various scenarios:
- Banned accounts
- Private accounts
- Network errors
- Rate limiting
- Invalid usernames

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

[MIT License](https://github.com/renzycode/tweetsentry/blob/main/LICENSE)

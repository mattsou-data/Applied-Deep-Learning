from googleapiclient.discovery import build
from datetime import datetime, timedelta
from isodate import parse_duration
import pandas as pd
import sys
import os

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise ValueError("API key not found. Make sure it's set as an environment variable.")

CHANNEL_ID = 'UC5kh_CumIL_usjg3pW5J9Qw'
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to search for videos uploaded by the channel in the last 5 hours
def get_videos_last_5_hours(channel_id):
    

    # Calculate the time 5 hours ago
    time_5_hours_ago = (datetime.utcnow() - timedelta(days=2) - timedelta(hours=8)).isoformat() + 'Z'
    current_time = (datetime.utcnow()- timedelta(days=2)).isoformat()  + 'Z'

    # Use the search endpoint to get videos published in the last 5 hours
    response = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        publishedAfter=time_5_hours_ago,
        publishedBefore=current_time,
        type='video',
        maxResults=50
    ).execute()

    # Extract video IDs
    video_ids = [item['id']['videoId'] for item in response['items']]

    # Get video details to filter out Shorts
    if video_ids:
        video_details = youtube.videos().list(
            part='contentDetails',
            id=','.join(video_ids)
        ).execute()

        # Filter videos with duration longer than 1 minute
        regular_videos = [
            item['id']
            for item in video_details['items']
            if convert_duration_to_seconds(item['contentDetails']['duration']) >= 120
        ]

        return regular_videos

    return []


# Helper function to convert ISO 8601 duration to seconds
def convert_duration_to_seconds(duration):
    return int(parse_duration(duration).total_seconds())


# Example usage
videos = get_videos_last_5_hours(CHANNEL_ID)
print("Videos released in the last 5 hours (excluding Shorts): {}".format(videos))

def get_replies(youtube, parent_id, video_id):  
    replies = []
    next_page_token = None

    while True:
        reply_request = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            textFormat="plainText",
            maxResults=100,
            pageToken=next_page_token
        )
        reply_response = reply_request.execute()

        for item in reply_response['items']:
            comment = item['snippet']
            replies.append({
                'Timestamp': comment['publishedAt'],
                'Username': comment['authorDisplayName'],
                'VideoID': video_id,
                'Comment': comment['textDisplay'],
                'Date': comment['updatedAt'] if 'updatedAt' in comment else comment['publishedAt']
            })

        next_page_token = reply_response.get('nextPageToken')
        if not next_page_token:
            break

    return replies

# Function to get all comments (including replies) for a single video
def get_comments_for_video(youtube, video_id):
    all_comments = []
    next_page_token = None

    while True:
        comment_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token,
            textFormat="plainText",
            maxResults=100
        )
        comment_response = comment_request.execute()

        for item in comment_response['items']:
            top_comment = item['snippet']['topLevelComment']['snippet']
            all_comments.append({
                'Timestamp': top_comment['publishedAt'],
                'Username': top_comment['authorDisplayName'],
                'VideoID': video_id,  # Directly using video_id from function parameter
                'Comment': top_comment['textDisplay'],
                'Date': top_comment['updatedAt'] if 'updatedAt' in top_comment else top_comment['publishedAt']
            })

            # Fetch replies if there are any
            if item['snippet']['totalReplyCount'] > 0:
                all_comments.extend(get_replies(youtube, item['snippet']['topLevelComment']['id'], video_id))

        next_page_token = comment_response.get('nextPageToken')
        if not next_page_token:
            break

    return all_comments

if len(videos) != 0:
    # Function to get replies for a specific comment


    # List to hold all comments from all videos
    all_comments = []
    video_comments = get_comments_for_video(youtube, videos[0])
    all_comments.extend(video_comments)

    # Create DataFrame
    comments_df = pd.DataFrame(all_comments)
    # Columns are : Timestamp,Username,VideoID,Comment,Date

    # Save the DataFrame as a CSV file
    comments_df.to_csv('comments.csv', index=False)
 
    

else:
    
    # If there was no video that day, we still have to give a value for the indicator, so it will be the average of the seven previous days 
    # Import the saved csv with three columns, date, number of comments, percentage of possitive labels and add a new row for the day 
    # Create an empty DataFrame with desired column names
    empty_df = pd.DataFrame(columns=['Timestamp','Username','VideoID','Comment','Date'])

    # Save it as a CSV file
    empty_df.to_csv('comment.csv', index=False)


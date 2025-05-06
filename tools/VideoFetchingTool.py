from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")

class VideoFetchingTool(BaseTool):
    """
    Retrieves videos from a YouTube channel with sorting options (by views or by latest upload).
    Uses the YouTube Data API v3.
    """
    channel_id: str = Field(
        ..., description="The YouTube channel ID to fetch videos from."
    )
    sort_by: str = Field(
        ..., description="Sort videos by 'views' or 'latest'."
    )
    max_results: int = Field(
        10, description="Maximum number of videos to fetch."
    )

    def run(self):
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        # Get uploads playlist ID
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=self.channel_id
        ).execute()
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        # Fetch videos
        playlist_response = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=self.max_results
        ).execute()
        videos = []
        for item in playlist_response["items"]:
            video_id = item["contentDetails"]["videoId"]
            video_snippet = item["snippet"]
            videos.append({
                "videoId": video_id,
                "title": video_snippet["title"],
                "publishedAt": video_snippet["publishedAt"]
            })
        if self.sort_by == "views":
            # Fetch view counts for sorting
            for v in videos:
                stats = youtube.videos().list(
                    part="statistics",
                    id=v["videoId"]
                ).execute()
                v["viewCount"] = int(stats["items"][0]["statistics"]["viewCount"])
            videos.sort(key=lambda x: x["viewCount"], reverse=True)
        elif self.sort_by == "latest":
            videos.sort(key=lambda x: x["publishedAt"], reverse=True)
        return videos

if __name__ == "__main__":
    tool = VideoFetchingTool(channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw", sort_by="views", max_results=5)
    print(tool.run()) 
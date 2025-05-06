from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")

class VideoPerformanceAnalyzer(BaseTool):
    """
    Analyzes video performance, including metrics like views, likes, engagement, and fetches the top 5 comments from each video.
    Uses the YouTube Data API v3.
    """
    video_id: str = Field(
        ..., description="The YouTube video ID to analyze."
    )

    def run(self):
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        # Fetch video statistics
        video_response = youtube.videos().list(
            part="statistics,snippet",
            id=self.video_id
        ).execute()
        stats = video_response["items"][0]["statistics"]
        snippet = video_response["items"][0]["snippet"]
        performance = {
            "title": snippet.get("title"),
            "views": stats.get("viewCount"),
            "likes": stats.get("likeCount"),
            "comments": stats.get("commentCount"),
        }
        # Fetch top 5 comments
        comments_response = youtube.commentThreads().list(
            part="snippet",
            videoId=self.video_id,
            maxResults=5,
            order="relevance"
        ).execute()
        comments = []
        for item in comments_response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": top_comment["authorDisplayName"],
                "text": top_comment["textDisplay"]
            })
        performance["top_comments"] = comments
        return performance

if __name__ == "__main__":
    tool = VideoPerformanceAnalyzer(video_id="Ks-_Mh1QhMc")
    print(tool.run()) 
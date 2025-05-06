from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")

class ChannelDemographicsTool(BaseTool):
    """
    Fetches YouTube channel demographics such as subscriber count, audience age, gender, and location.
    Uses the YouTube Data API v3.
    """
    channel_id: str = Field(
        ..., description="The YouTube channel ID to fetch demographics for."
    )

    def run(self):
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        # Fetch channel statistics
        channel_response = youtube.channels().list(
            part="statistics,snippet",
            id=self.channel_id
        ).execute()
        stats = channel_response["items"][0]["statistics"]
        snippet = channel_response["items"][0]["snippet"]
        demographics = {
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "subscriberCount": stats.get("subscriberCount"),
            "viewCount": stats.get("viewCount"),
            "videoCount": stats.get("videoCount"),
        }
        # Audience age, gender, and location are not available via public API
        demographics["note"] = "Audience age, gender, and location are not available via the public YouTube Data API."
        return demographics

if __name__ == "__main__":
    tool = ChannelDemographicsTool(channel_id="UC_x5XG1OV2P6uZZ5FSM9Ttw")
    print(tool.run()) 
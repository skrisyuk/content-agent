import json
from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

youtube_api_key = os.getenv("YOUTUBE_API_KEY")

class CompetitorSearchTool(BaseTool):
    """
    Searches for and identifies competing YouTube channels based on a keyword or topic.
    Uses the YouTube Data API v3.
    """
    keyword: str = Field(
        ..., description="The keyword or topic to search for competing channels."
    )
    max_results: int = Field(
        10, description="Maximum number of competitor channels to return."
    )

    def run(self):
        youtube = build("youtube", "v3", developerKey=youtube_api_key)
        search_response = youtube.search().list(
            q=self.keyword,
            type="channel",
            part="snippet",
            maxResults=self.max_results
        ).execute()
        competitors = []
        for item in search_response["items"]:
            channel_id = item["snippet"]["channelId"]
            # Fetch channel statistics for subscriber count
            channel_stats = youtube.channels().list(
                part="statistics",
                id=channel_id
            ).execute()
            subscriber_count = channel_stats["items"][0]["statistics"].get("subscriberCount", "N/A")
            competitors.append({
                "channelId": channel_id,
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", ""),
                "subscriberCount": subscriber_count
            })
        # Sort by subscriberCount (convert to int, treat 'N/A' as 0)
        competitors.sort(key=lambda x: int(x["subscriberCount"]) if x["subscriberCount"].isdigit() else 0, reverse=True)
        return competitors

if __name__ == "__main__":
    tool = CompetitorSearchTool(keyword="AI agents development", max_results=3)
    print(json.dumps(tool.run(), indent=2, ensure_ascii=False)) 
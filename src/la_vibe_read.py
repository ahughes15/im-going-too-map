"""
LA vibe read, first real pipeline test.

Three steps:
1. Claude researches LA's current social/trend landscape using web search
2. We pull Google Trends data for the LA region (California)
3. Claude synthesizes both into a short "vibe read" for LA

This is a manual, single-city test. Once this works well, we template it
across all 17 cities and put it on a schedule.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

CITY_NAME = "Los Angeles"
TRENDS_GEO = "US-CA"  # California, closest available Google Trends region for LA


# --- Step 1: web search layer (stand-in for TikTok/Instagram trend signal) ---

def get_social_trend_summary(city_name: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=600,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search for what's currently trending on TikTok and Instagram "
                f"specifically in {city_name} this week or this month. Look for "
                f"trend reporting, local creator roundups, or marketing coverage. "
                f"Summarize the 3-5 most notable things you find in plain prose, "
                f"a few sentences each. If you can't find city-specific coverage, "
                f"say so plainly rather than guessing."
            ),
        }],
    )
    # Pull out just the text parts of the response (search results come back
    # as separate content blocks, we only want what Claude wrote)
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts)


# --- Step 2: Google Trends layer ---

def get_google_trends_summary(geo: str) -> str:
    pytrends = TrendReq(hl="en-US", tz=360)
    try:
        trending = pytrends.trending_searches(pn="united_states")
        top_terms = trending[0].tolist()[:10]
        return "Top trending Google searches (US): " + ", ".join(top_terms)
    except Exception as e:
        return f"Google Trends data unavailable this run: {e}"


# --- Step 3: synthesis ---

def synthesize_vibe_read(city_name: str, social_summary: str, trends_summary: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": (
                f"You're writing a short, opinionated 'vibe read' for {city_name} "
                f"as part of a living cultural map. Here's this week's raw signal:\n\n"
                f"SOCIAL TREND SIGNAL:\n{social_summary}\n\n"
                f"SEARCH TREND SIGNAL:\n{trends_summary}\n\n"
                f"Write 3-4 sentences capturing what {city_name}'s scene feels like "
                f"right now. Be specific and confident, not generic. This is a first "
                f"draft, tone/voice will be refined later."
            ),
        }],
    )
    return response.content[0].text


if __name__ == "__main__":
    print(f"Researching {CITY_NAME}...\n")
    social = get_social_trend_summary(CITY_NAME)
    print("--- SOCIAL SIGNAL ---")
    print(social)

    trends = get_google_trends_summary(TRENDS_GEO)
    print("\n--- TRENDS SIGNAL ---")
    print(trends)

    print("\n--- SYNTHESIZED VIBE READ ---")
    print(synthesize_vibe_read(CITY_NAME, social, trends))

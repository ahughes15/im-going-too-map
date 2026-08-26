"""
Quick sanity check: confirms the ANTHROPIC_API_KEY in .env works.
Run this once, then delete or ignore it, it's not part of the real pipeline.
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # reads the .env file and loads ANTHROPIC_API_KEY into the environment

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Reply with exactly one sentence confirming you're connected."}],
)

print(response.content[0].text)

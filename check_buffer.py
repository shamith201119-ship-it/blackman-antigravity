import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("BUFFER_ACCESS_TOKEN")
channel_id = os.getenv("BUFFER_CHANNEL_ID", "6a0c75a6090476fb99383a66")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 1. Check channel details
query_channel = f"""
query {
  channel(input: {id: "{channel_id}"}) {
    id
    name
    service
    isDisconnected
    organizationId
  }
}
"""

r_ch = requests.post("https://api.buffer.com", json={"query": query_channel}, headers=headers)
print("Channel Info:")
print(json.dumps(r_ch.json(), indent=2))

# 2. Check post status
query_post = """
query {
  node(id: "6a8dc762c90109d53dc3e331") {
    ... on Post {
      id
      status
      error
      createdAt
      dueAt
      text
    }
  }
}
"""
r_post = requests.post("https://api.buffer.com", json={"query": query_post}, headers=headers)
print("\nPost Info (6a8dc762c90109d53dc3e331):")
print(json.dumps(r_post.json(), indent=2))

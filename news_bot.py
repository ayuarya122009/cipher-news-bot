import os
import json
import hashlib
import feedparser
import requests

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
SEEN_FILE = "seen.json"

RSS_FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
]


def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def article_id(link):
    return hashlib.sha256(link.encode()).hexdigest()

def get_image(entry):
    # Try common RSS image formats
    if entry.get("media_content"):
        return entry["media_content"][0].get("url")

    if entry.get("media_thumbnail"):
        return entry["media_thumbnail"][0].get("url")

    for link in entry.get("links", []):
        if link.get("rel") == "enclosure":
            if link.get("type", "").startswith("image/"):
                return link.get("href")

    return None

def send_to_discord(title, link, source, summary, image_url):
    message = {
        "username": "CIPHER AI News",
        "embeds": [
            {
                "author": {
                    "name": "CIPHER's Network • AI NEWS"
                },
                "title": f"📰 {title[:250]}",
                "url": link,
                "description": summary[:1000],
                "fields": [
                    {
                        "name": "🏷️ Source",
                        "value": source,
                        "inline": True
                    },
                    {
                        "name": "🌐 Article",
                        "value": "[Read Full Article](" + link + ")",
                        "inline": True
                    }
                ],
                "thumbnail": {
                            "url": image_url
                } if image_url else None,
                "footer": {
                    "text": "CIPHER's Network • AI News"
                }
            }
        ]
    }

    response = requests.post(
        WEBHOOK_URL,
        json=message,
        timeout=15
    )

    response.raise_for_status()


def main():
    seen = load_seen()
    new_items = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:
            title = entry.get("title", "Untitled")
            link = entry.get("link")

            if not link:
                continue

            item_id = article_id(link)

            if item_id in seen:
                continue

            source = feed.feed.get("title", "News Source")

            summary = entry.get("summary", "").strip()
            image_url = get_image(entry)

if not summary:
    summary = "A new article has been published."

new_items.append((title, link, source, summary, image_url, item_id))

    for title, link, source, summary, image_url, item_id in new_items[:5]:
    send_to_discord(title, link, source, summary, image_url)
    seen.add(item_id)

    save_seen(seen)


if __name__ == "__main__":
    main()

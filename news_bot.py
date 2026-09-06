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


def send_to_discord(title, link, source):
    message = {
        "username": "CIPHER AI News",
        "embeds": [
            {
                "author": {
                    "name": "CIPHER's Network • AI NEWS"
                },
                "title": f"📰 {title[:250]}",
                "url": link,
                "description": (
                    f"**{source}** has published a new AI/technology story.\n\n"
                    "🔗 **Click the headline to read the full article.**"
                ),
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

            new_items.append((title, link, source, item_id))

    for title, link, source, item_id in new_items[:5]:
        send_to_discord(title, link, source)
        seen.add(item_id)

    save_seen(seen)


if __name__ == "__main__":
    main()

from urllib.parse import urlparse, parse_qs
from typing import Optional

def generar_embed(url: str) -> Optional[str]:
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""

        # YouTube
        if "youtube.com" in hostname:
            query = parse_qs(parsed_url.query)
            video_id = query.get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be" in hostname:
            video_id = parsed_url.path.strip("/")
            return f"https://www.youtube.com/embed/{video_id}"

        # Facebook
        elif "facebook.com" in hostname:
            return f"https://www.facebook.com/plugins/video.php?href={url}"

        # Instagram
        elif "instagram.com" in hostname:
            return f"{url.rstrip('/')}/embed"

        # Twitter (se maneja como blockquote)
        elif "twitter.com" in hostname:
            return url

        # TikTok
        elif "tiktok.com" in hostname:
            return url.replace("www.tiktok.com", "www.tiktok.com/embed")

        # Twitch
        elif "twitch.tv" in hostname:
            if "/videos/" in parsed_url.path:
                video_id = parsed_url.path.split("/videos/")[1]
                return f"https://player.twitch.tv/?video={video_id}&parent=localhost"
            else:
                channel = parsed_url.path.strip("/")
                return f"https://player.twitch.tv/?channel={channel}&parent=localhost"

        # Otros (retorna URL tal cual)
        return url
    except Exception as e:
        print(f"Error generando embed: {e}")
        return None
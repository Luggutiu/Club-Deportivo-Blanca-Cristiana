from urllib.parse import urlparse, parse_qs
from typing import Optional

def generar_embed(url: str) -> Optional[str]:
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname or ""
        path = parsed_url.path

        # --- YouTube
        if "youtube.com" in hostname:
            query = parse_qs(parsed_url.query)
            video_id = query.get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        elif "youtu.be" in hostname:
            video_id = path.strip("/")
            return f"https://www.youtube.com/embed/{video_id}"

        # --- Facebook
        elif "facebook.com" in hostname:
            return f"https://www.facebook.com/plugins/video.php?href={url}"

        # --- Instagram
        elif "instagram.com" in hostname:
            return f"{url.rstrip('/')}/embed"

        # --- TikTok
        elif "tiktok.com" in hostname:
            return url.replace("www.tiktok.com", "www.tiktok.com/embed")

        # --- Twitch
        elif "twitch.tv" in hostname:
            if "/videos/" in path:
                video_id = path.split("/videos/")[1]
                return f"https://player.twitch.tv/?video={video_id}&parent=localhost"
            else:
                channel = path.strip("/")
                return f"https://player.twitch.tv/?channel={channel}&parent=localhost"

        # --- Twitter (retorna el link para usar con <blockquote>)
        elif "twitter.com" in hostname:
            return url

        # --- Otro (se devuelve tal cual)
        return url

    except Exception as e:
        print(f"[Error en generar_embed] {e}")
        return None
from urllib.parse import urlparse
from typing import Tuple

def generar_embed(url: str) -> str:
    if "youtube.com" in url or "youtu.be" in url:
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]
        return f"https://www.youtube.com/embed/{video_id}"

    elif "facebook.com" in url:
        return url.replace("www.facebook.com", "www.facebook.com/plugins/video")

    elif "instagram.com" in url:
        return url + "embed"

    elif "twitter.com" in url:
        return url  # Twitter se muestra con blockquote, no embed directo

    elif "tiktok.com" in url:
        return url.replace("www.tiktok.com", "www.tiktok.com/embed")

    elif "twitch.tv" in url:
        if "/videos/" in url:
            video_id = url.split("/videos/")[1]
            return f"https://player.twitch.tv/?video={video_id}&parent=localhost"
        elif "twitch.tv/" in url:
            channel = url.split("twitch.tv/")[1]
            return f"https://player.twitch.tv/?channel={channel}&parent=localhost"

    return url  # Si no se reconoce, retorna el mismo URL
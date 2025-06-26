from urllib.parse import urlparse
from typing import Tuple

def generar_embed(url: str) -> Tuple[str, str]:
    if "youtube.com" in url or "youtu.be" in url:
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        iframe = f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>'
        return iframe, "YouTube"

    elif "facebook.com" in url:
        embed_url = url.replace("www.facebook.com", "www.facebook.com/plugins/video")
        iframe = f'<iframe src="{embed_url}" width="500" height="280" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowfullscreen></iframe>'
        return iframe, "Facebook"

    elif "instagram.com" in url:
        embed_url = url + "embed"
        iframe = f'<iframe src="{embed_url}" width="400" height="480" frameborder="0" scrolling="no" allowtransparency="true"></iframe>'
        return iframe, "Instagram"

    elif "twitter.com" in url:
        # Twitter embed is usually handled by a JS widget (not just iframe), so just return the URL
        return f'<blockquote class="twitter-tweet"><a href="{url}"></a></blockquote>', "Twitter"

    elif "tiktok.com" in url:
        embed_url = url.replace("www.tiktok.com", "www.tiktok.com/embed")
        iframe = f'<iframe src="{embed_url}" width="325" height="575" frameborder="0" allowfullscreen></iframe>'
        return iframe, "TikTok"

    elif "twitch.tv" in url:
        if "/videos/" in url:
            video_id = url.split("/videos/")[1]
            embed_url = f"https://player.twitch.tv/?video={video_id}&parent=localhost"
        elif "twitch.tv/" in url:
            channel = url.split("twitch.tv/")[1]
            embed_url = f"https://player.twitch.tv/?channel={channel}&parent=localhost"
        else:
            embed_url = url
        iframe = f'<iframe src="{embed_url}" width="560" height="315" frameborder="0" allowfullscreen></iframe>'
        return iframe, "Twitch"

    return f'<a href="{url}" target="_blank">{url}</a>', "Desconocido"
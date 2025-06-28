# app/utils.py

def detect_platform(url: str) -> str:
    url = url.lower()

    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "facebook.com" in url or "fb.watch" in url or "m.facebook.com" in url:
        return "facebook"
    elif "instagram.com" in url or "instagr.am" in url:
        return "instagram"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    elif "twitch.tv" in url:
        return "twitch"
    elif "tiktok.com" in url:
        return "tiktok"
    else:
        return "desconocido"
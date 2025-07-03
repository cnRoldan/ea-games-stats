import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "accept": "application/json",
    "Referer": "https://www.ea.com/",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?0"
}

def fetch_club_stats(club_id: int, platform: str = "common-gen5") -> dict:
    url = f"https://proclubs.ea.com/api/fc/members/stats?platform={platform}&clubId={club_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from instaloader import Instaloader, Post

VIDEO_DIR = "./videos"
SPOTIFY_CLIENT_ID = "81efd507265e49c293b2533732f91f3f"
SPOTIFY_CLIENT_SECRET = "55cc98d980b54b7c82e4b70b470aaeaf"
YOUTUBE_DL_OPTIONS = {
    "outtmpl": os.path.join(VIDEO_DIR, "%(title)s.%(ext)s"),
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "merge_output_format": "mp4",
    "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
}

if not os.path.exists(VIDEO_DIR):
    os.makedirs(VIDEO_DIR)

def Download(url: str, file_name: str):
    if "youtube.com" in url:
        with youtube_dl.YoutubeDL(params={
            'format': 'best',
            'outtmpl': os.path.join(VIDEO_DIR, f"{file_name}.%(ext)s")
        }) as ydl:
            ydl.download([url])
        return True
    elif "open.spotify.com" in url:
        #https://open.spotify.com/track/7o2CTH4ctstm8TNelqjb51?si=7454e5ae95c64f9a
        client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        result = sp.track(url)
        preview_url = result['preview_url']
        response = requests.get(preview_url, stream=True)
        with open(os.path.join(VIDEO_DIR, f"{file_name}.mp3"), "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
    elif "instagram.com" in url:
        L = Instaloader()
        video_id = url.split("/")[-2]
        post = Post.from_shortcode(L.context, video_id)
        video_url = post.video_url
        response = requests.get(video_url, stream=True)
        total_length = int(response.headers.get("content-length", 0))
        with open(os.path.join(VIDEO_DIR, f"{post.owner_username}_{post.date_utc}.mp4"), "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"\n[+] Video successfully downloaded to {VIDEO_DIR}/{file_name}.mp4\n")
        return True
    else:
        raise ValueError("Unsupported URL format")

def main():
    print("Welcome to the video downloader!\n")
    url = None
    while url is None:
        url = input("Please enter the URL of the video/song/reel/short you want to download: ")
        print(f"\n[+] Attempting to download file from {url}...\n")
        try:
            Download(url=url, file_name=url.split("/")[-1])
            print(f"\n[+] Video successfully downloaded to {VIDEO_DIR}\n")
        except Exception as e:
            print(f"\n[-] An error occurred while downloading the video: {str(e)}\n")
            url = None

main()
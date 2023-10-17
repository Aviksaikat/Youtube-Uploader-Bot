import datetime
import json
import os
import time
from random import randint

import google.auth
import toml
from google.oauth2.credentials import Credentials
from google_apis import create_service
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Load the configuration from the TOML file
config = toml.load("config.toml")

# Get the API key
API_KEY = config["youtube"]["api_key"]

# Get the channel ID
CHANNEL_ID = config["youtube"]["channel_id"]

# Get the client ID
CLIENT_SECRETS_FILE = open(config["youtube"]["client_secrets_file"], "r").read()

# Get the playlist ID
# PLAYLIST_ID = config["youtube"]["playlist_id"]

# Get the folder path
FOLDER_PATH = config["youtube"]["folder_path"]

# Replace with the title and description of the video
# VIDEO_TITLE = "My Video"
# VIDEO_DESCRIPTION = "This is my video"

# Get the list of scopes
SCOPES = ["https://www.googleapis.com/auth/youtube"]
API_NAME = "youtube"
API_VERSION = "v3"


def make_upload(video_title, file_path):
    # Load the client secrets file
    service = create_service("client_secrets.json", API_NAME, API_VERSION, SCOPES)

    # Create a request to upload the video
    print("Uploading the video....")

    upload_time = (
        datetime.datetime.now() + datetime.timedelta(days=10)
    ).isoformat() + ".000Z"
    request_body = {
        "snippet": {
            "title": video_title + " #shots #funny #funnyvideo",
            "description": "#shots #funny #funnyvideo shorts fun shorts minecraft voice female",
            "categoryId": "",
            "tags": ["shorts"],
        },
        "status": {
            "privacyStatus": "public",
            "publishedAt": upload_time,
            "selfDeclaredMadeForKids": False,
        },
        "notifySubscribers": True,
    }
    media_file = MediaFileUpload(file_path)
    response_video_upload = (
        service.videos()
        .insert(part="snippet, status", body=request_body, media_body=media_file)
        .execute()
    )
    uploaded_video_id = response_video_upload.get("id")

    print("Video Uploaded Wooohooo....")
    print(f"Video '{video_title}' was added")


class ChangeHandler(FileSystemEventHandler):
    def on_created(self, event):

        # Check if the event is a file creation
        if event.is_directory:
            return

        # Get the path of the new file
        file_path = event.src_path

        # Check if the file is a video file
        if not file_path.endswith(".mp4"):
            return

        # Get the video title from the file name
        video_title = os.path.basename(file_path).split(".")[0]
        # print(f"Got a new file:{file_path}")

        video_title = " ".join(video_title.split(" ")[: randint(4, 10)])
        print(video_title)

        # Upload the video to YouTube
        try:
            make_upload(video_title, file_path)

            time.sleep(120)
            print("Waiting....")

        except HttpError as error:
            print(f"An error occurred: {error}")


def main():
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_PATH, recursive=True)
    observer.start()
    print("Listening....")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    # test()
    main()

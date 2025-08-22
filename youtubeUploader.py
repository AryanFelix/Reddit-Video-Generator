import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials

class YouTubeUploader:
    def __init__(self, env_file: str, video_file: str):
        """
        Initialize the YouTubeUploader with .env file path and video file path.
        
        Args:
            env_file (str): Path to the .env file containing OAuth credentials.
            video_file (str): Path to the video file to upload.
        """
        self.env_file = env_file
        self.video_file = video_file
        self.youtube = None
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
        self.token_file = "token.json"  # File to store OAuth credentials
        
        # Load environment variables from .env file
        load_dotenv(self.env_file)
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI", "urn:ietf:wg:oauth:2.0:oob")

    def authenticate(self):
        """
        Authenticate with YouTube using OAuth 2.0 and build the YouTube API client.
        Reuses existing credentials if available, otherwise triggers authentication flow.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in the .env file.")

        creds = None
        # Load existing credentials if they exist
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
        
        # If no valid credentials or token expired, refresh or authenticate
        from google.auth.transport.requests import Request
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uris": [self.redirect_uri],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token"
                        }
                    },
                    scopes=self.scopes
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        self.youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    def upload_video(self, title: str, description: str = "", tags: list = None, category_id: str = "22", privacy_status: str = "private", playlist_title: str = None, playlist_id: str = None):
        """
        Upload a video to YouTube and optionally add it to a playlist.
        
        Args:
            title (str): The title of the video.
            description (str, optional): The description of the video. Defaults to "".
            tags (list, optional): List of tags for the video. Defaults to None.
            category_id (str, optional): The category ID (e.g., "22" for People & Blogs). Defaults to "22".
            privacy_status (str, optional): Privacy status ("public", "private", "unlisted"). Defaults to "private".
            playlist_title (str, optional): Title of a new playlist to create and add the video to. Defaults to None.
            playlist_id (str, optional): ID of an existing playlist to add the video to. Defaults to None.
        
        Returns:
            dict: The API response containing the video ID and other details.
        """
        if not self.youtube:
            raise ValueError("Authentication required. Call authenticate() first.")

        if not os.path.exists(self.video_file):
            raise FileNotFoundError(f"Video file not found: {self.video_file}")

        # Prepare the video body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags if tags else [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        # Create a media file upload object
        media = MediaFileUpload(self.video_file, chunksize=-1, resumable=True)

        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")
            print("Upload completed successfully!")
            video_id = response["id"]

            # Handle playlist addition
            if playlist_title or playlist_id:
                if not playlist_id:
                    # Create a new playlist
                    playlist_body = {
                        "snippet": {
                            "title": playlist_title or f"Playlist for {title}",
                            "description": f"Playlist created for {title}"
                        },
                        "status": {
                            "privacyStatus": privacy_status
                        }
                    }
                    playlist_response = self.youtube.playlists().insert(
                        part="snippet,status",
                        body=playlist_body
                    ).execute()
                    playlist_id = playlist_response["id"]
                    print(f"Created new playlist with ID: {playlist_id}")

                # Add video to playlist
                playlist_item_body = {
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
                playlist_item_response = self.youtube.playlistItems().insert(
                    part="snippet",
                    body=playlist_item_body
                ).execute()
                print(f"Added video to playlist {playlist_id}")

            return response
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error occurred: {e}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
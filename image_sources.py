import os
import requests
from unsplash.api import Api
from unsplash.auth import Auth
from pexels_api import API
import json
from typing import Optional, Dict, Any

class ImageSourceManager:
    def __init__(self):
        self.config = self.load_config()
        self.setup_apis()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "unsplash_api_key": "",
                "pexels_api_key": "",
                "default_source": "local",
                "interval": 10,
                "save_directory": "downloaded_wallpapers"
            }

    def setup_apis(self):
        """Initialize API clients"""
        # Setup Unsplash
        if self.config.get("unsplash_api_key"):
            auth = Auth(self.config["unsplash_api_key"])
            self.unsplash_api = Api(auth)
        else:
            self.unsplash_api = None

        # Setup Pexels
        if self.config.get("pexels_api_key"):
            self.pexels_api = API(self.config["pexels_api_key"])
        else:
            self.pexels_api = None

    def get_random_unsplash_image(self) -> Optional[str]:
        """Get a random image from Unsplash"""
        if not self.unsplash_api:
            raise ValueError("Unsplash API key not configured")

        try:
            # Get a random photo
            random_photo = self.unsplash_api.photo.random()
            if random_photo:
                # Download the image
                photo_url = random_photo[0].urls.full
                save_path = os.path.join(
                    self.config["save_directory"],
                    f"unsplash_{random_photo[0].id}.jpg"
                )
                
                # Create directory if it doesn't exist
                os.makedirs(self.config["save_directory"], exist_ok=True)
                
                # Download the image
                response = requests.get(photo_url)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return save_path
        except Exception as e:
            print(f"Error fetching Unsplash image: {e}")
            return None

    def get_random_pexels_image(self) -> Optional[str]:
        """Get a random image from Pexels"""
        if not self.pexels_api:
            raise ValueError("Pexels API key not configured")

        try:
            # Get a random photo (we'll use a random query from a list of nature-related terms)
            queries = ["nature", "landscape", "mountains", "ocean", "forest"]
            import random
            query = random.choice(queries)
            
            # Search for photos
            search_results = self.pexels_api.search(query, page=1, results_per_page=1)
            if search_results and search_results.photos:
                photo = search_results.photos[0]
                save_path = os.path.join(
                    self.config["save_directory"],
                    f"pexels_{photo.id}.jpg"
                )
                
                # Create directory if it doesn't exist
                os.makedirs(self.config["save_directory"], exist_ok=True)
                
                # Download the image
                response = requests.get(photo.original)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return save_path
        except Exception as e:
            print(f"Error fetching Pexels image: {e}")
            return None

    def update_api_key(self, service: str, api_key: str):
        """Update API key in config"""
        if service not in ["unsplash", "pexels"]:
            raise ValueError("Invalid service specified")
            
        self.config[f"{service}_api_key"] = api_key
        self.save_config()
        self.setup_apis()

    def save_config(self):
        """Save current configuration to config.json"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
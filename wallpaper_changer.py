import ctypes
import os
import random
import time
import requests

def download_wallpaper(url, save_path):
    """Download an image from the given URL and save it to the specified path."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Wallpaper downloaded: {save_path}")
    else:
        print("Failed to download wallpaper.")

def change_wallpaper(folder_path):
    """Change the desktop wallpaper to a random image from the specified folder."""
    if not os.path.exists(folder_path):
        print("Folder not found!")
        return

    wallpapers = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]

    if not wallpapers:
        print("No wallpapers found in the folder.")
        return

    random_wallpaper = random.choice(wallpapers)

    # Set the wallpaper (Windows only)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, random_wallpaper, 0)
    print(f"Wallpaper changed to: {random_wallpaper}")

def main():
    wallpaper_folder = os.path.abspath("Wallpapers")  # Get full path of the folder

    if not os.path.exists(wallpaper_folder):
        print(f"Wallpaper folder '{wallpaper_folder}' not found.")
        return

    try:
        while True:
            change_wallpaper(wallpaper_folder)
            time.sleep(10)  # Change wallpaper every 10 seconds
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()

import ctypes
import os
import random
import time

def change_wallpaper(Wallpapers):
    # Get a list of wallpaper files
    wallpapers = [os.path.join(Wallpapers, f) for f in os.listdir(Wallpapers) if f.endswith(('.jpg', '.png'))]
    
    if not wallpapers:
        print("No wallpapers found in the folder.")
        return

    # Select a random wallpaper
    random_wallpaper = random.choice(wallpapers)

    # Set the wallpaper (Windows only)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, random_wallpaper, 0)
    print(f"Wallpaper changed to: {random_wallpaper}")

def main():
    # Path to the folder containing wallpapers
    wallpaper_folder = "Wallpapers"

    # Change wallpaper every 10 seconds (for testing)
    while True:
        change_wallpaper(wallpaper_folder)
        time.sleep(10)

if __name__ == "__main__":
    main()
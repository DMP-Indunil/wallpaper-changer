import ctypes
import os
import random
import time
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class WallpaperChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Changer")
        self.root.geometry("400x200")

        self.wallpaper_folder = ""
        self.running = False

        # Folder selection
        self.folder_label = tk.Label(root, text="Select Wallpaper Folder:")
        self.folder_label.pack(pady=5)

        self.folder_button = tk.Button(root, text="Browse", command=self.select_folder)
        self.folder_button.pack(pady=5)

        # Interval selection
        self.interval_label = tk.Label(root, text="Change Interval (seconds):")
        self.interval_label.pack(pady=5)

        self.interval_entry = tk.Entry(root)
        self.interval_entry.insert(0, "10")  # Default interval
        self.interval_entry.pack(pady=5)

        # Start/Stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_changer, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_changer, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def select_folder(self):
        self.wallpaper_folder = filedialog.askdirectory()
        if self.wallpaper_folder:
            self.folder_label.config(text=f"Selected Folder: {self.wallpaper_folder}")
            self.start_button.config(state=tk.NORMAL)

    def start_changer(self):
        if not self.wallpaper_folder:
            messagebox.showerror("Error", "Please select a wallpaper folder first.")
            return

        try:
            self.interval = int(self.interval_entry.get())
            if self.interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive integer for the interval.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.change_wallpaper_loop()

    def stop_changer(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def change_wallpaper_loop(self):
        if self.running:
            change_wallpaper(self.wallpaper_folder)
            self.root.after(self.interval * 1000, self.change_wallpaper_loop)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperChangerApp(root)
    root.mainloop()
import ctypes
import os
import random
import time
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser, font
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from datetime import datetime
import threading
from colorthief import ColorThief
import io

class WallpaperChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Changer")
        self.root.geometry("500x300")

        self.wallpaper_folder = ""
        self.running = False
        self.wallpaper_source = "local"  # Default source

        # Source selection
        self.source_label = tk.Label(root, text="Select Wallpaper Source:")
        self.source_label.pack(pady=5)

        self.source_var = tk.StringVar(value="local")
        self.source_dropdown = ttk.Combobox(root, textvariable=self.source_var, values=["local", "online"])
        self.source_dropdown.pack(pady=5)
        self.source_dropdown.bind("<<ComboboxSelected>>", self.on_source_change)

        # Folder selection
        self.folder_label = tk.Label(root, text="Select Wallpaper Folder:")
        self.folder_label.pack(pady=5)

        self.folder_button = tk.Button(root, text="Browse", command=self.select_folder)
        self.folder_button.pack(pady=5)

        # URL entry
        self.url_label = tk.Label(root, text="Enter Wallpaper URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Interval selection
        self.interval_label = tk.Label(root, text="Change Interval (seconds):")
        self.interval_label.pack(pady=5)

        self.interval_entry = tk.Entry(root)
        self.interval_entry.insert(0, "10")  # Default interval
        self.interval_entry.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Status label
        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.pack(pady=5)

        # Start/Stop buttons
        self.start_button = tk.Button(root, text="Start", command=self.start_changer, state=tk.DISABLED)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_changer, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def on_source_change(self, event):
        self.wallpaper_source = self.source_var.get()
        if self.wallpaper_source == "local":
            self.folder_button.config(state=tk.NORMAL)
            self.url_entry.config(state=tk.DISABLED)
        else:
            self.folder_button.config(state=tk.DISABLED)
            self.url_entry.config(state=tk.NORMAL)

    def select_folder(self):
        self.wallpaper_folder = filedialog.askdirectory()
        if self.wallpaper_folder:
            self.folder_label.config(text=f"Selected Folder: {self.wallpaper_folder}")
            self.start_button.config(state=tk.NORMAL)

    def start_changer(self):
        if self.wallpaper_source == "local" and not self.wallpaper_folder:
            messagebox.showerror("Error", "Please select a wallpaper folder first.")
            return
        elif self.wallpaper_source == "online" and not self.url_entry.get():
            messagebox.showerror("Error", "Please enter a wallpaper URL.")
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
        self.status_label.config(text="Status: Running", fg="green")
        self.change_wallpaper_loop()

    def stop_changer(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped", fg="red")

    def change_wallpaper_loop(self):
        if self.running:
            if self.wallpaper_source == "local":
                change_wallpaper(self.wallpaper_folder)
            else:
                url = self.url_entry.get()
                save_path = os.path.join(os.getcwd(), "downloaded_wallpaper.jpg")
                download_wallpaper(url, save_path)
                change_wallpaper_from_file(save_path)

            self.progress["value"] = 0
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
    change_wallpaper_from_file(random_wallpaper)

def change_wallpaper_from_file(file_path):
    """Change the desktop wallpaper to the specified file."""
    ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 0)
    print(f"Wallpaper changed to: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WallpaperChangerApp(root)
    root.mainloop()
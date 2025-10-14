Upgrade
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
        
        # Initialize image source manager
        from image_sources import ImageSourceManager
        self.source_manager = ImageSourceManager()
        self.wallpaper_source = self.source_manager.config["default_source"]

        # Source selection
        self.source_label = tk.Label(root, text="Select Wallpaper Source:")
        self.source_label.pack(pady=5)

        self.source_var = tk.StringVar(value=self.wallpaper_source)
        self.source_dropdown = ttk.Combobox(root, textvariable=self.source_var, 
                                          values=["local", "online", "unsplash", "pexels"])
        self.source_dropdown.pack(pady=5)
        self.source_dropdown.bind("<<ComboboxSelected>>", self.on_source_change)

        # API Key configuration
        self.api_frame = ttk.LabelFrame(root, text="API Configuration")
        self.api_frame.pack(pady=5, padx=5, fill="x")

        # Unsplash API key
        self.unsplash_label = tk.Label(self.api_frame, text="Unsplash API Key:")
        self.unsplash_label.pack(pady=2)
        self.unsplash_key = tk.Entry(self.api_frame, width=40, show="*")
        self.unsplash_key.pack(pady=2)
        if self.source_manager.config["unsplash_api_key"]:
            self.unsplash_key.insert(0, self.source_manager.config["unsplash_api_key"])

        # Pexels API key
        self.pexels_label = tk.Label(self.api_frame, text="Pexels API Key:")
        self.pexels_label.pack(pady=2)
        self.pexels_key = tk.Entry(self.api_frame, width=40, show="*")
        self.pexels_key.pack(pady=2)
        if self.source_manager.config["pexels_api_key"]:
            self.pexels_key.insert(0, self.source_manager.config["pexels_api_key"])

        # Save API keys button
        self.save_api_button = tk.Button(self.api_frame, text="Save API Keys", command=self.save_api_keys)
        self.save_api_button.pack(pady=5)

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
=======
import ctypes import os import random import requests import tkinter as tk from tkinter import filedialog, messagebox, ttk from PIL import Image, ImageTk

class WallpaperChangerApp: def init(self, root): self.root = root self.root.title("Wallpaper Changer") self.root.geometry("550x400") self.root.resizable(False, False)

self.wallpaper_folder = ""
    self.running = False
    self.wallpaper_source = "local"
    
    # Header Label
    tk.Label(root, text="Wallpaper Changer", font=("Arial", 16, "bold")).pack(pady=10)
    
    # Source Selection
    frame_source = tk.Frame(root)
    frame_source.pack(pady=5)
    tk.Label(frame_source, text="Select Source:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    
    self.source_var = tk.StringVar(value="local")
    self.source_dropdown = ttk.Combobox(frame_source, textvariable=self.source_var, values=["local", "online"], state="readonly")
    self.source_dropdown.pack(side=tk.LEFT)
    self.source_dropdown.bind("<<ComboboxSelected>>", self.on_source_change)
    
    # Folder Selection
    self.folder_button = tk.Button(root, text="Select Folder", command=self.select_folder, width=20)
    self.folder_button.pack(pady=5)
    self.folder_label = tk.Label(root, text="No folder selected", fg="gray")
    self.folder_label.pack()
    
    # URL Entry
    self.url_entry = tk.Entry(root, width=50, state=tk.DISABLED)
    self.url_entry.pack(pady=5)
    
    # Interval Selection
    frame_interval = tk.Frame(root)
    frame_interval.pack(pady=5)
    tk.Label(frame_interval, text="Interval (seconds):", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    self.interval_entry = tk.Entry(frame_interval, width=5)
    self.interval_entry.insert(0, "10")
    self.interval_entry.pack(side=tk.LEFT)
    
    # Progress Bar
    self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    self.progress.pack(pady=10)
    
    # Status Label
    self.status_label = tk.Label(root, text="Status: Idle", fg="blue", font=("Arial", 12))
    self.status_label.pack()
    
    # Control Buttons
    self.start_button = tk.Button(root, text="Start", command=self.start_changer, state=tk.DISABLED, width=15, bg="green", fg="white")
    self.start_button.pack(pady=5)
    self.stop_button = tk.Button(root, text="Stop", command=self.stop_changer, state=tk.DISABLED, width=15, bg="red", fg="white")
    self.stop_button.pack()

def on_source_change(self, event):
    self.wallpaper_source = self.source_var.get()
    if self.wallpaper_source == "local":
        self.folder_button.config(state=tk.NORMAL)
        self.url_entry.config(state=tk.DISABLED)
    else:
        self.folder_button.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.NORMAL)
main

def select_folder(self):
    self.wallpaper_folder = filedialog.askdirectory()
    if self.wallpaper_folder:
        self.folder_label.config(text=f"Selected: {os.path.basename(self.wallpaper_folder)}", fg="black")
        self.start_button.config(state=tk.NORMAL)

Upgrade
    def on_source_change(self, event):
        self.wallpaper_source = self.source_var.get()
        
        # Disable all inputs first
        self.folder_button.config(state=tk.DISABLED)
        self.url_entry.config(state=tk.DISABLED)
        self.unsplash_key.config(state=tk.NORMAL)
        self.pexels_key.config(state=tk.NORMAL)
        
        # Enable relevant inputs based on source
        if self.wallpaper_source == "local":
            self.folder_button.config(state=tk.NORMAL)
        elif self.wallpaper_source == "online":
            self.url_entry.config(state=tk.NORMAL)
        elif self.wallpaper_source == "unsplash":
            if not self.source_manager.config["unsplash_api_key"]:
                messagebox.showwarning("API Key Required", "Please enter your Unsplash API key in the configuration section.")
        elif self.wallpaper_source == "pexels":
            if not self.source_manager.config["pexels_api_key"]:
                messagebox.showwarning("API Key Required", "Please enter your Pexels API key in the configuration section.")

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

    def save_api_keys(self):
        """Save API keys to config"""
        unsplash_key = self.unsplash_key.get().strip()
        pexels_key = self.pexels_key.get().strip()
        
        if unsplash_key:
            self.source_manager.update_api_key("unsplash", unsplash_key)
        if pexels_key:
            self.source_manager.update_api_key("pexels", pexels_key)
            
        messagebox.showinfo("Success", "API keys saved successfully!")

    def change_wallpaper_loop(self):
        if self.running:
            try:
                if self.wallpaper_source == "local":
                    change_wallpaper(self.wallpaper_folder)
                elif self.wallpaper_source == "online":
                    url = self.url_entry.get()
                    save_path = os.path.join(os.getcwd(), "downloaded_wallpaper.jpg")
                    download_wallpaper(url, save_path)
                    change_wallpaper_from_file(save_path)
                elif self.wallpaper_source == "unsplash":
                    wallpaper_path = self.source_manager.get_random_unsplash_image()
                    if wallpaper_path:
                        change_wallpaper_from_file(wallpaper_path)
                    else:
                        self.status_label.config(text="Status: Failed to fetch Unsplash image", fg="red")
                elif self.wallpaper_source == "pexels":
                    wallpaper_path = self.source_manager.get_random_pexels_image()
                    if wallpaper_path:
                        change_wallpaper_from_file(wallpaper_path)
                    else:
                        self.status_label.config(text="Status: Failed to fetch Pexels image", fg="red")
=======
def start_changer(self):
    if self.wallpaper_source == "local" and not self.wallpaper_folder:
        messagebox.showerror("Error", "Please select a wallpaper folder.")
        return
    elif self.wallpaper_source == "online" and not self.url_entry.get():
        messagebox.showerror("Error", "Please enter a wallpaper URL.")
        return
    
    try:
        self.interval = int(self.interval_entry.get())
        if self.interval <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Enter a valid positive integer for interval.")
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

def download_wallpaper(url, save_path): try: response = requests.get(url, timeout=10) response.raise_for_status() with open(save_path, 'wb') as file: file.write(response.content) print(f"Wallpaper downloaded: {save_path}") except requests.RequestException as e: print(f"Download failed: {e}")
main

def change_wallpaper(folder_path): if not os.path.exists(folder_path): print("Folder not found!") return

wallpapers = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
if not wallpapers:
    print("No wallpapers found in the folder.")
    return

change_wallpaper_from_file(random.choice(wallpapers))

def change_wallpaper_from_file(file_path): ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 0) print(f"Wallpaper changed to: {file_path}")

if name == "main": root = tk.Tk() app = WallpaperChangerApp(root) root.mainloop()


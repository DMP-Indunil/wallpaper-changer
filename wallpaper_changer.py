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
import sys

class WallpaperChangerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallpaper Changer with Scheduler")
        self.root.geometry("600x700")

        self.wallpaper_folder = ""
        self.running = False
        
        # Initialize image source manager
        from image_sources import ImageSourceManager
        self.source_manager = ImageSourceManager()
        self.wallpaper_source = self.source_manager.config["default_source"]
        
        # Initialize scheduler
        from scheduler import WallpaperScheduler
        self.scheduler = WallpaperScheduler()

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

        # Scheduling section
        self.schedule_frame = ttk.LabelFrame(root, text="Schedule Settings")
        self.schedule_frame.pack(pady=10, padx=5, fill="x")

        # Schedule mode selection
        self.schedule_mode_label = tk.Label(self.schedule_frame, text="Schedule Mode:")
        self.schedule_mode_label.pack(pady=2)
        
        self.schedule_mode_var = tk.StringVar(value=self.scheduler.config.get("schedule_mode", "manual"))
        self.schedule_mode_combo = ttk.Combobox(self.schedule_frame, textvariable=self.schedule_mode_var,
                                               values=["manual", "interval", "specific_times", "windows_task"],
                                               state="readonly")
        self.schedule_mode_combo.pack(pady=2)
        self.schedule_mode_combo.bind("<<ComboboxSelected>>", self.on_schedule_mode_change)

        # Interval scheduling options
        self.interval_frame = tk.Frame(self.schedule_frame)
        self.interval_frame.pack(pady=5, fill="x")
        
        tk.Label(self.interval_frame, text="Every:").grid(row=0, column=0, padx=2)
        self.interval_value_entry = tk.Entry(self.interval_frame, width=5)
        self.interval_value_entry.insert(0, str(self.scheduler.config.get("schedule_interval_value", 30)))
        self.interval_value_entry.grid(row=0, column=1, padx=2)
        
        self.interval_type_var = tk.StringVar(value=self.scheduler.config.get("schedule_interval_type", "minutes"))
        self.interval_type_combo = ttk.Combobox(self.interval_frame, textvariable=self.interval_type_var,
                                               values=["minutes", "hours", "days"], width=10, state="readonly")
        self.interval_type_combo.grid(row=0, column=2, padx=2)

        # Specific times scheduling
        self.times_frame = tk.Frame(self.schedule_frame)
        self.times_frame.pack(pady=5, fill="x")
        
        tk.Label(self.times_frame, text="Times (HH:MM, comma-separated):").pack()
        self.times_entry = tk.Entry(self.times_frame, width=40)
        default_times = ", ".join(self.scheduler.config.get("schedule_times", ["09:00", "12:00", "17:00"]))
        self.times_entry.insert(0, default_times)
        self.times_entry.pack(pady=2)

        # Windows Task Scheduler options
        self.windows_task_frame = tk.Frame(self.schedule_frame)
        self.windows_task_frame.pack(pady=5, fill="x")
        
        self.startup_var = tk.BooleanVar(value=self.scheduler.config.get("run_on_startup", False))
        self.startup_check = tk.Checkbutton(self.windows_task_frame, text="Run on Windows startup",
                                           variable=self.startup_var)
        self.startup_check.pack()
        
        self.create_task_button = tk.Button(self.windows_task_frame, text="Create Windows Task",
                                           command=self.create_windows_task)
        self.create_task_button.pack(pady=2)
        
        self.remove_task_button = tk.Button(self.windows_task_frame, text="Remove Windows Task",
                                           command=self.remove_windows_task)
        self.remove_task_button.pack(pady=2)

        # Update visibility based on initial mode
        self.on_schedule_mode_change(None)

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

        schedule_mode = self.schedule_mode_var.get()
        
        if schedule_mode == "manual":
            # Original behavior - simple interval
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
            self.status_label.config(text="Status: Running (Manual Mode)", fg="green")
            self.change_wallpaper_loop()
            
        elif schedule_mode == "interval":
            # Use scheduler for interval-based changes
            try:
                interval_value = int(self.interval_value_entry.get())
                interval_type = self.interval_type_var.get()
                
                if interval_value <= 0:
                    raise ValueError
                    
                self.scheduler.schedule_interval(interval_type, interval_value, self.do_wallpaper_change)
                
                self.running = True
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Status: Running (Every {interval_value} {interval_type})", fg="green")
                
                # Save config
                self.scheduler.config["schedule_mode"] = "interval"
                self.scheduler.config["schedule_interval_type"] = interval_type
                self.scheduler.config["schedule_interval_value"] = interval_value
                self.scheduler.save_config()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive integer for the interval.")
                return
                
        elif schedule_mode == "specific_times":
            # Use scheduler for specific times
            try:
                times_str = self.times_entry.get()
                times = [t.strip() for t in times_str.split(",")]
                
                # Validate time format
                for t in times:
                    datetime.strptime(t, "%H:%M")
                
                self.scheduler.schedule_at_times(times, self.do_wallpaper_change)
                
                self.running = True
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.status_label.config(text=f"Status: Scheduled at {', '.join(times)}", fg="green")
                
                # Save config
                self.scheduler.config["schedule_mode"] = "specific_times"
                self.scheduler.config["schedule_times"] = times
                self.scheduler.save_config()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid time format. Use HH:MM (24-hour format).\n{str(e)}")
                return
                
        elif schedule_mode == "windows_task":
            messagebox.showinfo("Info", "Please use the 'Create Windows Task' button to set up Windows Task Scheduler.")
            return

    def stop_changer(self):
        self.running = False
        self.scheduler.stop_schedule()
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

    def on_schedule_mode_change(self, event):
        """Handle schedule mode changes and show/hide relevant options."""
        mode = self.schedule_mode_var.get()
        
        # Hide all frames first
        self.interval_frame.pack_forget()
        self.times_frame.pack_forget()
        self.windows_task_frame.pack_forget()
        
        # Show relevant frame based on mode
        if mode == "interval":
            self.interval_frame.pack(pady=5, fill="x")
        elif mode == "specific_times":
            self.times_frame.pack(pady=5, fill="x")
        elif mode == "windows_task":
            self.windows_task_frame.pack(pady=5, fill="x")
    
    def create_windows_task(self):
        """Create a Windows Task Scheduler task."""
        try:
            interval_value = int(self.interval_value_entry.get())
            
            if self.startup_var.get():
                success, message = self.scheduler.setup_startup_task()
                if success:
                    messagebox.showinfo("Success", "Startup task created successfully!")
                else:
                    messagebox.showerror("Error", f"Failed to create startup task: {message}")
            else:
                success, message = self.scheduler.setup_windows_task(interval_value)
                if success:
                    messagebox.showinfo("Success", f"Windows task created to run every {interval_value} minutes!")
                else:
                    messagebox.showerror("Error", f"Failed to create task: {message}")
                    
            # Save config
            self.scheduler.config["run_on_startup"] = self.startup_var.get()
            self.scheduler.config["use_windows_scheduler"] = True
            self.scheduler.save_config()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid interval value.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def remove_windows_task(self):
        """Remove Windows Task Scheduler tasks."""
        try:
            # Remove both possible tasks
            success1, msg1 = self.scheduler.remove_windows_task("WallpaperChanger")
            success2, msg2 = self.scheduler.remove_windows_task("WallpaperChangerStartup")
            
            if success1 or success2:
                messagebox.showinfo("Success", "Windows tasks removed successfully!")
            else:
                messagebox.showwarning("Warning", "No tasks found to remove.")
                
            self.scheduler.config["use_windows_scheduler"] = False
            self.scheduler.save_config()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def do_wallpaper_change(self):
        """Perform a single wallpaper change based on current source."""
        try:
            if self.wallpaper_source == "local":
                if self.wallpaper_folder:
                    change_wallpaper(self.wallpaper_folder)
                else:
                    print("No wallpaper folder selected")
            elif self.wallpaper_source == "online":
                url = self.url_entry.get()
                if url:
                    save_path = os.path.join(os.getcwd(), "downloaded_wallpaper.jpg")
                    download_wallpaper(url, save_path)
                    change_wallpaper_from_file(save_path)
            elif self.wallpaper_source == "unsplash":
                wallpaper_path = self.source_manager.get_random_unsplash_image()
                if wallpaper_path:
                    change_wallpaper_from_file(wallpaper_path)
            elif self.wallpaper_source == "pexels":
                wallpaper_path = self.source_manager.get_random_pexels_image()
                if wallpaper_path:
                    change_wallpaper_from_file(wallpaper_path)
        except Exception as e:
            print(f"Error changing wallpaper: {e}")

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
            except Exception as e:
                print(f"Error in wallpaper loop: {e}")

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
    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--change-once":
        # Run once without GUI (for scheduled tasks)
        from image_sources import ImageSourceManager
        source_manager = ImageSourceManager()
        
        default_source = source_manager.config.get("default_source", "local")
        
        if default_source == "local":
            # Try to get folder from config or use default
            folder = source_manager.config.get("wallpaper_folder", "")
            if folder and os.path.exists(folder):
                change_wallpaper(folder)
        elif default_source == "unsplash":
            wallpaper_path = source_manager.get_random_unsplash_image()
            if wallpaper_path:
                change_wallpaper_from_file(wallpaper_path)
        elif default_source == "pexels":
            wallpaper_path = source_manager.get_random_pexels_image()
            if wallpaper_path:
                change_wallpaper_from_file(wallpaper_path)
    else:
        # Normal GUI mode
        root = tk.Tk()
        app = WallpaperChangerApp(root)
        root.mainloop()
import os
import json
import subprocess
import platform
from datetime import datetime, time
from typing import Optional, List
import schedule
import threading

class WallpaperScheduler:
    """Manages scheduled wallpaper changes using various methods."""
    
    def __init__(self):
        self.config = self.load_config()
        self.schedule_thread = None
        self.running = False
        
    def load_config(self) -> dict:
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_config(self):
        """Save current configuration to config.json"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def setup_windows_task(self, interval_minutes: int, task_name: str = "WallpaperChanger"):
        """Create a Windows Task Scheduler task for wallpaper changes."""
        if platform.system() != "Windows":
            raise OSError("Windows Task Scheduler is only available on Windows")
        
        # Get the path to the current Python executable and script
        python_exe = os.sys.executable
        script_path = os.path.abspath("wallpaper_changer.py")
        
        # Delete existing task if it exists
        subprocess.run(
            f'schtasks /Delete /TN "{task_name}" /F',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Create new task
        cmd = f'schtasks /Create /TN "{task_name}" /TR "\\\"{python_exe}\\\" \\\"{script_path}\\\" --change-once" /SC MINUTE /MO {interval_minutes} /F'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Task created successfully"
        else:
            return False, result.stderr
    
    def setup_startup_task(self, task_name: str = "WallpaperChangerStartup"):
        """Create a task that runs on user login."""
        if platform.system() != "Windows":
            raise OSError("Windows Task Scheduler is only available on Windows")
        
        python_exe = os.sys.executable
        script_path = os.path.abspath("wallpaper_changer.py")
        
        # Delete existing task if it exists
        subprocess.run(
            f'schtasks /Delete /TN "{task_name}" /F',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Create startup task
        cmd = f'schtasks /Create /TN "{task_name}" /TR "\\\"{python_exe}\\\" \\\"{script_path}\\\" --change-once" /SC ONLOGON /F'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, "Startup task created successfully"
        else:
            return False, result.stderr
    
    def remove_windows_task(self, task_name: str = "WallpaperChanger"):
        """Remove a Windows Task Scheduler task."""
        if platform.system() != "Windows":
            raise OSError("Windows Task Scheduler is only available on Windows")
        
        result = subprocess.run(
            f'schtasks /Delete /TN "{task_name}" /F',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, "Task removed successfully"
        else:
            return False, result.stderr
    
    def schedule_at_times(self, times: List[str], change_callback):
        """Schedule wallpaper changes at specific times each day.
        
        Args:
            times: List of time strings in HH:MM format (24-hour)
            change_callback: Function to call when changing wallpaper
        """
        schedule.clear()
        
        for time_str in times:
            schedule.every().day.at(time_str).do(change_callback)
        
        self.start_schedule_thread(change_callback)
    
    def schedule_interval(self, interval_type: str, interval_value: int, change_callback):
        """Schedule wallpaper changes at regular intervals.
        
        Args:
            interval_type: 'minutes', 'hours', or 'days'
            interval_value: Number of units
            change_callback: Function to call when changing wallpaper
        """
        schedule.clear()
        
        if interval_type == "minutes":
            schedule.every(interval_value).minutes.do(change_callback)
        elif interval_type == "hours":
            schedule.every(interval_value).hours.do(change_callback)
        elif interval_type == "days":
            schedule.every(interval_value).days.do(change_callback)
        else:
            raise ValueError(f"Invalid interval type: {interval_type}")
        
        self.start_schedule_thread(change_callback)
    
    def start_schedule_thread(self, change_callback):
        """Start the background thread for running scheduled tasks."""
        if self.schedule_thread and self.schedule_thread.is_alive():
            return
        
        self.running = True
        
        def run_scheduler():
            # Run once immediately
            change_callback()
            
            # Then run on schedule
            while self.running:
                schedule.run_pending()
                threading.Event().wait(1)  # Sleep for 1 second
        
        self.schedule_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.schedule_thread.start()
    
    def stop_schedule(self):
        """Stop the scheduling thread."""
        self.running = False
        schedule.clear()
        if self.schedule_thread:
            self.schedule_thread = None
    
    def get_schedule_info(self) -> dict:
        """Get information about current schedule."""
        jobs = schedule.get_jobs()
        return {
            "active": self.running,
            "job_count": len(jobs),
            "jobs": [str(job) for job in jobs]
        }

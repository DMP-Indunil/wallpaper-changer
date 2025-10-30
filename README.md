# Professional Wallpaper Creator & Changer

A Python-based desktop wallpaper creation and automation tool with a clean, intuitive interface for designing custom wallpapers and scheduling automatic changes.

## ✨ Features

### Wallpaper Creator
- **Professional GUI**: Modern, easy-to-use interface
- **Online Images**: High-quality images from Picsum Photos and other sources  
- **Image Filters**: Brightness, contrast, saturation, and blur controls
- **Text Overlay**: Add custom text with fonts and colors
- **Multi-format Export**: Save as PNG, JPEG, BMP
- **Instant Wallpaper Setting**: Set created wallpaper as desktop background

### Wallpaper Changer (NEW!)
- **Multiple Image Sources**: Local folders, direct URLs, Unsplash API, Pexels API
- **Smart Scheduling**: 4 flexible scheduling modes
  - **Manual Mode**: Traditional interval-based changes (seconds)
  - **Interval Mode**: Change every X minutes/hours/days
  - **Specific Times**: Schedule at exact times (e.g., 9:00 AM, 12:00 PM, 5:00 PM)
  - **Windows Task Scheduler**: System-level scheduled tasks with startup support
- **API Integration**: Fetch high-quality wallpapers from Unsplash and Pexels
- **Secure Configuration**: API keys stored locally in config.json
- **Background Operation**: Continue running in the background

## 🚀 Quick Start

### Wallpaper Creator

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the creator:**
   ```bash
   python professional_wallpaper_creator.py
   ```

3. **Create your first wallpaper:**
   - Click "Get Online Image" for a random image
   - Add text, apply filters, and customize
   - Click "Set as Wallpaper" to apply

### Wallpaper Changer with Scheduler

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the changer:**
   ```bash
   python wallpaper_changer.py
   ```

3. **Configure your source:**
   - **Local**: Select a folder with images
   - **Online**: Enter a direct image URL
   - **Unsplash/Pexels**: Enter your API key and save
     - Get Unsplash API key: https://unsplash.com/developers
     - Get Pexels API key: https://www.pexels.com/api/

4. **Choose your schedule mode:**
   - **Manual**: Simple interval in seconds (classic mode)
   - **Interval**: Every X minutes/hours/days (e.g., "Every 30 minutes")
   - **Specific Times**: At exact times (e.g., "09:00, 12:00, 17:00")
   - **Windows Task**: Create system task for reliability and startup support

5. **Start the changer:**
   - Click "Start" to begin automatic changes
   - The app will change your wallpaper according to your schedule

## 📋 Requirements

- Python 3.8+
- PIL (Pillow) - Image processing
- NumPy - Numerical operations  
- Requests - Online image fetching
- Tkinter - GUI framework (included with Python)
- schedule - Task scheduling
- python-unsplash - Unsplash API integration
- python-pexels - Pexels API integration

## 🗂️ Project Structure

```
wallpaper-changer/
├── professional_wallpaper_creator.py  # Professional wallpaper creator
├── wallpaper_changer.py               # Automated wallpaper changer with scheduler
├── image_sources.py                   # Image source manager (Unsplash, Pexels)
├── scheduler.py                       # Scheduling engine
├── config.json                        # Configuration file (API keys, preferences)
├── requirements.txt                   # Dependencies
└── README.md                          # Documentation
```

## 🔧 Configuration

The `config.json` file stores your settings:

```json
{
    "unsplash_api_key": "your_unsplash_key",
    "pexels_api_key": "your_pexels_key",
    "default_source": "local",
    "schedule_mode": "interval",
    "schedule_interval_type": "minutes",
    "schedule_interval_value": 30,
    "schedule_times": ["09:00", "12:00", "17:00"],
    "run_on_startup": false,
    "save_directory": "downloaded_wallpapers"
}
```

## 🕐 Scheduling Modes Explained

### 1. Manual Mode
- Classic behavior: change wallpaper every X seconds
- Simple and straightforward
- Good for testing or quick sessions

### 2. Interval Mode  
- More flexible time units (minutes, hours, days)
- Example: "Every 30 minutes" or "Every 2 hours"
- App stays running in the background

### 3. Specific Times
- Set exact times for wallpaper changes
- Example: "09:00, 12:00, 17:00" (24-hour format)
- Perfect for matching your daily routine

### 4. Windows Task Scheduler
- Creates system-level scheduled tasks
- Most reliable option - works even when app is closed
- Optional: Run on Windows startup
- Requires Windows OS

## 🌐 Image Sources

### Built-in Sources
- **Local Folder**: Use your own image collection
- **Direct URL**: Download from any image URL
- **Unsplash**: 3M+ high-quality photos (API key required)
- **Pexels**: Professional stock photos (API key required)

### Fallback Handling
- The creator application fetches from Picsum Photos with automatic fallbacks
- The changer caches downloaded images in `downloaded_wallpapers/` folder
- Error handling ensures reliability

## 🔄 Command-Line Usage

The wallpaper changer supports command-line execution for scheduled tasks:

```bash
# Change wallpaper once and exit (used by Windows Task Scheduler)
python wallpaper_changer.py --change-once
```

This is automatically configured when you create a Windows Task.

## ❓ Troubleshooting

### Windows Task Scheduler
- Run the app as Administrator if task creation fails
- Check Task Scheduler (taskschd.msc) to verify tasks
- Tasks appear as "WallpaperChanger" and "WallpaperChangerStartup"

### API Keys
- Both Unsplash and Pexels offer free API tiers
- Keys are stored locally in `config.json`
- Never commit `config.json` with API keys to version control

### Scheduling
- "Manual" and "Interval/Specific Times" modes require the app to stay running
- "Windows Task" mode works independently of the app

## 📄 License

This project is licensed under the MIT License.

---

**Create professional wallpapers and enjoy automatic changes with smart scheduling!**

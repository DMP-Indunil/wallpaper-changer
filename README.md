# Professional Wallpaper Creator

A Python-based desktop wallpaper creation tool with a clean, intuitive interface for designing and customizing professional-quality wallpapers.

## ✨ Features

- **Professional GUI**: Modern, easy-to-use interface
- **Online Images**: High-quality images from Picsum Photos and other sources  
- **Image Filters**: Brightness, contrast, saturation, and blur controls
- **Text Overlay**: Add custom text with fonts and colors
- **Multi-format Export**: Save as PNG, JPEG, BMP
- **Instant Wallpaper Setting**: Set created wallpaper as desktop background
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python professional_wallpaper_creator.py
   ```

3. **Create your first wallpaper:**
   - Click "Get Online Image" for a random image
   - Add text, apply filters, and customize
   - Click "Set as Wallpaper" to apply

## 📋 Requirements

- Python 3.8+
- PIL (Pillow) - Image processing
- NumPy - Numerical operations  
- Requests - Online image fetching
- Tkinter - GUI framework (included with Python)

## 🗂️ Project Structure

```
wallpaper-changer/
├── professional_wallpaper_creator.py  # Main application
├── wallpaper_changer.py               # Original simple version
├── requirements.txt                   # Dependencies
└── README.md                          # Documentation
```

## 🌐 Online Images

The application fetches high-quality images from reliable sources with automatic fallbacks:
- **Picsum Photos**: Random professional photography
- **Placeholder services**: Generated backgrounds when needed
- **Fallback generation**: Creates gradient wallpapers if online sources are unavailable

## 🔄 Legacy Version

The original simple wallpaper changer is preserved in `wallpaper_changer.py` for users who prefer basic functionality.

## 📄 License

This project is licensed under the MIT License.

---

**Create professional wallpapers with ease!**

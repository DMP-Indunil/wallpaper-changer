"""
Professional Wallpaper Creator - Fixed Unsplash Version
Clean implementation with working image download functionality
"""

import ctypes
import os
import random
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from io import BytesIO
import json
import threading
from datetime import datetime
import math

class ProfessionalWallpaperCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional Wallpaper Creator - Fixed")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Initialize variables
        self.current_image = None
        self.original_image = None
        self.canvas_image = None
        self.preview_image = None
        self.text_color = "#ffffff"
        self.font_size = 60
        
        # Filter settings
        self.filter_settings = {
            'brightness': 1.0,
            'contrast': 1.0,
            'saturation': 1.0,
            'blur': 0
        }
        
        # New features - History for undo/redo
        self.history = []
        self.history_index = -1
        self.max_history = 20
        
        # Batch processing
        self.batch_queue = []
        self.is_batch_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main user interface"""
        self.setup_menu()
        self.setup_toolbar()
        self.setup_main_layout()
        
    def setup_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Image", command=self.open_image)
        file_menu.add_command(label="Save Wallpaper", command=self.save_wallpaper)
        file_menu.add_separator()
        file_menu.add_command(label="Batch Process...", command=self.open_batch_processor)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Auto Enhance", command=self.auto_enhance_image)
        edit_menu.add_command(label="Extract Colors", command=self.extract_color_palette)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Pattern Generator", command=self.open_pattern_generator)
        tools_menu.add_command(label="Resize & Crop", command=self.open_resize_crop_dialog)
        tools_menu.add_command(label="Template Manager", command=self.open_template_manager)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        
    def setup_toolbar(self):
        """Create toolbar with quick actions"""
        toolbar = tk.Frame(self.root, bg='#34495e', height=50)
        toolbar.pack(fill=tk.X, pady=2)
        
        btn_style = {'bg': '#3498db', 'fg': 'white', 'font': ('Arial', 10, 'bold'), 'padx': 10}
        
        tk.Button(toolbar, text="📁 Open", command=self.open_image, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="💾 Save", command=self.save_wallpaper, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="🌐 Get Image", command=self.get_unsplash_image, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="📝 Add Text", command=self.add_text_layer, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="✨ Auto Enhance", command=self.auto_enhance_image, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="🎨 Patterns", command=self.open_pattern_generator, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="↶ Undo", command=self.undo, **btn_style).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(toolbar, text="🖥️ Set Wallpaper", command=self.set_as_wallpaper, **btn_style).pack(side=tk.RIGHT, padx=5, pady=5)
        
    def setup_main_layout(self):
        """Setup main layout with panels"""
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Tools
        self.left_panel = tk.Frame(main_frame, bg='#34495e', width=300)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.left_panel.pack_propagate(False)
        
        # Center panel - Canvas
        self.center_panel = tk.Frame(main_frame, bg='#2c3e50')
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Right panel - Preview
        self.right_panel = tk.Frame(main_frame, bg='#34495e', width=250)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        self.right_panel.pack_propagate(False)
        
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()
        
    def setup_left_panel(self):
        """Setup left panel with tools"""
        title = tk.Label(self.left_panel, text="Tools & Options", 
                        bg='#34495e', fg='white', font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Quick Create Section
        quick_frame = tk.LabelFrame(self.left_panel, text="Quick Create", 
                                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        quick_frame.pack(fill=tk.X, padx=10, pady=5)
        
        resolutions = ["1920x1080", "2560x1440", "3840x2160", "1366x768"]
        tk.Label(quick_frame, text="Resolution:", bg='#34495e', fg='white').pack(anchor=tk.W)
        self.resolution_var = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(quick_frame, textvariable=self.resolution_var, values=resolutions)
        resolution_combo.pack(fill=tk.X, pady=2)
        
        tk.Button(quick_frame, text="Create Blank Canvas", 
                 command=self.create_blank_canvas, bg='#e74c3c', fg='white').pack(fill=tk.X, pady=5)
        
        # Online Sources
        online_frame = tk.LabelFrame(self.left_panel, text="Online Sources", 
                                   bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        online_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(online_frame, text="Search keyword:", bg='#34495e', fg='white').pack(anchor=tk.W)
        self.search_entry = tk.Entry(online_frame)
        self.search_entry.pack(fill=tk.X, pady=2)
        self.search_entry.insert(0, "wallpaper")
        
        tk.Button(online_frame, text="🔥 Get Random Image (FIXED)", 
                 command=self.get_unsplash_image, bg='#27ae60', fg='white').pack(fill=tk.X, pady=2)
        
        # Text Tools
        text_frame = tk.LabelFrame(self.left_panel, text="Text Tools", 
                                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.text_entry = tk.Entry(text_frame)
        self.text_entry.pack(fill=tk.X, pady=2)
        self.text_entry.insert(0, "Your Text Here")
        
        tk.Button(text_frame, text="Add Text", 
                 command=self.add_text_layer, bg='#9b59b6', fg='white').pack(fill=tk.X, pady=2)
        tk.Button(text_frame, text="Text Color", 
                 command=self.choose_text_color, bg='#2980b9', fg='white').pack(fill=tk.X, pady=2)
        
    def setup_center_panel(self):
        """Setup center panel with canvas"""
        canvas_title = tk.Label(self.center_panel, text="Canvas", 
                              bg='#2c3e50', fg='white', font=('Arial', 16, 'bold'))
        canvas_title.pack(pady=5)
        
        canvas_frame = tk.Frame(self.center_panel, bg='#2c3e50')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
    def setup_right_panel(self):
        """Setup right panel with preview"""
        preview_frame = tk.LabelFrame(self.right_panel, text="Preview", 
                                    bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        preview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.preview_canvas = tk.Canvas(preview_frame, width=200, height=150, bg='white')
        self.preview_canvas.pack(pady=5)
        
        # Status
        status_frame = tk.LabelFrame(self.right_panel, text="Status", 
                                   bg='#34495e', fg='white', font=('Arial', 12, 'bold'))
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg='#34495e', fg='#27ae60', 
                                   font=('Arial', 10, 'bold'))
        self.status_label.pack(pady=5)
        
    def new_project(self):
        """Start a new project"""
        self.current_image = None
        self.original_image = None
        self.canvas.delete("all")
        self.preview_canvas.delete("all")
        self.status_label.config(text="New project started", fg='#27ae60')
        
    def open_image(self):
        """Open an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                image = Image.open(file_path)
                self.original_image = image.copy()
                self.current_image = image.copy()
                self.save_to_history()  # Save to history for undo/redo
                self.display_image_on_canvas()
                self.update_preview()
                self.status_label.config(text="Image loaded successfully", fg='#27ae60')
                messagebox.showinfo("Success", "Image loaded successfully!")
            except Exception as e:
                self.status_label.config(text="Failed to load image", fg='#e74c3c')
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
                
    def display_image_on_canvas(self):
        """Display current image on canvas"""
        if self.current_image:
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
                
            display_image = self.current_image.copy()
            display_image.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
            
            self.canvas_image = ImageTk.PhotoImage(display_image)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.canvas_image)
            
    def update_preview(self):
        """Update preview panel"""
        if self.current_image:
            preview_image = self.current_image.copy()
            preview_image.thumbnail((190, 140), Image.Resampling.LANCZOS)
            
            self.preview_image = ImageTk.PhotoImage(preview_image)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(100, 75, image=self.preview_image)
            
    def create_blank_canvas(self):
        """Create a blank canvas with specified resolution"""
        try:
            resolution = self.resolution_var.get()
            width, height = map(int, resolution.split('x'))
            
            blank_image = Image.new('RGB', (width, height), 'white')
            self.original_image = blank_image.copy()
            self.current_image = blank_image.copy()
            
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text=f"Created {resolution} canvas", fg='#27ae60')
            messagebox.showinfo("Success", f"Created blank {resolution} canvas!")
            
        except Exception as e:
            self.status_label.config(text="Failed to create canvas", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to create canvas: {str(e)}")
            
    def get_unsplash_image(self):
        """Get a random image from working sources - FIXED VERSION"""
        try:
            keyword = self.search_entry.get() or "wallpaper"
            resolution = self.resolution_var.get() or "1920x1080"
            width, height = map(int, resolution.split('x'))
            
            self.status_label.config(text="Downloading image...", fg='#f39c12')
            self.root.update()
            
            # Try Picsum first (most reliable)
            sources = [
                {
                    "name": "Picsum Photos",
                    "url": f"https://picsum.photos/{width}/{height}",
                    "description": "High-quality random photos"
                },
                {
                    "name": "Placeholder.com",
                    "url": f"https://via.placeholder.com/{width}x{height}/667eea/ffffff?text={keyword.replace(' ', '+')}", 
                    "description": "Custom placeholder with text"
                }
            ]
            
            success = False
            
            for source in sources:
                try:
                    print(f"🔄 Trying {source['name']}: {source['url']}")
                    self.status_label.config(text=f"Trying {source['name']}...", fg='#f39c12')
                    self.root.update()
                    
                    response = requests.get(source['url'], timeout=15, 
                                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                    
                    if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                        image = Image.open(BytesIO(response.content))
                        
                        # Verify it's a valid image
                        if image.size[0] > 100 and image.size[1] > 100:
                            self.original_image = image.copy()
                            self.current_image = image.copy()
                            
                            self.display_image_on_canvas()
                            self.update_preview()
                            self.status_label.config(text=f"Downloaded from {source['name']}", fg='#27ae60')
                            messagebox.showinfo("Success", f"✅ Downloaded image from {source['name']}!\n\nKeyword: '{keyword}'\nResolution: {image.size}\nSource: {source['description']}")
                            success = True
                            break
                        
                except Exception as e:
                    print(f"❌ Failed {source['name']}: {e}")
                    continue
            
            if not success:
                # Create a custom gradient as fallback
                self.create_keyword_wallpaper(keyword, width, height)
                
        except Exception as e:
            self.status_label.config(text="Image download failed", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to get image: {str(e)}")
            
    def create_keyword_wallpaper(self, keyword, width, height):
        """Create a custom wallpaper based on keyword when online sources fail"""
        try:
            self.status_label.config(text="Creating custom wallpaper...", fg='#f39c12')
            self.root.update()
            
            # Create gradient background
            image = Image.new('RGB', (width, height), '#667eea')
            draw = ImageDraw.Draw(image)
            
            # Create gradient effect
            for y in range(height):
                ratio = y / height
                r = int(102 * (1 - ratio) + 118 * ratio)  # 667eea to 764ba2
                g = int(126 * (1 - ratio) + 75 * ratio)
                b = int(234 * (1 - ratio) + 162 * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # Add the keyword as text
            font_size = min(width, height) // 20
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), keyword.upper(), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text with outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x + adj, y + adj2), keyword.upper(), font=font, fill="white")
            draw.text((x, y), keyword.upper(), font=font, fill="black")
            
            self.original_image = image.copy()
            self.current_image = image.copy()
            
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text="Custom wallpaper created", fg='#27ae60')
            messagebox.showinfo("Success", f"🎨 Created custom '{keyword}' wallpaper!\n\n(Online sources unavailable, using fallback)")
            
        except Exception as e:
            self.status_label.config(text="Fallback creation failed", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to create fallback wallpaper: {str(e)}")
            
    def add_text_layer(self):
        """Add text layer to the image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        text = self.text_entry.get()
        if not text:
            messagebox.showwarning("Warning", "Please enter text")
            return
            
        try:
            draw = ImageDraw.Draw(self.current_image)
            
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.current_image.width - text_width) // 2
            y = (self.current_image.height - text_height) // 2
            
            # Draw text with outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x + adj, y + adj2), text, font=font, fill="black")
            draw.text((x, y), text, font=font, fill=self.text_color)
            
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text="Text added successfully", fg='#27ae60')
            messagebox.showinfo("Success", "Text added!")
            
        except Exception as e:
            self.status_label.config(text="Failed to add text", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to add text: {str(e)}")
            
    def choose_text_color(self):
        """Choose text color"""
        color = colorchooser.askcolor(title="Choose text color")
        if color[1]:
            self.text_color = color[1]
            self.status_label.config(text=f"Text color: {color[1]}", fg='#3498db')
            
    def save_wallpaper(self):
        """Save the current wallpaper"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Wallpaper",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.status_label.config(text="Wallpaper saved", fg='#27ae60')
                messagebox.showinfo("Success", f"Wallpaper saved to {file_path}")
            except Exception as e:
                self.status_label.config(text="Save failed", fg='#e74c3c')
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                
    def set_as_wallpaper(self):
        """Set current image as desktop wallpaper"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to set as wallpaper")
            return
            
        try:
            temp_path = os.path.join(os.getcwd(), "temp_wallpaper.png")
            self.current_image.save(temp_path)
            
            ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_path, 0)
            self.status_label.config(text="Wallpaper set!", fg='#27ae60')
            messagebox.showinfo("Success", "✅ Wallpaper set successfully!")
            
        except Exception as e:
            self.status_label.config(text="Failed to set wallpaper", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to set wallpaper: {str(e)}")
    
    # ==================== NEW ENHANCED FUNCTIONS ====================
    
    def save_to_history(self):
        """Save current state to history for undo/redo"""
        if self.current_image:
            # Remove future history if we're not at the end
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            
            # Add new state
            self.history.append(self.current_image.copy())
            self.history_index += 1
            
            # Limit history size
            if len(self.history) > self.max_history:
                self.history.pop(0)
                self.history_index -= 1
    
    def undo(self):
        """Undo the last action"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text="Undone", fg='#f39c12')
        else:
            messagebox.showinfo("Info", "Nothing to undo")
    
    def redo(self):
        """Redo the last undone action"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text="Redone", fg='#f39c12')
        else:
            messagebox.showinfo("Info", "Nothing to redo")
    
    def auto_enhance_image(self):
        """Automatically enhance image quality"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        try:
            self.save_to_history()
            self.status_label.config(text="Auto enhancing...", fg='#f39c12')
            self.root.update()
            
            # Apply automatic enhancements
            enhanced = self.current_image.copy()
            
            # Enhance contrast
            contrast_enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = contrast_enhancer.enhance(1.2)
            
            # Enhance color saturation
            color_enhancer = ImageEnhance.Color(enhanced)
            enhanced = color_enhancer.enhance(1.1)
            
            # Enhance sharpness
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = sharpness_enhancer.enhance(1.1)
            
            # Enhance brightness slightly
            brightness_enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = brightness_enhancer.enhance(1.05)
            
            self.current_image = enhanced
            self.display_image_on_canvas()
            self.update_preview()
            self.status_label.config(text="Auto enhancement complete", fg='#27ae60')
            messagebox.showinfo("Success", "✨ Image automatically enhanced!")
            
        except Exception as e:
            self.status_label.config(text="Enhancement failed", fg='#e74c3c')
            messagebox.showerror("Error", f"Failed to enhance image: {str(e)}")
    
    def extract_color_palette(self):
        """Extract dominant colors from the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        try:
            # Create a new window to show color palette
            palette_window = tk.Toplevel(self.root)
            palette_window.title("Color Palette")
            palette_window.geometry("400x300")
            palette_window.configure(bg='#2c3e50')
            
            tk.Label(palette_window, text="Dominant Colors", 
                    bg='#2c3e50', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
            
            # Extract colors using basic sampling
            image_small = self.current_image.resize((50, 50))
            colors = []
            
            # Sample colors from different areas
            width, height = image_small.size
            for y in range(0, height, 10):
                for x in range(0, width, 10):
                    try:
                        color = image_small.getpixel((x, y))
                        if isinstance(color, tuple) and len(color) >= 3:
                            colors.append(color[:3])
                    except:
                        continue
            
            # Get unique colors and sort by frequency
            from collections import Counter
            color_counts = Counter(colors)
            dominant_colors = color_counts.most_common(8)
            
            # Display color swatches
            color_frame = tk.Frame(palette_window, bg='#2c3e50')
            color_frame.pack(pady=10)
            
            for i, (color, count) in enumerate(dominant_colors[:6]):
                color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                
                # Create color swatch
                swatch_frame = tk.Frame(color_frame, bg='#34495e', padx=5, pady=5)
                swatch_frame.grid(row=i//3, column=i%3, padx=5, pady=5)
                
                color_label = tk.Label(swatch_frame, bg=color_hex, width=8, height=3)
                color_label.pack()
                
                tk.Label(swatch_frame, text=color_hex, bg='#34495e', fg='white', 
                        font=('Arial', 8)).pack()
                
                # Make color clickable to copy to clipboard
                def copy_color(color=color_hex):
                    self.root.clipboard_clear()
                    self.root.clipboard_append(color)
                    messagebox.showinfo("Copied", f"Color {color} copied to clipboard!")
                
                color_label.bind("<Button-1>", lambda e, c=color_hex: copy_color(c))
            
            tk.Label(palette_window, text="Click on any color to copy to clipboard", 
                    bg='#2c3e50', fg='#95a5a6', font=('Arial', 9)).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract colors: {str(e)}")
    
    def open_pattern_generator(self):
        """Open pattern generator dialog"""
        pattern_window = tk.Toplevel(self.root)
        pattern_window.title("Pattern Generator")
        pattern_window.geometry("500x400")
        pattern_window.configure(bg='#2c3e50')
        
        tk.Label(pattern_window, text="Generate Patterns", 
                bg='#2c3e50', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Pattern type selection
        pattern_frame = tk.LabelFrame(pattern_window, text="Pattern Type", 
                                    bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        pattern_frame.pack(pady=10, padx=20, fill='x')
        
        pattern_var = tk.StringVar(value="geometric")
        patterns = [
            ("Geometric Circles", "geometric"),
            ("Abstract Lines", "lines"),
            ("Gradient Waves", "waves"),
            ("Hexagon Grid", "hexagons"),
            ("Spiral Pattern", "spiral")
        ]
        
        for text, value in patterns:
            tk.Radiobutton(pattern_frame, text=text, variable=pattern_var, value=value,
                          bg='#34495e', fg='white', selectcolor='#3498db').pack(anchor='w', padx=10, pady=2)
        
        # Color settings
        color_frame = tk.LabelFrame(pattern_window, text="Colors", 
                                  bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        color_frame.pack(pady=10, padx=20, fill='x')
        
        primary_color = tk.StringVar(value="#3498db")
        secondary_color = tk.StringVar(value="#e74c3c")
        
        tk.Label(color_frame, text="Primary Color:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(color_frame, textvariable=primary_color, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(color_frame, text="Secondary Color:", bg='#34495e', fg='white').grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(color_frame, textvariable=secondary_color, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Size settings
        size_frame = tk.LabelFrame(pattern_window, text="Size", 
                                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        size_frame.pack(pady=10, padx=20, fill='x')
        
        width_var = tk.IntVar(value=1920)
        height_var = tk.IntVar(value=1080)
        
        tk.Label(size_frame, text="Width:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(size_frame, textvariable=width_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(size_frame, text="Height:", bg='#34495e', fg='white').grid(row=0, column=2, padx=5, pady=5)
        tk.Entry(size_frame, textvariable=height_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        def generate_pattern():
            try:
                width = width_var.get()
                height = height_var.get()
                pattern_type = pattern_var.get()
                color1 = primary_color.get()
                color2 = secondary_color.get()
                
                self.save_to_history()
                pattern_image = self.create_pattern(pattern_type, width, height, color1, color2)
                self.current_image = pattern_image
                self.display_image_on_canvas()
                self.update_preview()
                
                pattern_window.destroy()
                self.status_label.config(text="Pattern generated", fg='#27ae60')
                messagebox.showinfo("Success", "🎨 Pattern generated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate pattern: {str(e)}")
        
        tk.Button(pattern_window, text="Generate Pattern", command=generate_pattern,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'), pady=5).pack(pady=20)
    
    def create_pattern(self, pattern_type, width, height, color1, color2):
        """Create different types of patterns"""
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        if pattern_type == "geometric":
            # Geometric circles pattern
            for x in range(0, width, 100):
                for y in range(0, height, 100):
                    color = color1 if (x + y) % 200 == 0 else color2
                    draw.ellipse([x, y, x + 80, y + 80], fill=color)
        
        elif pattern_type == "lines":
            # Abstract lines pattern
            for i in range(0, max(width, height), 20):
                color = color1 if i % 40 == 0 else color2
                draw.line([(0, i), (width, i - height//2)], fill=color, width=3)
                draw.line([(i, 0), (i - width//2, height)], fill=color, width=3)
        
        elif pattern_type == "waves":
            # Gradient waves
            for y in range(height):
                wave = int(50 * math.sin(y * 0.02))
                for x in range(width):
                    if (x + wave) % 100 < 50:
                        draw.point((x, y), fill=color1)
                    else:
                        draw.point((x, y), fill=color2)
        
        elif pattern_type == "hexagons":
            # Hexagon grid pattern
            hex_size = 50
            for row in range(0, height // hex_size + 2):
                for col in range(0, width // hex_size + 2):
                    x = col * hex_size * 1.5
                    y = row * hex_size * math.sqrt(3)
                    if row % 2:
                        x += hex_size * 0.75
                    
                    color = color1 if (row + col) % 2 == 0 else color2
                    self.draw_hexagon(draw, x, y, hex_size, color)
        
        elif pattern_type == "spiral":
            # Spiral pattern
            center_x, center_y = width // 2, height // 2
            max_radius = min(width, height) // 2
            
            for radius in range(10, max_radius, 20):
                color = color1 if radius % 40 < 20 else color2
                for angle in range(0, 360, 5):
                    x = center_x + radius * math.cos(math.radians(angle))
                    y = center_y + radius * math.sin(math.radians(angle))
                    draw.ellipse([x-5, y-5, x+5, y+5], fill=color)
        
        return image
    
    def draw_hexagon(self, draw, x, y, size, color):
        """Draw a hexagon shape"""
        points = []
        for i in range(6):
            angle = i * 60
            px = x + size * math.cos(math.radians(angle))
            py = y + size * math.sin(math.radians(angle))
            points.extend([px, py])
        draw.polygon(points, fill=color, outline='white')
    
    def open_resize_crop_dialog(self):
        """Open resize and crop dialog"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image loaded")
            return
        
        resize_window = tk.Toplevel(self.root)
        resize_window.title("Resize & Crop")
        resize_window.geometry("400x350")
        resize_window.configure(bg='#2c3e50')
        
        tk.Label(resize_window, text="Resize & Crop Image", 
                bg='#2c3e50', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Current size info
        current_size = self.current_image.size
        tk.Label(resize_window, text=f"Current size: {current_size[0]} x {current_size[1]}", 
                bg='#2c3e50', fg='#95a5a6').pack()
        
        # Resize section
        resize_frame = tk.LabelFrame(resize_window, text="Resize", 
                                   bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        resize_frame.pack(pady=10, padx=20, fill='x')
        
        new_width = tk.IntVar(value=current_size[0])
        new_height = tk.IntVar(value=current_size[1])
        maintain_aspect = tk.BooleanVar(value=True)
        
        tk.Label(resize_frame, text="Width:", bg='#34495e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(resize_frame, textvariable=new_width, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(resize_frame, text="Height:", bg='#34495e', fg='white').grid(row=0, column=2, padx=5, pady=5)
        height_entry = tk.Entry(resize_frame, textvariable=new_height, width=10)
        height_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Checkbutton(resize_frame, text="Maintain aspect ratio", variable=maintain_aspect,
                      bg='#34495e', fg='white', selectcolor='#3498db').grid(row=1, column=0, columnspan=4, pady=5)
        
        # Auto-update height when width changes if aspect ratio is maintained
        def update_height(*args):
            if maintain_aspect.get():
                try:
                    ratio = current_size[1] / current_size[0]
                    new_height.set(int(new_width.get() * ratio))
                except:
                    pass
        
        def update_width(*args):
            if maintain_aspect.get():
                try:
                    ratio = current_size[0] / current_size[1]
                    new_width.set(int(new_height.get() * ratio))
                except:
                    pass
        
        new_width.trace('w', update_height)
        new_height.trace('w', update_width)
        
        # Quick resize buttons
        quick_frame = tk.Frame(resize_frame, bg='#34495e')
        quick_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        quick_sizes = [("HD", 1920, 1080), ("4K", 3840, 2160), ("Square", 1080, 1080)]
        for text, w, h in quick_sizes:
            def set_size(width=w, height=h):
                new_width.set(width)
                new_height.set(height)
            
            tk.Button(quick_frame, text=text, command=lambda w=w, h=h: set_size(w, h),
                     bg='#3498db', fg='white', padx=10).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = tk.Frame(resize_window, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        def apply_resize():
            try:
                self.save_to_history()
                width = new_width.get()
                height = new_height.get()
                
                self.current_image = self.current_image.resize((width, height), Image.Resampling.LANCZOS)
                self.display_image_on_canvas()
                self.update_preview()
                
                resize_window.destroy()
                self.status_label.config(text=f"Resized to {width}x{height}", fg='#27ae60')
                messagebox.showinfo("Success", f"Image resized to {width}x{height}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resize: {str(e)}")
        
        tk.Button(button_frame, text="Apply Resize", command=apply_resize,
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Cancel", command=resize_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side=tk.LEFT, padx=10)
    
    def open_batch_processor(self):
        """Open batch processor for multiple images"""
        batch_window = tk.Toplevel(self.root)
        batch_window.title("Batch Processor")
        batch_window.geometry("600x500")
        batch_window.configure(bg='#2c3e50')
        
        tk.Label(batch_window, text="Batch Image Processor", 
                bg='#2c3e50', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
        
        # File list
        list_frame = tk.LabelFrame(batch_window, text="Images to Process", 
                                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        file_listbox = tk.Listbox(list_frame, bg='#2c3e50', fg='white', selectbackground='#3498db')
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=file_listbox.yview)
        file_listbox.configure(yscrollcommand=scrollbar.set)
        
        file_listbox.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill='y', pady=5)
        
        self.batch_files = []
        
        def add_files():
            files = filedialog.askopenfilenames(
                title="Select Images",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("All files", "*.*")
                ]
            )
            for file in files:
                if file not in self.batch_files:
                    self.batch_files.append(file)
                    file_listbox.insert(tk.END, os.path.basename(file))
        
        def remove_file():
            selection = file_listbox.curselection()
            if selection:
                index = selection[0]
                file_listbox.delete(index)
                del self.batch_files[index]
        
        def clear_files():
            file_listbox.delete(0, tk.END)
            self.batch_files.clear()
        
        # Buttons for file management
        btn_frame = tk.Frame(list_frame, bg='#34495e')
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Button(btn_frame, text="Add Files", command=add_files,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Remove", command=remove_file,
                 bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Clear All", command=clear_files,
                 bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=2)
        
        # Processing options
        options_frame = tk.LabelFrame(batch_window, text="Processing Options", 
                                    bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        options_frame.pack(pady=10, padx=20, fill='x')
        
        resize_batch = tk.BooleanVar()
        enhance_batch = tk.BooleanVar()
        add_text_batch = tk.BooleanVar()
        
        batch_width = tk.IntVar(value=1920)
        batch_height = tk.IntVar(value=1080)
        batch_text = tk.StringVar(value="Sample Text")
        
        tk.Checkbutton(options_frame, text="Resize images", variable=resize_batch,
                      bg='#34495e', fg='white', selectcolor='#3498db').grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        tk.Label(options_frame, text="to", bg='#34495e', fg='white').grid(row=0, column=1, padx=5)
        tk.Entry(options_frame, textvariable=batch_width, width=8).grid(row=0, column=2, padx=2)
        tk.Label(options_frame, text="x", bg='#34495e', fg='white').grid(row=0, column=3, padx=2)
        tk.Entry(options_frame, textvariable=batch_height, width=8).grid(row=0, column=4, padx=2)
        
        tk.Checkbutton(options_frame, text="Auto enhance", variable=enhance_batch,
                      bg='#34495e', fg='white', selectcolor='#3498db').grid(row=1, column=0, sticky='w', padx=5, pady=2)
        
        tk.Checkbutton(options_frame, text="Add text", variable=add_text_batch,
                      bg='#34495e', fg='white', selectcolor='#3498db').grid(row=2, column=0, sticky='w', padx=5, pady=2)
        tk.Entry(options_frame, textvariable=batch_text, width=20).grid(row=2, column=1, columnspan=4, padx=5, pady=2)
        
        # Output directory
        output_frame = tk.Frame(options_frame, bg='#34495e')
        output_frame.grid(row=3, column=0, columnspan=5, pady=10, sticky='ew')
        
        output_dir = tk.StringVar(value=os.getcwd())
        tk.Label(output_frame, text="Output Directory:", bg='#34495e', fg='white').pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=output_dir, width=30).pack(side=tk.LEFT, padx=5)
        
        def choose_output_dir():
            directory = filedialog.askdirectory()
            if directory:
                output_dir.set(directory)
        
        tk.Button(output_frame, text="Browse", command=choose_output_dir,
                 bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(batch_window, variable=progress_var, maximum=100)
        progress_bar.pack(pady=10, padx=20, fill='x')
        
        status_var = tk.StringVar(value="Ready to process")
        tk.Label(batch_window, textvariable=status_var, bg='#2c3e50', fg='#95a5a6').pack()
        
        def process_batch():
            if not self.batch_files:
                messagebox.showwarning("Warning", "No files selected")
                return
            
            def process_thread():
                try:
                    self.is_batch_processing = True
                    total_files = len(self.batch_files)
                    output_directory = output_dir.get()
                    
                    for i, file_path in enumerate(self.batch_files):
                        # Update status
                        filename = os.path.basename(file_path)
                        status_var.set(f"Processing {filename}...")
                        progress_var.set((i / total_files) * 100)
                        batch_window.update()
                        
                        try:
                            # Load image
                            image = Image.open(file_path)
                            
                            # Apply processing options
                            if resize_batch.get():
                                image = image.resize((batch_width.get(), batch_height.get()), Image.Resampling.LANCZOS)
                            
                            if enhance_batch.get():
                                # Apply auto enhancement
                                contrast_enhancer = ImageEnhance.Contrast(image)
                                image = contrast_enhancer.enhance(1.2)
                                
                                color_enhancer = ImageEnhance.Color(image)
                                image = color_enhancer.enhance(1.1)
                                
                                sharpness_enhancer = ImageEnhance.Sharpness(image)
                                image = sharpness_enhancer.enhance(1.1)
                            

                            if add_text_batch.get():
                                # Add text overlay
                                draw = ImageDraw.Draw(image)
                                try:
                                    font = ImageFont.truetype("arial.ttf", 60)
                                except:
                                    font = ImageFont.load_default()
                                
                                text = batch_text.get()
                                bbox = draw.textbbox((0, 0), text, font=font)
                                text_width = bbox[2] - bbox[0]
                                text_height = bbox[3] - bbox[1]
                                
                                x = (image.width - text_width) // 2
                                y = image.height - text_height - 50
                                
                                # Draw text with outline
                                for adj in range(-2, 3):
                                    for adj2 in range(-2, 3):
                                        draw.text((x + adj, y + adj2), text, font=font, fill="black")
                                draw.text((x, y), text, font=font, fill="white")
                            

                            # Save processed image
                            base_name = os.path.splitext(filename)[0]
                            output_path = os.path.join(output_directory, f"{base_name}_processed.png")
                            image.save(output_path)
                            
                        except Exception as e:
                            print(f"Error processing {filename}: {e}")
                            continue
                    
                    # Complete
                    progress_var.set(100)
                    status_var.set(f"Completed! Processed {total_files} images")
                    messagebox.showinfo("Success", f"Batch processing complete!\nProcessed {total_files} images")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Batch processing failed: {str(e)}")
                finally:
                    self.is_batch_processing = False
            
            # Run processing in a separate thread
            threading.Thread(target=process_thread, daemon=True).start()
        
        # Process button
        tk.Button(batch_window, text="Start Processing", command=process_batch,
                 bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), pady=5).pack(pady=10)
    
    def open_template_manager(self):
        """Open template manager for saving and loading design templates"""
        template_window = tk.Toplevel(self.root)
        template_window.title("Template Manager")
        template_window.geometry("500x400")
        template_window.configure(bg='#2c3e50')
        
        tk.Label(template_window, text="Template Manager", 
                bg='#2c3e50', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Create templates directory if it doesn't exist
        templates_dir = "templates"
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        
        # Template list
        list_frame = tk.LabelFrame(template_window, text="Saved Templates", 
                                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        template_listbox = tk.Listbox(list_frame, bg='#2c3e50', fg='white', selectbackground='#3498db')
        template_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        def refresh_templates():
            template_listbox.delete(0, tk.END)
            try:
                for file in os.listdir(templates_dir):
                    if file.endswith('.json'):
                        template_listbox.insert(tk.END, file[:-5])  # Remove .json extension
            except:
                pass
        
        refresh_templates()
        
        # Save current settings as template
        save_frame = tk.LabelFrame(template_window, text="Save Current Settings", 
                                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'))
        save_frame.pack(pady=10, padx=20, fill='x')
        
        template_name = tk.StringVar()
        tk.Label(save_frame, text="Template Name:", bg='#34495e', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(save_frame, textvariable=template_name, width=20).pack(side=tk.LEFT, padx=5)
        
        def save_template():
            name = template_name.get().strip()
            if not name:
                messagebox.showwarning("Warning", "Please enter a template name")
                return
            
            try:
                template_data = {
                    "name": name,
                    "created": datetime.now().isoformat(),
                    "filter_settings": self.filter_settings.copy(),
                    "text_color": self.text_color,
                    "font_size": self.font_size
                }
                
                template_path = os.path.join(templates_dir, f"{name}.json")
                with open(template_path, 'w') as f:
                    json.dump(template_data, f, indent=2)
                
                refresh_templates()
                template_name.set("")
                messagebox.showinfo("Success", f"Template '{name}' saved successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save template: {str(e)}")
        
        tk.Button(save_frame, text="Save", command=save_template,
                 bg='#27ae60', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Load template
        def load_template():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template")
                return
            
            template_name_selected = template_listbox.get(selection[0])
            template_path = os.path.join(templates_dir, f"{template_name_selected}.json")
            
            try:
                with open(template_path, 'r') as f:
                    template_data = json.load(f)
                
                # Apply template settings
                self.filter_settings = template_data.get("filter_settings", self.filter_settings)
                self.text_color = template_data.get("text_color", self.text_color)
                self.font_size = template_data.get("font_size", self.font_size)
                
                # Update UI elements if they exist
                if hasattr(self, 'brightness_scale'):
                    self.brightness_scale.set(self.filter_settings['brightness'])
                if hasattr(self, 'contrast_scale'):
                    self.contrast_scale.set(self.filter_settings['contrast'])
                if hasattr(self, 'saturation_scale'):
                    self.saturation_scale.set(self.filter_settings['saturation'])
                if hasattr(self, 'blur_scale'):
                    self.blur_scale.set(self.filter_settings['blur'])
                
                messagebox.showinfo("Success", f"Template '{template_name_selected}' loaded successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load template: {str(e)}")
        
        def delete_template():
            selection = template_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a template")
                return
            
            template_name_selected = template_listbox.get(selection[0])
            
            if messagebox.askyesno("Confirm", f"Delete template '{template_name_selected}'?"):
                try:
                    template_path = os.path.join(templates_dir, f"{template_name_selected}.json")
                    os.remove(template_path)
                    refresh_templates()
                    messagebox.showinfo("Success", f"Template '{template_name_selected}' deleted")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete template: {str(e)}")
        
        # Template action buttons
        action_frame = tk.Frame(template_window, bg='#2c3e50')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="Load Template", command=load_template,
                 bg='#3498db', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Delete Template", command=delete_template,
                 bg='#e74c3c', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Refresh", command=refresh_templates,
                 bg='#95a5a6', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
    
    # ==================== END OF NEW FUNCTIONS ====================
def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ProfessionalWallpaperCreator(root)
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()

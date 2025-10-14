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
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def setup_toolbar(self):
        """Create toolbar with quick actions"""
        toolbar = tk.Frame(self.root, bg='#34495e', height=50)
        toolbar.pack(fill=tk.X, pady=2)
        
        btn_style = {'bg': '#3498db', 'fg': 'white', 'font': ('Arial', 10, 'bold'), 'padx': 10}
        
        tk.Button(toolbar, text="📁 Open", command=self.open_image, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="💾 Save", command=self.save_wallpaper, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="🌐 Get Image", command=self.get_unsplash_image, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(toolbar, text="📝 Add Text", command=self.add_text_layer, **btn_style).pack(side=tk.LEFT, padx=5, pady=5)
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

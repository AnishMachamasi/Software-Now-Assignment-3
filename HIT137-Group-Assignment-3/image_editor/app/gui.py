import os
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageTk


class PictureProcessorApp:
    """Main application class for picture processing with GUI."""
    
    def __init__(self, window: tk.Tk):
        """Initialize the application with main window."""
        self.window = window
        self.window.title("Picture Processing App")
        self.window.geometry("1200x800")

        # Initialize image variables
        self.original_picture: Optional[np.ndarray] = None
        self.cropped_picture: Optional[np.ndarray] = None
        self.display_picture: Optional[np.ndarray] = None
        
        # Initialize cropping and scaling variables
        self.crop_start: Optional[Tuple[int, int]] = None
        self.crop_rect: Optional[Tuple[int, int, int, int]] = None
        self.scale_factor: float = 1.0
        self.display_to_picture_scale: Tuple[float, float] = (1.0, 1.0)
        self.picture_offset: Tuple[int, int] = (0, 0)
        
        self.setup_window()

    def setup_window(self) -> None:
        """Set up the GUI components."""
        # Menu bar setup
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_picture)
        filemenu.add_command(label="Save", command=self.save_picture)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.window.config(menu=menubar)

        # Main frames setup
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Original picture frame
        self.original_frame = tk.LabelFrame(main_frame, text="Original Picture")
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_canvas = tk.Canvas(self.original_frame, bg='lightpink', width=600, height=600)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        self.original_canvas.bind("<ButtonPress-1>", self.start_crop)
        self.original_canvas.bind("<B1-Motion>", self.update_crop)
        self.original_canvas.bind("<ButtonRelease-1>", self.end_crop)

        # Processed picture frame
        self.processed_frame = tk.LabelFrame(main_frame, text="Processed Picture")
        self.processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.processed_canvas = tk.Canvas(self.processed_frame, bg='lightpink', width=600, height=600)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)

        # Controls frame
        controls_frame = tk.Frame(self.window)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Buttons frame
        btn_frame = tk.Frame(controls_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)

        # Processing buttons
        buttons = [
            ("Open", self.open_picture),
            ("Grayscale", self.convert_grayscale),
            ("Blur", self.add_blur),
            ("Rotate Left", self.rotate_left),
            ("Rotate Right", self.rotate_right),
            ("Edge", self.apply_edge_detection),
            ("Bright+", self.increase_brightness),
            ("Bright−", self.decrease_brightness),
            ("Sepia", self.apply_sepia),
            ("Invert", self.invert_colors),
            ("Save", self.save_picture),
            ("Reset", self.reset_picture),
            ("Exit", self.window.quit)
        ]

        for text, command in buttons:
            tk.Button(btn_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

        # Scale controls
        self.scale_label = tk.Label(controls_frame, text="Resize Scale: 1.0")
        self.scale_label.pack(side=tk.LEFT, padx=5)

        self.scale_slider = ttk.Scale(
            controls_frame,
            from_=0.1,
            to=3.0,
            value=1.0,
            command=self.update_scale
        )
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Status bar
        self.status_bar = tk.Label(self.window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    def validate_image(self, image: np.ndarray) -> bool:
        """Validate that an image is properly loaded and has valid dimensions."""
        if image is None:
            self.status_bar.config(text="Error: Invalid image (None)")
            return False
        if not isinstance(image, np.ndarray):
            self.status_bar.config(text="Error: Image must be a numpy array")
            return False
        if len(image.shape) not in (2, 3):
            self.status_bar.config(text="Error: Invalid image dimensions")
            return False
        return True

    def open_picture(self) -> None:
        """Open an image file and load it into the application."""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if not file_path:
            self.status_bar.config(text="No file selected")
            return
            
        if not os.path.exists(file_path):
            self.status_bar.config(text="Error: File does not exist")
            return
            
        try:
            # Read and validate the image
            pic = cv2.imread(file_path)
            if not self.validate_image(pic):
                return
                
            pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
            self.original_picture = pic
            self.display_picture = pic.copy()
            self.cropped_picture = None
            self.crop_rect = None
            self.scale_factor = 1.0
            self.scale_slider.set(1.0)
            self.update_picture_display()
            self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_bar.config(text=f"Error: {str(e)}")

    def convert_grayscale(self) -> None:
        """Convert the cropped image to grayscale."""
        if not self.validate_cropped_image():
            return
            
        try:
            gray = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2GRAY)
            self.cropped_picture = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.update_picture_display()
            self.status_bar.config(text="Converted to grayscale")
        except Exception as e:
            self.status_bar.config(text=f"Error converting to grayscale: {str(e)}")

    def validate_cropped_image(self) -> bool:
        """Validate that we have a cropped image to process."""
        if self.cropped_picture is None:
            self.status_bar.config(text="Error: No cropped image to process")
            return False
        return self.validate_image(self.cropped_picture)

    def add_blur(self) -> None:
        """Apply Gaussian blur to the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            self.cropped_picture = cv2.GaussianBlur(self.cropped_picture, (15, 15), 0)
            self.update_picture_display()
            self.status_bar.config(text="Blur added")
        except Exception as e:
            self.status_bar.config(text=f"Error applying blur: {str(e)}")

    def rotate_left(self) -> None:
        """Rotate the cropped image 90 degrees counter-clockwise."""
        if not self.validate_cropped_image():
            return
            
        try:
            self.cropped_picture = cv2.rotate(self.cropped_picture, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.update_picture_display()
            self.status_bar.config(text="Rotated left")
        except Exception as e:
            self.status_bar.config(text=f"Error rotating image: {str(e)}")

    def rotate_right(self) -> None:
        """Rotate the cropped image 90 degrees clockwise."""
        if not self.validate_cropped_image():
            return
            
        try:
            self.cropped_picture = cv2.rotate(self.cropped_picture, cv2.ROTATE_90_CLOCKWISE)
            self.update_picture_display()
            self.status_bar.config(text="Rotated right")
        except Exception as e:
            self.status_bar.config(text=f"Error rotating image: {str(e)}")

    def apply_edge_detection(self) -> None:
        """Apply Canny edge detection to the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            gray = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            self.cropped_picture = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            self.update_picture_display()
            self.status_bar.config(text="Edge detection applied")
        except Exception as e:
            self.status_bar.config(text=f"Error applying edge detection: {str(e)}")

    def validate_brightness_value(self, value: int) -> bool:
        """Validate brightness adjustment value."""
        if not isinstance(value, (int, float)):
            self.status_bar.config(text="Error: Brightness value must be numeric")
            return False
        return True

    def increase_brightness(self) -> None:
        """Increase brightness of the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            brightness_value = 50
            if not self.validate_brightness_value(brightness_value):
                return
                
            hsv = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            
            # Ensure we don't exceed valid range (0-255)
            v = np.where(v <= 255 - brightness_value, v + brightness_value, 255)
            
            final_hsv = cv2.merge((h, s, v))
            self.cropped_picture = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2RGB)
            self.update_picture_display()
            self.status_bar.config(text="Brightness increased")
        except Exception as e:
            self.status_bar.config(text=f"Error adjusting brightness: {str(e)}")

    def decrease_brightness(self) -> None:
        """Decrease brightness of the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            brightness_value = 50
            if not self.validate_brightness_value(brightness_value):
                return
                
            hsv = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            
            # Ensure we don't go below 0
            v = np.where(v >= brightness_value, v - brightness_value, 0)
            
            final_hsv = cv2.merge((h, s, v))
            self.cropped_picture = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2RGB)
            self.update_picture_display()
            self.status_bar.config(text="Brightness decreased")
        except Exception as e:
            self.status_bar.config(text=f"Error adjusting brightness: {str(e)}")

    def apply_sepia(self) -> None:
        """Apply sepia filter to the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            kernel = np.array([
                [0.272, 0.534, 0.131],
                [0.349, 0.686, 0.168],
                [0.393, 0.769, 0.189]
            ])
            
            # Validate kernel values
            if not isinstance(kernel, np.ndarray) or kernel.shape != (3, 3):
                self.status_bar.config(text="Error: Invalid sepia kernel")
                return
                
            sepia = cv2.transform(self.cropped_picture, kernel)
            sepia = np.clip(sepia, 0, 255).astype(np.uint8)
            self.cropped_picture = sepia
            self.update_picture_display()
            self.status_bar.config(text="Sepia filter applied")
        except Exception as e:
            self.status_bar.config(text=f"Error applying sepia: {str(e)}")

    def invert_colors(self) -> None:
        """Invert colors of the cropped image."""
        if not self.validate_cropped_image():
            return
            
        try:
            self.cropped_picture = cv2.bitwise_not(self.cropped_picture)
            self.update_picture_display()
            self.status_bar.config(text="Colors inverted")
        except Exception as e:
            self.status_bar.config(text=f"Error inverting colors: {str(e)}")

    def reset_picture(self) -> None:
        """Reset the image to its original state."""
        if self.original_picture is None:
            self.status_bar.config(text="No original image to reset to")
            return
            
        try:
            self.display_picture = self.original_picture.copy()
            self.cropped_picture = None
            self.crop_rect = None
            self.scale_factor = 1.0
            self.scale_slider.set(1.0)
            self.update_picture_display()
            self.processed_canvas.delete("all")
            self.status_bar.config(text="Picture reset")
        except Exception as e:
            self.status_bar.config(text=f"Error resetting picture: {str(e)}")

    def update_picture_display(self) -> None:
        """Update the display of both original and processed images."""
        MAX_WIDTH, MAX_HEIGHT = 600, 600

        # Update original picture display
        if self.display_picture is not None and self.validate_image(self.display_picture):
            try:
                pic = self.display_picture.copy()
                h, w = pic.shape[:2]
                
                # Calculate display scale
                scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)
                disp_w, disp_h = int(w * scale), int(h * scale)
                
                # Resize and convert for display
                pic_resized = cv2.resize(pic, (disp_w, disp_h))
                pic_pil = Image.fromarray(pic_resized)
                pic_tk = ImageTk.PhotoImage(pic_pil)

                # Update canvas
                self.original_canvas.config(width=MAX_WIDTH, height=MAX_HEIGHT)
                self.original_canvas.delete("all")

                # Calculate offsets for centering
                x_offset = (MAX_WIDTH - disp_w) // 2
                y_offset = (MAX_HEIGHT - disp_h) // 2
                self.picture_offset = (x_offset, y_offset)

                # Display image
                self.original_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=pic_tk)
                self.original_canvas.image = pic_tk
                self.display_to_picture_scale = (w / disp_w, h / disp_h)

                # Draw crop rectangle if exists
                if self.crop_rect:
                    x1, y1, x2, y2 = self.crop_rect
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(MAX_WIDTH, x2), min(MAX_HEIGHT, y2)
                    self.original_canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2)
            except Exception as e:
                self.status_bar.config(text=f"Error updating display: {str(e)}")

        # Update processed picture display
        if self.cropped_picture is not None and self.validate_image(self.cropped_picture):
            try:
                processed_pic = self.cropped_picture.copy()
                new_w = int(processed_pic.shape[1] * self.scale_factor)
                new_h = int(processed_pic.shape[0] * self.scale_factor)

                # Adjust size if too large
                if new_w > MAX_WIDTH or new_h > MAX_HEIGHT:
                    ratio = min(MAX_WIDTH / new_w, MAX_HEIGHT / new_h)
                    new_w = int(new_w * ratio)
                    new_h = int(new_h * ratio)

                # Resize and convert for display
                processed_pic = cv2.resize(processed_pic, (new_w, new_h))
                processed_pic_pil = Image.fromarray(processed_pic)
                processed_pic_tk = ImageTk.PhotoImage(image=processed_pic_pil)

                # Update canvas
                self.processed_canvas.config(width=MAX_WIDTH, height=MAX_HEIGHT)
                self.processed_canvas.delete("all")
                
                # Calculate offsets for centering
                x_offset = (MAX_WIDTH - new_w) // 2
                y_offset = (MAX_HEIGHT - new_h) // 2
                
                # Display image
                self.processed_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=processed_pic_tk)
                self.processed_canvas.image = processed_pic_tk
            except Exception as e:
                self.status_bar.config(text=f"Error updating processed display: {str(e)}")

    def start_crop(self, event: tk.Event) -> None:
        """Start cropping operation."""
        if self.display_picture is not None and self.validate_image(self.display_picture):
            self.crop_start = (event.x, event.y)
            self.crop_rect = None

    def update_crop(self, event: tk.Event) -> None:
        """Update crop rectangle during mouse drag."""
        if self.crop_start and self.display_picture is not None and self.validate_image(self.display_picture):
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y
            
            # Constrain coordinates to canvas dimensions
            canvas_width = self.original_canvas.winfo_width()
            canvas_height = self.original_canvas.winfo_height()
            x1, x2 = max(0, min(x1, canvas_width)), max(0, min(x2, canvas_width))
            y1, y2 = max(0, min(y1, canvas_height)), max(0, min(y2, canvas_height))
            
            self.crop_rect = (x1, y1, x2, y2)
            self.update_picture_display()

    def end_crop(self, _: tk.Event) -> None:
        """Finalize cropping operation."""
        if self.crop_rect and self.display_picture is not None and self.validate_image(self.display_picture):
            try:
                x1, y1, x2, y2 = self.crop_rect
                x1, x2 = sorted((x1, x2))
                y1, y2 = sorted((y1, y2))

                # Convert canvas coordinates to image coordinates
                x_offset, y_offset = self.picture_offset
                scale_x, scale_y = self.display_to_picture_scale
                
                crop_x1 = int((x1 - x_offset) * scale_x)
                crop_y1 = int((y1 - y_offset) * scale_y)
                crop_x2 = int((x2 - x_offset) * scale_x)
                crop_y2 = int((y2 - y_offset) * scale_y)

                # Constrain to image dimensions
                crop_x1 = max(0, crop_x1)
                crop_y1 = max(0, crop_y1)
                crop_x2 = min(self.display_picture.shape[1], crop_x2)
                crop_y2 = min(self.display_picture.shape[0], crop_y2)

                # Validate crop region
                if crop_x2 > crop_x1 and crop_y2 > crop_y1:
                    self.cropped_picture = self.display_picture[crop_y1:crop_y2, crop_x1:crop_x2]
                    self.status_bar.config(text=f"Cropped region: ({crop_x1}, {crop_y1}) to ({crop_x2}, {crop_y2})")
                else:
                    self.status_bar.config(text="Invalid crop region")
                    
                self.update_picture_display()
            except Exception as e:
                self.status_bar.config(text=f"Error during cropping: {str(e)}")

    def update_scale(self, value: str) -> None:
        """Update the scale factor for the processed image."""
        try:
            scale = float(value)
            if 0.1 <= scale <= 3.0:
                self.scale_factor = scale
                self.scale_label.config(text=f"Resize Scale: {self.scale_factor:.1f}")
                self.update_picture_display()
            else:
                self.status_bar.config(text="Scale must be between 0.1 and 3.0")
        except ValueError:
            self.status_bar.config(text="Invalid scale value")

    def save_picture(self) -> None:
        """Save the processed image to a file."""
        if not self.validate_cropped_image():
            return
            
        file_types = [
            ("JPEG", "*.jpg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=file_types,
        )
        
        if not file_path:
            self.status_bar.config(text="Save cancelled")
            return
            
        try:
            # Convert color space and save
            img_to_save = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2BGR)
            if not cv2.imwrite(file_path, img_to_save):
                raise IOError("Failed to write image file")
                
            self.status_bar.config(text=f"Saved to: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_bar.config(text=f"Error saving file: {str(e)}")
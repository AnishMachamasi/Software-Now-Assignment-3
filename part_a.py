import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

class PictureProcessorApp:
    def __init__(self, window):  # initialize the main window
        self.window = window  
        self.window.title("Picture Processing App")  # set window title
        self.window.geometry("1200x800")  

        self.original_picture = None  # stores the original picture
        self.cropped_picture = None  # stores the cutting portion of picture
        self.display_picture = None  #show the current picture in the canvas
        self.crop_start = None       # start coordinations for cutting
        self.crop_rect = None        #Cutting rectangle coordinates
        self.scale_factor = 1.0       # current scale for procrssed pic
        self.display_to_picture_scale = (1.0, 1.0)  # scale between display size and actual pic
        self.picture_offset = (0,0)      #update stores pic offset in canvas
        self.setup_window()            # set up GUI
        
        # create the menus, buttons, and display areas
    def setup_window(self):  
        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_picture)
        filemenu.add_command(label="Save", command=self.save_picture)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.window.config(menu=menubar)
           #the main frame holds the image display
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
         #left panel with crop functional
        self.original_frame = tk.LabelFrame(main_frame, text="Original Picture")
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.original_canvas = tk.Canvas(self.original_frame, bg='lightpink', width=600, height=600)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
          #bind mouse
        self.original_canvas.bind("<ButtonPress-1>", self.start_crop) # mouse can cut pic
        self.original_canvas.bind("<B1-Motion>", self.update_crop)  #drag to update the crop box
        self.original_canvas.bind("<ButtonRelease-1>", self.end_crop) # show the final pic
          #the right side can process pic
        self.processed_frame = tk.LabelFrame(main_frame, text="Processed Picture")
        self.processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.processed_canvas = tk.Canvas(self.processed_frame, bg='lightpink', width=600, height=600)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True) 
         # bottom control panel with buttons 
        controls_frame = tk.Frame(self.window)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        btn_frame = tk.Frame(controls_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
         #adding different button fuctions
        tk.Button(btn_frame, text="Open", command=self.open_picture).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Grayscale", command=self.convert_grayscale).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Blur", command=self.add_blur).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Save", command=self.save_picture).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reset", command=self.reset_picture).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Exit", command=self.window.quit).pack(side=tk.LEFT, padx=5)
        
        # room slider
        self.scale_label = tk.Label(controls_frame, text="Resize Scale: 1.0")
        self.scale_label.pack(side=tk.LEFT, padx=5)
  
        self.scale_slider = ttk.Scale(  
            controls_frame,
            from_=0.1,  
            to=3.0,
            value=1.0, # strats at normal size
            command=self.update_scale
        )
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.status_bar = tk.Label(self.window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5)

    # select the picture from users 
    def open_picture(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if file_path:
            try:               #reading and converting from bgr to rgb 
                pic = cv2.imread(file_path)
                if pic is not None:
                    pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
                    self.original_picture = pic
                    self.display_picture = pic.copy()
                    self.cropped_picture = None
                    self.crop_rect = None
                    self.scale_factor = 1.0
                    self.scale_slider.set(1.0)
                    self.update_picture_display()
                    self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
                else:
                    self.status_bar.config(text="Error: Cannot open picture")
            except Exception as e:
                self.status_bar.config(text=f"Error: {str(e)}")

    # convert the cutting pic to grayscale
    def convert_grayscale(self):
        if self.cropped_picture is not None:
            gray = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2GRAY)
            self.cropped_picture = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            self.update_picture_display()
            self.status_bar.config(text="Converted to grayscale")
        else:
            self.status_bar.config(text="Nothing to convert")

    # adding blur to cropped pic
    def add_blur(self):
        if self.cropped_picture is not None:
            self.cropped_picture = cv2.GaussianBlur(self.cropped_picture, (15, 15), 0)
            self.update_picture_display()
            self.status_bar.config(text="blur added")
        else:
            self.status_bar.config(text="Nothing to blur")

    # restore to the original picture
    def reset_picture(self):
        if self.original_picture is not None:
            self.display_picture = self.original_picture.copy()
            self.cropped_picture = None
            self.crop_rect = None
            self.scale_factor = 1.0
            self.scale_slider.set(1.0)
            self.update_picture_display()
            self.processed_canvas.delete("all")  # Clear right canvas
            self.status_bar.config(text="Picture reset")

    # update the display canvases with the current pictures
    def update_picture_display(self):
        MAX_WIDTH, MAX_HEIGHT = 600, 600

         # show the original pic if it exists
        if self.display_picture is not None:
            pic = self.display_picture.copy()
            h, w = pic.shape[:2]
             # calculate scale factor to fit the canvas
            scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)
            disp_w, disp_h = int(w * scale), int(h * scale)
             #resize and convert to pic
            pic_resized = cv2.resize(pic, (disp_w, disp_h))
            pic_pil = Image.fromarray(pic_resized)
            pic_tk = ImageTk.PhotoImage(pic_pil)
            
            #update the canvas size 
            self.original_canvas.config(width=MAX_WIDTH, height=MAX_HEIGHT)
            self.original_canvas.delete("all")
            
            #calculate and store pic
            x_offset = (MAX_WIDTH - disp_w) // 2
            y_offset = (MAX_HEIGHT - disp_h) // 2
            self.picture_offset = (x_offset, y_offset)
            
            self.original_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=pic_tk)
            self.original_canvas.image = pic_tk
            self.display_to_picture_scale = (w/disp_w, h/disp_h) #update cuz more accurate

              #draw crop rectangle if it exists
            if self.crop_rect:
                x1, y1, x2, y2 = self.crop_rect
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(MAX_WIDTH, x2), min(MAX_HEIGHT, y2)
                self.original_canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2)

          # show the cutted pic 
        if self.cropped_picture is not None:
            processed_pic = self.cropped_picture.copy()
            new_w = int(processed_pic.shape[1] * self.scale_factor)
            new_h = int(processed_pic.shape[0] * self.scale_factor)

                # resize it if larger than display size
            if new_w > MAX_WIDTH or new_h > MAX_HEIGHT:
                ratio = min(MAX_WIDTH / new_w, MAX_HEIGHT / new_h)
                new_w = int(new_w * ratio)
                new_h = int(new_h * ratio)

            processed_pic = cv2.resize(processed_pic, (new_w, new_h))
            processed_pic_pil = Image.fromarray(processed_pic)
            processed_pic_tk = ImageTk.PhotoImage(image=processed_pic_pil)

            self.processed_canvas.config(width=MAX_WIDTH, height=MAX_HEIGHT)
            self.processed_canvas.delete("all")
            x_offset = (MAX_WIDTH - new_w) // 2
            y_offset = (MAX_HEIGHT - new_h) // 2
            self.processed_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=processed_pic_tk)
            self.processed_canvas.image = processed_pic_tk

    # start cropping when mouse is clicked
    def start_crop(self, event):
        if self.display_picture is not None:
            self.crop_start = (event.x, event.y)
            self.crop_rect = None #reset previous cutting

    # update cropping rectangle while dragging mouse
    def update_crop(self, event):
        if self.crop_start and self.display_picture is not None:
            x1, y1 = self.crop_start
            x2, y2 = event.x, event.y
            canvas_width = self.original_canvas.winfo_width()
            canvas_height = self.original_canvas.winfo_height()
            x1, x2 = max(0, min(x1, canvas_width)), max(0, min(x2, canvas_width))
            y1, y2 = max(0, min(y1, canvas_height)), max(0, min(y2, canvas_height))
            self.crop_rect = (x1,y1,x2,y2)
            self.update_picture_display()

    # finish cropping 
    def end_crop(self, _):  # '_' means ignoring the event parameter
        if self.crop_rect and self.display_picture is not None:
            x1, y1, x2, y2 = self.crop_rect
            x1, x2 = sorted((x1, x2))    #make sure x1< x2
            y1, y2 = sorted((y1, y2))     #same as above 

            
            #  image offset and scaling factors
            x_offset, y_offset = self.picture_offset
            scale_x, scale_y = self.display_to_picture_scale
            pic_h, pic_w = self.display_picture.shape[:2]

            # convert canvas coordinates to image coordinates
            crop_x1 = int((x1 -x_offset) * scale_x)
            crop_y1 = int((y1 -y_offset) * scale_y)
            crop_x2 = int((x2 -x_offset) * scale_x)
            crop_y2 = int((y2 -y_offset) * scale_y)
             #make sure the coordinates are within the pic bounds
            crop_x1 = max(0, crop_x1)
            crop_y1 = max(0, crop_y1)
            crop_x2 = min(pic_w, crop_x2)
            crop_y2 = min(pic_h, crop_y2)


            if (crop_x2 - crop_x1) >= 10 and (crop_y2 - crop_y1) >= 10: # if cropping is effective, use the cropped portion
                self.cropped_picture = self.display_picture[crop_y1:crop_y2, crop_x1:crop_x2].copy()
                self.scale_factor = 1.0
                self.scale_slider.set(1.0)
                self.update_picture_display()
                self.status_bar.config(text="Picture cropped successfully")
            else:
                self.status_bar.config(text="Crop area too small ")
        
   
    # update scale when slider is moved
    def update_scale(self, value):
        try:
            self.scale_factor = float(value)
            self.scale_label.config(text=f"Resize Scale: {self.scale_factor:.1f}")
            if self.cropped_picture is not None:
                self.update_picture_display()
        except ValueError:
               self.status_bar.config(text="Invalid scale value")


    # save cutted picture 
    def save_picture(self):
        if self.cropped_picture is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg *.jpeg"), ("All files", "*.*")])
            if file_path:
                try:
                    save_pic = cv2.cvtColor(self.cropped_picture, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(file_path, save_pic)
                    self.status_bar.config(text=f"Saved to {os.path.basename(file_path)}")
                except Exception as e:
                    self.status_bar.config(text=f"Save failed: {str(e)}")
        else:
            self.status_bar.config(text="Nothing to save")

# start the app
if __name__ == "__main__":
    window = tk.Tk()  
    app = PictureProcessorApp(window)  
    window.mainloop()


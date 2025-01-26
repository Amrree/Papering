import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from .base_frame import DraggableFrame

class ReadImageFrame(DraggableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, title="Read Image", *args, **kwargs)
        self.setup_read_panel()
    
    def setup_read_panel(self):
        # Content area with improved contrast
        content = tk.Frame(self, bg='#1e1e1e')
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create a frame for the drop zone
        self.drop_frame = tk.Frame(content, bg='#2d2d2d', relief='groove', bd=2)
        self.drop_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add drop zone label
        self.drop_label = tk.Label(self.drop_frame, 
                                 text="Drag and drop an image here",
                                 bg='#2d2d2d',
                                 fg='#ffffff',
                                 font=('Arial', 12))
        self.drop_label.pack(pady=20)
        
        # Add upload button
        upload_btn = ttk.Button(content, 
                              text="Upload Image", 
                              style='Retro.TButton',
                              command=self.upload_image)
        upload_btn.pack(pady=5)
        
        # Image preview area
        self.preview_frame = tk.Frame(content, bg='#1e1e1e')
        self.preview_frame.pack(fill='both', expand=True, pady=10)
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.display_image(file_path)
    
    def display_image(self, image_path):
        try:
            # Open and resize image to fit the preview area
            image = Image.open(image_path)
            # Calculate new size while maintaining aspect ratio
            display_size = (250, 250)  # Maximum display size
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for display
            photo = ImageTk.PhotoImage(image)
            
            # Create or update image label
            if hasattr(self, 'image_label'):
                self.image_label.configure(image=photo)
                self.image_label.image = photo
            else:
                self.image_label = tk.Label(self.preview_frame, image=photo, bg='#1e1e1e')
                self.image_label.image = photo
                self.image_label.pack(pady=5)
                
        except Exception as e:
            error_label = tk.Label(self.preview_frame, 
                                 text=f"Error loading image: {str(e)}", 
                                 fg='red',
                                 bg='#1e1e1e')
            error_label.pack(pady=5)
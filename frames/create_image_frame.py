import tkinter as tk
from tkinter import ttk
import requests
from .base_frame import DraggableFrame

class CreateImageFrame(DraggableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, title="Create Image", *args, **kwargs)
        self.setup_create_panel()
    
    def setup_create_panel(self):
        # Content area with improved contrast
        content = tk.Frame(self, bg='#1e1e1e')
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Image creation area with improved visibility
        self.prompt_entry = tk.Text(content, height=5, width=30,
                                   font=('Arial', 12),
                                   bg='#2d2d2d',
                                   fg='#ffffff',
                                   insertbackground='#ffffff',
                                   relief='sunken',
                                   padx=8,
                                   pady=8)
        self.prompt_entry.pack(pady=10)
        
        generate_btn = ttk.Button(content, text="Generate Image", style='Retro.TButton',
                                 command=self.generate_image)
        generate_btn.pack(pady=5)
    
    def generate_image(self):
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if prompt:
            try:
                response = requests.post('http://localhost:11434/api/generate',
                                       json={'model': 'lava', 'prompt': f"Generate an image of: {prompt}"})
                if response.status_code == 200:
                    response_data = response.json()
                    # Display the generated image description
                    result_text = tk.Text(self, height=5, width=30)
                    result_text.insert("1.0", response_data['response'])
                    result_text.pack(pady=5)
            except Exception as e:
                error_label = tk.Label(self, text=f"Error: {str(e)}", fg='red')
                error_label.pack(pady=5)
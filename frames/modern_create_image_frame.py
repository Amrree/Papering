import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import json
import threading
from datetime import datetime
import os
from PIL import Image, ImageTk
import base64
import io

class ModernCreateImageFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.generated_images = []
        self.current_image = None
        self.setup_create_panel()
        
    def setup_create_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(self.content_frame, text="AI Image Generator", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Prompt input area
        prompt_frame = ctk.CTkFrame(self.content_frame)
        prompt_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(prompt_frame, text="Image Prompt:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.prompt_entry = ctk.CTkTextbox(prompt_frame, 
                                         height=100,
                                         font=ctk.CTkFont(size=12),
                                         wrap="word",
                                         placeholder_text="Describe the image you want to create...")
        self.prompt_entry.pack(fill='x', padx=10, pady=(0, 10))
        
        # Style and settings frame
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(settings_frame, text="Settings:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Style selection
        style_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        style_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(style_frame, text="Style:").pack(side='left', padx=(0, 10))
        self.style_var = ctk.StringVar(value="realistic")
        self.style_menu = ctk.CTkOptionMenu(style_frame, 
                                          variable=self.style_var,
                                          values=["realistic", "cartoon", "anime", "painting", "sketch", "digital art"])
        self.style_menu.pack(side='left', padx=(0, 20))
        
        # Quality selection
        ctk.CTkLabel(style_frame, text="Quality:").pack(side='left', padx=(0, 10))
        self.quality_var = ctk.StringVar(value="high")
        self.quality_menu = ctk.CTkOptionMenu(style_frame, 
                                            variable=self.quality_var,
                                            values=["low", "medium", "high", "ultra"])
        self.quality_menu.pack(side='left')
        
        # Size selection
        size_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        size_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(size_frame, text="Size:").pack(side='left', padx=(0, 10))
        self.size_var = ctk.StringVar(value="1024x1024")
        self.size_menu = ctk.CTkOptionMenu(size_frame, 
                                         variable=self.size_var,
                                         values=["512x512", "768x768", "1024x1024", "1024x1792", "1792x1024"])
        self.size_menu.pack(side='left')
        
        # Generate button
        self.generate_btn = ctk.CTkButton(self.content_frame, 
                                        text="Generate Image", 
                                        command=self.generate_image,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        height=40)
        self.generate_btn.pack(fill='x', pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.content_frame)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide by default
        
        # Status label
        self.status_label = ctk.CTkLabel(self.content_frame, text="Ready to generate", 
                                       text_color="green")
        self.status_label.pack(pady=(0, 10))
        
        # Image preview area
        self.preview_frame = ctk.CTkFrame(self.content_frame)
        self.preview_frame.pack(fill='both', expand=True)
        
        ctk.CTkLabel(self.preview_frame, text="Generated Image:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Image display area
        self.image_display = ctk.CTkLabel(self.preview_frame, text="No image generated yet",
                                        font=ctk.CTkFont(size=12),
                                        text_color="gray")
        self.image_display.pack(expand=True, padx=10, pady=10)
        
        # Image action buttons
        self.action_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.action_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.save_btn = ctk.CTkButton(self.action_frame, text="Save Image", 
                                    command=self.save_image,
                                    width=100)
        self.save_btn.pack(side='left', padx=(0, 5))
        
        self.copy_btn = ctk.CTkButton(self.action_frame, text="Copy to Clipboard", 
                                    command=self.copy_image,
                                    width=120)
        self.copy_btn.pack(side='left', padx=(0, 5))
        
        self.regenerate_btn = ctk.CTkButton(self.action_frame, text="Regenerate", 
                                          command=self.regenerate_image,
                                          width=100)
        self.regenerate_btn.pack(side='left', padx=(0, 5))
        
        # History frame
        history_frame = ctk.CTkFrame(self.content_frame)
        history_frame.pack(fill='x', pady=(10, 0))
        
        ctk.CTkLabel(history_frame, text="Generation History:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.history_listbox = tk.Listbox(history_frame, height=4, 
                                        bg="#2b2b2b", fg="white",
                                        selectbackground="#1f538d")
        self.history_listbox.pack(fill='x', padx=10, pady=(0, 10))
        self.history_listbox.bind('<Double-Button-1>', self.load_history_item)
        
    def generate_image(self):
        """Generate image using AI"""
        prompt = self.prompt_entry.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showwarning("Warning", "Please enter a prompt")
            return
            
        # Show progress bar
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.start()
        self.status_label.configure(text="Generating image...", text_color="orange")
        self.generate_btn.configure(state="disabled")
        
        def generate():
            try:
                # Enhanced prompt with style and quality
                style = self.style_var.get()
                quality = self.quality_var.get()
                size = self.size_var.get()
                
                enhanced_prompt = f"{prompt}, {style} style, {quality} quality"
                
                # For now, we'll simulate image generation since we need a proper AI image service
                # In a real implementation, you'd use services like DALL-E, Midjourney, or Stable Diffusion
                self.simulate_image_generation(enhanced_prompt, size)
                
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Error: {str(e)}", text_color="red"))
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.generate_btn.configure(state="normal"))
                
        threading.Thread(target=generate, daemon=True).start()
        
    def simulate_image_generation(self, prompt, size):
        """Simulate image generation (replace with actual AI service)"""
        import time
        time.sleep(3)  # Simulate generation time
        
        # Create a placeholder image
        width, height = map(int, size.split('x'))
        placeholder = Image.new('RGB', (width, height), color='#2b2b2b')
        
        # Add some text to the placeholder
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(placeholder)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        text = f"Generated: {prompt[:50]}..."
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
        
        # Update UI in main thread
        self.after(0, lambda: self.display_generated_image(placeholder, prompt))
        
    def display_generated_image(self, image, prompt):
        """Display the generated image"""
        # Resize image for display
        display_size = (300, 300)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Update display
        self.image_display.configure(image=photo, text="")
        self.image_display.image = photo  # Keep a reference
        
        # Store the full-size image
        self.current_image = image
        
        # Add to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        history_item = f"{timestamp}: {prompt[:30]}..."
        self.history_listbox.insert(0, history_item)
        self.generated_images.insert(0, {
            'image': image,
            'prompt': prompt,
            'timestamp': timestamp
        })
        
        # Update status
        self.status_label.configure(text="Image generated successfully!", text_color="green")
        self.progress_bar.pack_forget()
        self.generate_btn.configure(state="normal")
        
    def save_image(self):
        """Save the current image to file"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                messagebox.showinfo("Success", f"Image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
                
    def copy_image(self):
        """Copy image to clipboard"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to copy")
            return
            
        try:
            # Convert image to base64 for clipboard
            buffer = io.BytesIO()
            self.current_image.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            
            # For now, just show a message (actual clipboard implementation would need more work)
            messagebox.showinfo("Info", "Image copied to clipboard (simulated)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy image: {str(e)}")
            
    def regenerate_image(self):
        """Regenerate the current image with the same prompt"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to regenerate")
            return
            
        # Get the last prompt from history
        if self.generated_images:
            last_prompt = self.generated_images[0]['prompt']
            self.prompt_entry.delete(1.0, tk.END)
            self.prompt_entry.insert(1.0, last_prompt)
            self.generate_image()
        else:
            messagebox.showwarning("Warning", "No previous prompt found")
            
    def load_history_item(self, event):
        """Load a history item when double-clicked"""
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.generated_images):
                item = self.generated_images[index]
                self.current_image = item['image']
                
                # Display the image
                display_size = (300, 300)
                image = item['image'].copy()
                image.thumbnail(display_size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.image_display.configure(image=photo, text="")
                self.image_display.image = photo
                
                # Update prompt
                self.prompt_entry.delete(1.0, tk.END)
                self.prompt_entry.insert(1.0, item['prompt'])
                
                self.status_label.configure(text=f"Loaded: {item['timestamp']}", text_color="blue")
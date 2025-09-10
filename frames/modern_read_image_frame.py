import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import requests
import json
import threading
from datetime import datetime
import os
import base64
import io

class ModernReadImageFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.current_image = None
        self.current_image_path = None
        self.analysis_results = []
        self.setup_read_panel()
        
    def setup_read_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(self.content_frame, text="AI Image Analyzer", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Upload section
        upload_frame = ctk.CTkFrame(self.content_frame)
        upload_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(upload_frame, text="Upload Image:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Upload buttons
        button_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.upload_btn = ctk.CTkButton(button_frame, text="Choose File", 
                                      command=self.upload_image,
                                      width=120)
        self.upload_btn.pack(side='left', padx=(0, 10))
        
        self.drag_drop_btn = ctk.CTkButton(button_frame, text="Drag & Drop Area", 
                                         command=self.show_drag_drop_info,
                                         width=120)
        self.drag_drop_btn.pack(side='left', padx=(0, 10))
        
        # File info
        self.file_info_label = ctk.CTkLabel(button_frame, text="No file selected", 
                                          text_color="gray")
        self.file_info_label.pack(side='right')
        
        # Image preview area
        self.preview_frame = ctk.CTkFrame(self.content_frame)
        self.preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        ctk.CTkLabel(self.preview_frame, text="Image Preview:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Image display
        self.image_display = ctk.CTkLabel(self.preview_frame, 
                                        text="Drag and drop an image here\nor click 'Choose File'",
                                        font=ctk.CTkFont(size=12),
                                        text_color="gray")
        self.image_display.pack(expand=True, padx=10, pady=10)
        
        # Image controls
        self.control_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.control_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.analyze_btn = ctk.CTkButton(self.control_frame, text="Analyze Image", 
                                       command=self.analyze_image,
                                       width=120)
        self.analyze_btn.pack(side='left', padx=(0, 10))
        
        self.rotate_btn = ctk.CTkButton(self.control_frame, text="Rotate", 
                                      command=self.rotate_image,
                                      width=80)
        self.rotate_btn.pack(side='left', padx=(0, 10))
        
        self.enhance_btn = ctk.CTkButton(self.control_frame, text="Enhance", 
                                       command=self.enhance_image,
                                       width=80)
        self.enhance_btn.pack(side='left', padx=(0, 10))
        
        self.save_btn = ctk.CTkButton(self.control_frame, text="Save", 
                                    command=self.save_image,
                                    width=80)
        self.save_btn.pack(side='left', padx=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.content_frame)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide by default
        
        # Status label
        self.status_label = ctk.CTkLabel(self.content_frame, text="Ready to analyze", 
                                       text_color="green")
        self.status_label.pack(pady=(0, 10))
        
        # Analysis results area
        results_frame = ctk.CTkFrame(self.content_frame)
        results_frame.pack(fill='both', expand=True)
        
        ctk.CTkLabel(results_frame, text="Analysis Results:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Results text area
        self.results_text = ctk.CTkTextbox(results_frame, 
                                         height=150,
                                         font=ctk.CTkFont(size=12))
        self.results_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Results actions
        results_actions = ctk.CTkFrame(results_frame, fg_color="transparent")
        results_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        self.copy_results_btn = ctk.CTkButton(results_actions, text="Copy Results", 
                                            command=self.copy_results,
                                            width=120)
        self.copy_results_btn.pack(side='left', padx=(0, 10))
        
        self.export_results_btn = ctk.CTkButton(results_actions, text="Export Results", 
                                              command=self.export_results,
                                              width=120)
        self.export_results_btn.pack(side='left', padx=(0, 10))
        
        self.clear_results_btn = ctk.CTkButton(results_actions, text="Clear", 
                                             command=self.clear_results,
                                             width=80)
        self.clear_results_btn.pack(side='left', padx=(0, 10))
        
        # Enable drag and drop
        self.setup_drag_drop()
        
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.image_display.bind('<Button-1>', self.upload_image)
        
        # Bind drag and drop events
        self.image_display.bind('<B1-Motion>', self.on_drag)
        self.image_display.bind('<ButtonRelease-1>', self.on_drop)
        
    def on_drag(self, event):
        """Handle drag events"""
        pass  # Could implement drag functionality here
        
    def on_drop(self, event):
        """Handle drop events"""
        pass  # Could implement drop functionality here
        
    def show_drag_drop_info(self):
        """Show information about drag and drop"""
        messagebox.showinfo("Drag & Drop", 
                          "You can drag and drop image files directly onto the preview area.\n\n"
                          "Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF")
        
    def upload_image(self):
        """Upload image from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, file_path):
        """Load and display image"""
        try:
            # Open and process image
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            self.current_image = image
            self.current_image_path = file_path
            
            # Update file info
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            self.file_info_label.configure(text=f"{file_name} ({size_mb:.1f} MB)")
            
            # Display image
            self.display_image(image)
            
            # Enable analyze button
            self.analyze_btn.configure(state="normal")
            self.status_label.configure(text="Image loaded successfully", text_color="green")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.status_label.configure(text="Failed to load image", text_color="red")
            
    def display_image(self, image):
        """Display image in the preview area"""
        # Calculate display size (max 400x400)
        max_size = 400
        width, height = image.size
        
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * max_size / width)
            else:
                new_height = max_size
                new_width = int(width * max_size / height)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Update display
        self.image_display.configure(image=photo, text="")
        self.image_display.image = photo  # Keep a reference
        
    def analyze_image(self):
        """Analyze image using AI"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load an image first")
            return
            
        # Show progress bar
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.start()
        self.status_label.configure(text="Analyzing image...", text_color="orange")
        self.analyze_btn.configure(state="disabled")
        
        def analyze():
            try:
                # Convert image to base64 for API
                buffer = io.BytesIO()
                self.current_image.save(buffer, format='PNG')
                img_data = buffer.getvalue()
                img_base64 = base64.b64encode(img_data).decode()
                
                # Prepare prompt for image analysis
                prompt = ("Analyze this image in detail. Describe what you see, including objects, people, "
                         "text, colors, composition, mood, and any other relevant details. "
                         "If there's text in the image, transcribe it. "
                         "Provide a comprehensive analysis suitable for a book writing context.")
                
                # Make request to Ollama with image
                response = requests.post('http://localhost:11434/api/generate',
                                       json={
                                           'model': 'llava',
                                           'prompt': prompt,
                                           'images': [img_base64],
                                           'stream': False
                                       },
                                       timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_text = result.get('response', 'No analysis available')
                    
                    # Update UI in main thread
                    self.after(0, lambda: self.display_analysis(analysis_text))
                else:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"Analysis failed: {response.status_code}", text_color="red"))
                    
            except requests.exceptions.ConnectionError:
                self.after(0, lambda: self.status_label.configure(
                    text="Error: Could not connect to AI server", text_color="red"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.status_label.configure(
                    text="Error: Analysis timed out", text_color="red"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=f"Error: {str(e)}", text_color="red"))
            finally:
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.analyze_btn.configure(state="normal"))
                
        threading.Thread(target=analyze, daemon=True).start()
        
    def display_analysis(self, analysis_text):
        """Display analysis results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the analysis
        formatted_analysis = f"=== Image Analysis - {timestamp} ===\n\n{analysis_text}\n\n"
        
        # Add to results
        self.results_text.insert(tk.END, formatted_analysis)
        self.results_text.see(tk.END)
        
        # Store in history
        self.analysis_results.append({
            'timestamp': timestamp,
            'analysis': analysis_text,
            'image_path': self.current_image_path
        })
        
        self.status_label.configure(text="Analysis completed", text_color="green")
        
    def rotate_image(self):
        """Rotate the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to rotate")
            return
            
        try:
            self.current_image = self.current_image.rotate(90, expand=True)
            self.display_image(self.current_image)
            self.status_label.configure(text="Image rotated", text_color="blue")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate image: {str(e)}")
            
    def enhance_image(self):
        """Enhance the current image"""
        if not self.current_image:
            messagebox.showwarning("Warning", "No image to enhance")
            return
            
        try:
            # Apply some basic enhancements
            enhanced = ImageOps.autocontrast(self.current_image)
            enhanced = ImageOps.sharpness(enhanced)
            
            self.current_image = enhanced
            self.display_image(self.current_image)
            self.status_label.configure(text="Image enhanced", text_color="blue")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enhance image: {str(e)}")
            
    def save_image(self):
        """Save the current image"""
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
                
    def copy_results(self):
        """Copy analysis results to clipboard"""
        results = self.results_text.get("1.0", tk.END).strip()
        if results:
            self.clipboard_clear()
            self.clipboard_append(results)
            messagebox.showinfo("Success", "Results copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No results to copy")
            
    def export_results(self):
        """Export analysis results to file"""
        if not self.analysis_results:
            messagebox.showwarning("Warning", "No results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Analysis Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # Export as JSON
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
                else:
                    # Export as text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Image Analysis Results\n")
                        f.write("=" * 50 + "\n\n")
                        for result in self.analysis_results:
                            f.write(f"Timestamp: {result['timestamp']}\n")
                            f.write(f"Image: {result['image_path']}\n")
                            f.write(f"Analysis: {result['analysis']}\n")
                            f.write("-" * 30 + "\n\n")
                            
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
                
    def clear_results(self):
        """Clear analysis results"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all results?"):
            self.results_text.delete("1.0", tk.END)
            self.analysis_results = []
            self.status_label.configure(text="Results cleared", text_color="blue")
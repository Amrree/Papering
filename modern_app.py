import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime
from PIL import Image, ImageTk
import requests
import threading
import webbrowser
from export_utils import ProjectExporter

# Import our custom frames
from frames.modern_chat_frame import ModernChatFrame
from frames.modern_create_image_frame import ModernCreateImageFrame
from frames.modern_read_image_frame import ModernReadImageFrame
from frames.characters_frame import CharactersFrame
from frames.scenes_frame import ScenesFrame
from frames.outline_frame import OutlineFrame

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernDraggableFrame(ctk.CTkFrame):
    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title = title
        self.configure(fg_color=("gray90", "gray13"))
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self, height=30)
        self.title_bar.pack(fill='x', padx=2, pady=2)
        self.title_bar.pack_propagate(False)
        
        # Title label
        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=ctk.CTkFont(size=12, weight="bold"))
        self.title_label.pack(side='left', padx=10, pady=5)
        
        # Window control buttons
        control_frame = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        control_frame.pack(side='right', padx=5)
        
        # Minimize button
        self.min_button = ctk.CTkButton(control_frame, text='_', command=self.minimize,
                                      width=20, height=20, font=ctk.CTkFont(size=10))
        self.min_button.pack(side='left', padx=1)
        
        # Maximize button
        self.max_button = ctk.CTkButton(control_frame, text='□', command=self.maximize,
                                      width=20, height=20, font=ctk.CTkFont(size=10))
        self.max_button.pack(side='left', padx=1)
        
        # Close button
        self.close_button = ctk.CTkButton(control_frame, text='×', command=self.close,
                                       width=20, height=20, font=ctk.CTkFont(size=10),
                                       fg_color="red", hover_color="darkred")
        self.close_button.pack(side='left', padx=1)
        
        # Bind mouse events for dragging
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.drag)
        self.title_label.bind('<Button-1>', self.start_drag)
        self.title_label.bind('<B1-Motion>', self.drag)
        
        # Initialize drag variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        
    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def drag(self, event):
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
        
    def minimize(self):
        self.place_forget()
        
    def maximize(self):
        if hasattr(self, '_restore_info'):
            # Restore previous size and position
            x, y, w, h = self._restore_info
            self.place(x=x, y=y, width=w, height=h)
            delattr(self, '_restore_info')
        else:
            # Store current size and position
            self._restore_info = (self.winfo_x(), self.winfo_y(),
                                self.winfo_width(), self.winfo_height())
            # Maximize
            self.place(x=0, y=0,
                      width=self.master.winfo_width(),
                      height=self.master.winfo_height())
            
    def close(self):
        window_name = self.title
        if hasattr(self.master, 'window_states') and window_name in self.master.window_states:
            self.master.window_states[window_name].set(False)
            self.master.toggle_window(window_name)

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("AI Book Studio - Modern Edition")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.panel_positions = {}
        self.window_states = {}
        self.current_project = None
        self.projects = {}
        self.exporter = ProjectExporter()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main area
        self.create_main_area()
        
        # Create status bar
        self.create_status_bar()
        
        # Load saved layout
        self.load_layout()
        
    def create_sidebar(self):
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo/Title
        title_label = ctk.CTkLabel(self.sidebar, text="AI Book Studio", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)
        
        # Project section
        project_frame = ctk.CTkFrame(self.sidebar)
        project_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(project_frame, text="Projects", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.new_project_btn = ctk.CTkButton(project_frame, text="New Project", 
                                           command=self.new_project)
        self.new_project_btn.pack(fill="x", padx=10, pady=5)
        
        self.open_project_btn = ctk.CTkButton(project_frame, text="Open Project", 
                                            command=self.open_project)
        self.open_project_btn.pack(fill="x", padx=10, pady=5)
        
        # Tools section
        tools_frame = ctk.CTkFrame(self.sidebar)
        tools_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(tools_frame, text="AI Tools", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # AI Chat button
        self.chat_btn = ctk.CTkButton(tools_frame, text="AI Chat", 
                                    command=lambda: self.toggle_window("Chat"))
        self.chat_btn.pack(fill="x", padx=10, pady=2)
        
        # Image Creation button
        self.create_image_btn = ctk.CTkButton(tools_frame, text="Create Image", 
                                            command=lambda: self.toggle_window("Create Image"))
        self.create_image_btn.pack(fill="x", padx=10, pady=2)
        
        # Image Reading button
        self.read_image_btn = ctk.CTkButton(tools_frame, text="Read Image", 
                                          command=lambda: self.toggle_window("Read Image"))
        self.read_image_btn.pack(fill="x", padx=10, pady=2)
        
        # Writing Tools section
        writing_frame = ctk.CTkFrame(self.sidebar)
        writing_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(writing_frame, text="Writing Tools", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.characters_btn = ctk.CTkButton(writing_frame, text="Characters", 
                                          command=lambda: self.toggle_window("Characters"))
        self.characters_btn.pack(fill="x", padx=10, pady=2)
        
        self.scenes_btn = ctk.CTkButton(writing_frame, text="Scenes", 
                                      command=lambda: self.toggle_window("Scenes"))
        self.scenes_btn.pack(fill="x", padx=10, pady=2)
        
        self.outline_btn = ctk.CTkButton(writing_frame, text="Outline", 
                                       command=lambda: self.toggle_window("Outline"))
        self.outline_btn.pack(fill="x", padx=10, pady=2)
        
        # Export section
        export_frame = ctk.CTkFrame(self.sidebar)
        export_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(export_frame, text="Export", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.export_pdf_btn = ctk.CTkButton(export_frame, text="Export PDF", 
                                          command=self.export_pdf)
        self.export_pdf_btn.pack(fill="x", padx=10, pady=2)
        
        self.export_epub_btn = ctk.CTkButton(export_frame, text="Export EPUB", 
                                           command=self.export_epub)
        self.export_epub_btn.pack(fill="x", padx=10, pady=2)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(self.sidebar, text="Settings", 
                                        command=self.open_settings)
        self.settings_btn.pack(side="bottom", padx=10, pady=10)
        
    def create_main_area(self):
        # Main content area
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Create the three main panels
        self.create_panels()
        
    def create_panels(self):
        # Create panels with modern styling
        panel_width = 400
        panel_height = 600
        panel_padding = 20
        
        # Calculate starting positions
        start_x = 50
        start_y = 50
        
        # Create Chat panel
        self.chat_window = self.create_panel("Chat", start_x, start_y, panel_width, panel_height)
        
        # Create Image Creation panel
        self.create_window = self.create_panel("Create Image", 
                                             start_x + panel_width + panel_padding, 
                                             start_y, panel_width, panel_height)
        
        # Create Image Reading panel
        self.read_window = self.create_panel("Read Image", 
                                           start_x + (panel_width + panel_padding) * 2, 
                                           start_y, panel_width, panel_height)
        
        # Create additional panels (initially hidden)
        self.characters_window = self.create_panel("Characters", 
                                                 start_x, start_y + panel_height + panel_padding, 
                                                 panel_width, panel_height)
        self.characters_window.place_forget()
        
        self.scenes_window = self.create_panel("Scenes", 
                                             start_x + panel_width + panel_padding, 
                                             start_y + panel_height + panel_padding, 
                                             panel_width, panel_height)
        self.scenes_window.place_forget()
        
        self.outline_window = self.create_panel("Outline", 
                                              start_x + (panel_width + panel_padding) * 2, 
                                              start_y + panel_height + panel_padding, 
                                              panel_width, panel_height)
        self.outline_window.place_forget()
        
        # Initialize window states
        for window_name in ["Chat", "Create Image", "Read Image", "Characters", "Scenes", "Outline"]:
            self.window_states[window_name] = tk.BooleanVar(value=True)
            
    def create_panel(self, title, x, y, width, height):
        if title == "Chat":
            panel = ModernChatFrame(self.main_frame)
        elif title == "Create Image":
            panel = ModernCreateImageFrame(self.main_frame)
        elif title == "Read Image":
            panel = ModernReadImageFrame(self.main_frame)
        elif title == "Characters":
            panel = CharactersFrame(self.main_frame)
        elif title == "Scenes":
            panel = ScenesFrame(self.main_frame)
        elif title == "Outline":
            panel = OutlineFrame(self.main_frame)
        else:
            panel = ctk.CTkFrame(self.main_frame)
            
        panel.place(x=x, y=y, width=width, height=height)
        return panel
        
    def create_status_bar(self):
        # Status bar
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # AI Status indicator
        self.ai_status_label = ctk.CTkLabel(self.status_bar, text="AI: Offline", 
                                          text_color="red")
        self.ai_status_label.pack(side="right", padx=10, pady=5)
        
    def toggle_window(self, window_name):
        is_visible = self.window_states.get(window_name, tk.BooleanVar(value=True)).get()
        window = getattr(self, window_name.lower().replace(" ", "_") + "_window", None)
        
        if window:
            if is_visible:
                window.place(x=window.winfo_x(), y=window.winfo_y())
            else:
                window.place_forget()
                
    def new_project(self):
        # Create new project dialog
        dialog = ctk.CTkInputDialog(text="Enter project name:", title="New Project")
        project_name = dialog.get_input()
        
        if project_name:
            self.current_project = project_name
            self.projects[project_name] = {
                "created": datetime.now().isoformat(),
                "chapters": [],
                "characters": [],
                "scenes": []
            }
            self.status_label.configure(text=f"Project: {project_name}")
            
    def open_project(self):
        # Open project file dialog
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    project_data = json.load(f)
                self.current_project = project_data.get("name", "Unknown")
                self.projects[self.current_project] = project_data
                self.status_label.configure(text=f"Project: {self.current_project}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open project: {str(e)}")
                
    def export_pdf(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            project_data = self.collect_project_data()
            if self.exporter.export_project(project_data, 'pdf', file_path):
                messagebox.showinfo("Success", f"Project exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export project")
            
    def export_epub(self):
        if not self.current_project:
            messagebox.showwarning("Warning", "No project selected")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export EPUB",
            defaultextension=".epub",
            filetypes=[("EPUB files", "*.epub")]
        )
        
        if file_path:
            project_data = self.collect_project_data()
            if self.exporter.export_project(project_data, 'epub', file_path):
                messagebox.showinfo("Success", f"Project exported to {file_path}")
            else:
                messagebox.showerror("Error", "Failed to export project")
                
    def collect_project_data(self):
        """Collect all project data from the various frames"""
        project_data = {
            'project_info': {
                'name': self.current_project,
                'created': datetime.now().isoformat(),
                'description': 'AI Book Studio Project'
            }
        }
        
        # Collect characters
        if hasattr(self, 'characters_window'):
            project_data['characters'] = self.characters_window.get_characters()
        
        # Collect chapters
        if hasattr(self, 'outline_window'):
            project_data['chapters'] = self.outline_window.get_chapters()
        
        # Collect scenes
        if hasattr(self, 'scenes_window'):
            project_data['scenes'] = self.scenes_window.get_scenes()
        
        return project_data
            
    def open_settings(self):
        # Create settings window
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # AI Settings
        ai_frame = ctk.CTkFrame(settings_window)
        ai_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(ai_frame, text="AI Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Ollama URL
        ctk.CTkLabel(ai_frame, text="Ollama Server URL:").pack(pady=5)
        self.ollama_url_entry = ctk.CTkEntry(ai_frame, placeholder_text="http://localhost:11434")
        self.ollama_url_entry.pack(fill="x", padx=10, pady=5)
        
        # Model selection
        ctk.CTkLabel(ai_frame, text="AI Model:").pack(pady=5)
        self.model_var = ctk.StringVar(value="llava")
        model_menu = ctk.CTkOptionMenu(ai_frame, variable=self.model_var,
                                     values=["llava", "llama2", "codellama", "mistral"])
        model_menu.pack(fill="x", padx=10, pady=5)
        
        # Save settings button
        save_btn = ctk.CTkButton(settings_window, text="Save Settings", 
                               command=lambda: self.save_settings(settings_window))
        save_btn.pack(pady=20)
        
    def save_settings(self, window):
        # TODO: Implement settings saving
        messagebox.showinfo("Info", "Settings saved!")
        window.destroy()
        
    def save_layout(self):
        # Save current panel positions
        for panel_name, panel in {
            "Chat": self.chat_window,
            "Create Image": self.create_window,
            "Read Image": self.read_window
        }.items():
            self.panel_positions[panel_name] = {
                "x": panel.winfo_x(),
                "y": panel.winfo_y(),
                "width": panel.winfo_width(),
                "height": panel.winfo_height()
            }
        
        # Save to file
        with open("layout.json", "w") as f:
            json.dump(self.panel_positions, f, indent=2)
            
    def load_layout(self):
        try:
            with open("layout.json", "r") as f:
                saved_positions = json.load(f)
                
            # Restore panel positions
            for panel_name, pos in saved_positions.items():
                if panel_name == "Chat":
                    self.chat_window.place(x=pos["x"], y=pos["y"], 
                                         width=pos.get("width", 350), 
                                         height=pos.get("height", 500))
                elif panel_name == "Create Image":
                    self.create_window.place(x=pos["x"], y=pos["y"],
                                           width=pos.get("width", 350), 
                                           height=pos.get("height", 500))
                elif panel_name == "Read Image":
                    self.read_window.place(x=pos["x"], y=pos["y"],
                                         width=pos.get("width", 350), 
                                         height=pos.get("height", 500))
        except FileNotFoundError:
            pass  # Use default layout if no saved layout exists

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
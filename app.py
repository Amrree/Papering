import tkinter as tk
from tkinter import ttk
import json
from PIL import Image, ImageTk
import requests
from frames.chat_frame import ChatFrame
from frames.create_image_frame import CreateImageFrame
from frames.read_image_frame import ReadImageFrame

class DraggableFrame(tk.Frame):
    def __init__(self, parent, title="", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.title = title
        
        # Configure frame styling
        self.configure(bg='#f0f0f0', relief='raised', borderwidth=2)
        
        # Title bar
        self.title_bar = tk.Frame(self, bg='#c0c0c0', relief='raised', borderwidth=1)
        self.title_bar.pack(fill='x')
        
        # Title label
        tk.Label(self.title_bar, text=title, bg='#c0c0c0', fg='black').pack(side='left', padx=5)
        
        # Window control buttons
        control_frame = tk.Frame(self.title_bar, bg='#c0c0c0')
        control_frame.pack(side='right', padx=2)
        
        # Minimize button
        self.min_button = tk.Button(control_frame, text='_', command=self.minimize,
                                  width=2, bg='#d4d0c8', relief='raised')
        self.min_button.pack(side='left', padx=1)
        
        # Maximize button
        self.max_button = tk.Button(control_frame, text='□', command=self.maximize,
                                  width=2, bg='#d4d0c8', relief='raised')
        self.max_button.pack(side='left', padx=1)
        
        # Close button
        self.close_button = tk.Button(control_frame, text='×', command=self.close,
                                   width=2, bg='#d4d0c8', relief='raised')
        self.close_button.pack(side='left', padx=1)
        
        # Bind mouse events for dragging
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.drag)
        
        # Create resize handles
        self.resize_handle = tk.Frame(self, width=10, height=10, bg='#808080', cursor='sizing')
        self.resize_handle.place(relx=1.0, rely=1.0, anchor='se')
        
        # Bind resize events
        self.resize_handle.bind('<Button-1>', self.start_resize)
        self.resize_handle.bind('<B1-Motion>', self.resize)
        
        # Initialize drag and resize variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._initial_width = 0
        self._initial_height = 0
        
    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def drag(self, event):
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
        
    def start_resize(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._initial_width = self.winfo_width()
        self._initial_height = self.winfo_height()
        
    def resize(self, event):
        width_diff = event.x_root - self._resize_start_x
        height_diff = event.y_root - self._resize_start_y
        
        new_width = max(200, self._initial_width + width_diff)  # Minimum width of 200
        new_height = max(200, self._initial_height + height_diff)  # Minimum height of 200
        
        self.place(width=new_width, height=new_height)

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
        
        # Bind mouse events for dragging
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.drag)
        
        # Create resize handles
        self.resize_handle = tk.Frame(self, width=10, height=10, bg='#808080', cursor='sizing')
        self.resize_handle.place(relx=1.0, rely=1.0, anchor='se')
        
        # Bind resize events
        self.resize_handle.bind('<Button-1>', self.start_resize)
        self.resize_handle.bind('<B1-Motion>', self.resize)
        
        # Initialize drag and resize variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._resize_start_x = 0
        self._resize_start_y = 0
        self._initial_width = 0
        self._initial_height = 0
        
    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        
    def drag(self, event):
        x = self.winfo_x() - self._drag_start_x + event.x
        y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=x, y=y)
        
    def start_resize(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_y = event.y_root
        self._initial_width = self.winfo_width()
        self._initial_height = self.winfo_height()
        
    def resize(self, event):
        width_diff = event.x_root - self._resize_start_x
        height_diff = event.y_root - self._resize_start_y
        
        new_width = max(200, self._initial_width + width_diff)  # Minimum width of 200
        new_height = max(200, self._initial_height + height_diff)  # Minimum height of 200
        
        self.place(width=new_width, height=new_height)

class RetroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("AI Book Studio")
        self.geometry("1024x768")
        self.configure(bg='#1e1e1e')  # Darker background for better contrast
        
        # Create main container
        self.main_container = tk.Frame(self, bg='#1e1e1e')
        self.main_container.pack(fill='both', expand=True)
        
        # Initialize panel positions dictionary
        self.panel_positions = {}
        
        # Add menu bar for layout management
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        
        # Create Layout menu
        layout_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Layout", menu=layout_menu)
        layout_menu.add_command(label="Save Layout", command=self.save_layout)
        layout_menu.add_command(label="Load Layout", command=self.load_layout)
        
        # Create View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Add window controls to View menu
        view_menu.add_command(label="Show All Windows", command=self.show_all_windows)
        view_menu.add_command(label="Hide All Windows", command=self.hide_all_windows)
        view_menu.add_separator()
        
        # Add individual window toggles
        self.window_states = {}
        for window_name in ["Chat", "Create Image", "Read Image"]:
            self.window_states[window_name] = tk.BooleanVar(value=True)
            view_menu.add_checkbutton(
                label=window_name,
                variable=self.window_states[window_name],
                command=lambda name=window_name: self.toggle_window(name)
            )
        
        # Create View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Add window controls to View menu
        view_menu.add_command(label="Show All Windows", command=self.show_all_windows)
        view_menu.add_command(label="Hide All Windows", command=self.hide_all_windows)
        view_menu.add_separator()
        
        # Add individual window toggles
        self.window_states = {}
        for window_name in ["Chat", "Create Image", "Read Image"]:
            self.window_states[window_name] = tk.BooleanVar(value=True)
            view_menu.add_checkbutton(
                label=window_name,
                variable=self.window_states[window_name],
                command=lambda name=window_name: self.toggle_window(name)
            )
        
        # Create top bar with improved styling
        self.top_bar = tk.Frame(self.main_container, bg='#1e1e1e', height=50)
        self.top_bar.pack(fill='x', pady=(0, 5))
        
        # Add Canvas button with improved styling
        self.canvas_btn = tk.Button(self.top_bar, text="Canvas", 
                                  bg='#2d2d2d', fg='#ffffff',
                                  activebackground='#3d3d3d',
                                  activeforeground='#ffffff',
                                  font=('Arial', 14, 'bold'),
                                  relief='flat',
                                  padx=15,
                                  pady=8)
        self.canvas_btn.pack(side='left', padx=10, pady=8)
        
        # Create tab buttons
        tab_buttons = [
            "Read Image",
            "Create Image",
            "Generate Story",
            "Characters",
            "Scenes",
            "Layout"
        ]
        
        for tab_text in tab_buttons:
            tab_btn = tk.Button(self.top_bar, text=tab_text,
                              bg='#2d2d2d', fg='#ffffff',
                              activebackground='#3d3d3d',
                              activeforeground='#ffffff',
                              font=('Arial', 14, 'bold'),
                              relief='flat',
                              padx=15,
                              pady=8)
            tab_btn.pack(side='left', padx=5, pady=8)
        
        # Create sidebar with improved styling
        self.sidebar = tk.Frame(self.main_container, bg='#2d2d2d', width=200)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # Create sidebar buttons
        buttons = [
            "AI Writer",
            "Generate Image",
            "Read Image",
            "Characters",
            "Scenes",
            "Layout",
            "Export",
            "Settings"
        ]
        
        # Update button styling for better visibility
        for button_text in buttons:
            btn = tk.Button(self.sidebar, text=button_text,
                          bg='#d4d0c8',  # Lighter background
                          fg='#000000',  # Black text for maximum contrast
                          activebackground='#c0c0c0',
                          activeforeground='#000000',
                          font=('Arial', 12, 'bold'),
                          width=15,
                          relief='raised',
                          pady=10)
            btn.pack(pady=5, padx=10)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Retro.TButton',
                            padding=6,
                            relief='raised',
                            background='#d4d0c8',
                            foreground='#000000',  # Darker text for better contrast
                            font=('Arial', 12, 'bold'))
        
        # Create the three main panels with improved positioning and styling
        panel_width = 300
        panel_height = 400
        panel_padding = 20
        start_x = (self.winfo_screenwidth() - (panel_width * 3 + panel_padding * 2)) // 2
        start_y = 100  # Give some space from the top bar

        self.chat_window = self.create_panel("Chat", start_x, start_y)
        self.create_window = self.create_panel("Create Image", start_x + panel_width + panel_padding, start_y)
        self.read_window = self.create_panel("Read Image", start_x + (panel_width + panel_padding) * 2, start_y)

        # Update text styling for better visibility
        self.style = ttk.Style()
        self.style.configure('Retro.TButton',
                            padding=6,
                            relief='raised',
                            background='#d4d0c8',
                            font=('Arial', 12))
        
    def create_panel(self, title, x, y):
        if title == "Chat":
            panel = ChatFrame(self)
        elif title == "Create Image":
            panel = CreateImageFrame(self)
        else:
            panel = ReadImageFrame(self)
            
        panel.place(x=x, y=y, width=300, height=400)
        return panel
        
    def save_layout(self):
        # Save current panel positions
        for panel_name, panel in {
            "Chat": self.chat_window,
            "Create Image": self.create_window,
            "Read Image": self.read_window
        }.items():
            self.panel_positions[panel_name] = {
                "x": panel.winfo_x(),
                "y": panel.winfo_y()
            }
        
        # Save to file
        with open("layout.json", "w") as f:
            json.dump(self.panel_positions, f)
            
    def load_layout(self):
        try:
            with open("layout.json", "r") as f:
                saved_positions = json.load(f)
                
            # Restore panel positions
            for panel_name, pos in saved_positions.items():
                if panel_name == "Chat":
                    self.chat_window.place(x=pos["x"], y=pos["y"])
                elif panel_name == "Create Image":
                    self.create_window.place(x=pos["x"], y=pos["y"])
                elif panel_name == "Read Image":
                    self.read_window.place(x=pos["x"], y=pos["y"])
        except FileNotFoundError:
            pass  # Use default layout if no saved layout exists

    def show_all_windows(self):
        for window_name in self.window_states:
            self.window_states[window_name].set(True)
            self.toggle_window(window_name)
    
    def hide_all_windows(self):
        for window_name in self.window_states:
            self.window_states[window_name].set(False)
            self.toggle_window(window_name)
    
    def show_all_windows(self):
        for window_name in self.window_states:
            self.window_states[window_name].set(True)
            self.toggle_window(window_name)
    
    def hide_all_windows(self):
        for window_name in self.window_states:
            self.window_states[window_name].set(False)
            self.toggle_window(window_name)
    
    def toggle_window(self, window_name):
        is_visible = self.window_states[window_name].get()
        window = getattr(self, window_name.lower().replace(" ", "_") + "_window")
        if is_visible:
            window.place(x=window.winfo_x(), y=window.winfo_y())
        else:
            window.place_forget()

if __name__ == "__main__":
    app = RetroApp()
    app.mainloop()
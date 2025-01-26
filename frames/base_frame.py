import tkinter as tk

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
import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frames.chat_frame import ChatFrame

class TestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Chat Frame Test")
        self.geometry("400x600")
        self.configure(bg='#1e1e1e')
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('Retro.TButton',
                            padding=6,
                            relief='raised',
                            background='#d4d0c8',
                            foreground='#000000',
                            font=('Arial', 12, 'bold'))
        
        # Create and position the chat frame
        self.chat_frame = ChatFrame(self)
        self.chat_frame.place(x=50, y=50, width=300, height=400)

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
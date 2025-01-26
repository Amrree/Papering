import tkinter as tk
from tkinter import ttk
import requests
from .base_frame import DraggableFrame

class ChatFrame(DraggableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, title="Chat", *args, **kwargs)
        self.setup_chat_panel()
    
    def setup_chat_panel(self):
        # Content area with improved contrast
        content = tk.Frame(self, bg='#1e1e1e')
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Chat input area with improved visibility
        self.chat_text = tk.Text(content, height=15, width=30, 
                                font=('Arial', 12),
                                bg='#2d2d2d',
                                fg='#ffffff',
                                insertbackground='#ffffff',
                                relief='sunken',
                                padx=8,
                                pady=8)
        self.chat_text.pack(pady=10)
        
        send_btn = ttk.Button(content, text="Send", style='Retro.TButton',
                             command=self.send_chat)
        send_btn.pack(pady=5)
    
    def send_chat(self):
        text = self.chat_text.get("1.0", tk.END).strip()
        if text:
            try:
                response = requests.post('http://localhost:11434/api/generate',
                                       json={'model': 'lava', 'prompt': text})
                if response.status_code == 200:
                    response_data = response.json()
                    self.chat_text.insert(tk.END, f"\n\nAI: {response_data['response']}\n")
            except Exception as e:
                self.chat_text.insert(tk.END, f"\n\nError: Could not connect to Ollama server: {str(e)}\n")
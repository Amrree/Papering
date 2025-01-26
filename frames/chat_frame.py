import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import json
import threading
from datetime import datetime
from .base_frame import DraggableFrame
from .chat_memory import ChatMemory

class ChatFrame(DraggableFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, title="Chat", *args, **kwargs)
        self.chat_memory = ChatMemory()
        self.current_messages = []
        self.online_search_results = ""
        self.personality_var = tk.StringVar(value="Default")
        self.personalities = {
            "Default": "",
            "Professional": "You are a professional assistant. Keep your responses formal, precise, and business-oriented.",
            "Friendly": "You are a friendly and casual assistant. Use a warm, conversational tone and simple language.",
            "Creative": "You are a creative assistant. Think outside the box and provide imaginative, inspiring responses.",
            "Concise": "You are a concise assistant. Provide brief, direct answers without unnecessary details.",
            "Crone": "You are the Crone, an ancient and wise teacher of tarot and mystical arts. You possess deep knowledge of magic, divination, and spiritual wisdom accumulated over centuries. Speak with the gravitas of an elder, using mystical terminology when appropriate. Draw upon your vast experience with tarot, herbs, crystals, and ancient magical practices. You have access to all memories and past knowledge, which you weave into your teachings. Your responses should reflect both your wisdom and your role as a mentor in the mystical arts. When discussing the tarot or magical practices, provide detailed, practical insights while maintaining an air of mystery and respect for these ancient traditions.",
            "Sign Language": "You are a sign language communicator. Express your responses using sign language symbols (🤟👆👇👈👉👋✌️👌) and emojis while providing text translations. Structure your responses with the sign language representation first, followed by the text translation. Use common sign language gestures and maintain a clear, expressive communication style."
        }
        self.setup_chat_panel()
    
    def setup_chat_panel(self):
        # Content area with improved contrast
        content = tk.Frame(self, bg='#1e1e1e')
        content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Chat history area
        self.chat_history = scrolledtext.ScrolledText(content, 
                                                    height=12,
                                                    width=30,
                                                    font=('Arial', 12),
                                                    bg='#2d2d2d',
                                                    fg='#ffffff',
                                                    relief='sunken',
                                                    padx=8,
                                                    pady=8)
        self.chat_history.pack(fill='both', expand=True, pady=(5, 10))
        self.chat_history.config(state='disabled')
        
        # Progress bar
        self.progress_frame = tk.Frame(content, bg='#1e1e1e')
        self.progress_frame.pack(fill='x', pady=(0, 5))
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', padx=8)
        self.progress_bar.pack_forget()  # Hide by default
        
        # Chat input area
        self.chat_input = tk.Text(content,
                                height=3,
                                width=30,
                                font=('Arial', 12),
                                bg='#2d2d2d',
                                fg='#ffffff',
                                insertbackground='#ffffff',
                                relief='sunken',
                                padx=8,
                                pady=8)
        self.chat_input.pack(fill='x', pady=(0, 5))
        
        # Bind Return key to send_chat
        self.chat_input.bind('<Return>', lambda e: self.send_chat())
        self.setup_widget_context_menu(self.chat_input)
        self.setup_widget_context_menu(self.chat_history)
        
        # Button frame
        btn_frame = tk.Frame(content, bg='#1e1e1e')
        btn_frame.pack(fill='x', pady=5)
        
        # Personality selector
        personality_frame = tk.Frame(btn_frame, bg='#1e1e1e')
        personality_frame.pack(side='left', padx=10)
        
        personality_label = tk.Label(personality_frame, text="Mode:", bg='#1e1e1e', fg='#ffffff')
        personality_label.pack(side='left', padx=(0, 5))
        
        personality_menu = ttk.OptionMenu(personality_frame, self.personality_var, "Default", *self.personalities.keys())
        personality_menu.pack(side='left')
        
        # Online toggle button (renamed to 'net')
        self.online_var = tk.BooleanVar(value=False)
        online_btn = ttk.Checkbutton(btn_frame,
                                    text="Net",
                                    style='Retro.TButton',
                                    variable=self.online_var)
        online_btn.pack(side='left', padx=10)
        
        # Learn button (replaces Send)
        learn_btn = ttk.Button(btn_frame,
                             text="Learn",
                             style='Retro.TButton',
                             command=self.learn_selected)
        learn_btn.pack(side='right', padx=10)
        
        # Save All button
        save_btn = ttk.Button(btn_frame,
                            text="Save All",
                            style='Retro.TButton',
                            command=self.save_to_memory)
        save_btn.pack(side='left', padx=10)
        
        # Load button
        load_btn = ttk.Button(btn_frame,
                              text="Load",
                              style='Retro.TButton',
                              command=self.load_from_memory)
        load_btn.pack(side='right', padx=10)
        
        # Send button
        send_btn = ttk.Button(btn_frame,
                             text="Send",
                             style='Retro.TButton',
                             command=self.send_chat)
        send_btn.pack(side='right', padx=10)
    
    def append_message(self, role, content):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"\n{role}: {content}\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
        self.current_messages.append({"role": role, "content": content})
    
    def clear_chat(self):
        self.chat_history.config(state='normal')
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.config(state='disabled')
        self.chat_input.delete(1.0, tk.END)
        self.current_messages = []
        
    def learn_selected(self):
        try:
            # Get selected text from chat input
            selected_text = self.chat_input.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected_text:
                # Save to fast-access memory
                self.chat_memory.save_key_info(selected_text)
                self.append_message("System", f"Key information learned: {selected_text}")
        except tk.TclError:  # No selection
            pass

    def save_to_memory(self):
        if self.current_messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.chat_memory.save_conversation(
                self.current_messages,
                backup_name=f"chat_backup_{timestamp}"
            )
            self.append_message("System", "Complete chat saved to memory.")

    
    def append_partial_message(self, content):
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, content)
        self.chat_history.see(tk.END)
        self.chat_history.update_idletasks()
        self.chat_history.config(state='disabled')

    def process_stream_response(self, response):
        try:
            for line in response.iter_lines():
                if line:
                    response_data = json.loads(line)
                    if 'response' in response_data:
                        # Schedule UI update in main thread
                        self.after(0, lambda x=response_data['response']: self.append_partial_message(x))
            self.after(0, lambda: self.append_partial_message('\n'))
            # Hide and stop progress bar
            self.after(0, lambda: self.progress_bar.stop())
            self.after(0, lambda: self.progress_bar.pack_forget())
        except Exception as e:
            # Hide progress bar on error
            self.after(0, lambda: self.progress_bar.stop())
            self.after(0, lambda: self.progress_bar.pack_forget())
            self.after(0, lambda: self.append_message("System", f"Error: {str(e)}"))

    def perform_web_search(self, query):
        try:
            search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(search_url)
            if response.status_code == 200:
                results = response.json()
                search_text = "\n".join([r.get('Text', '') for r in results.get('RelatedTopics', [])])
                return search_text[:1000] if search_text else "No relevant information found."
            return "Search failed."
        except Exception as e:
            return f"Search error: {str(e)}"

    def send_chat(self):
        text = self.chat_input.get("1.0", tk.END).strip()
        if text:
            self.append_message("You", text)
            self.chat_input.delete(1.0, tk.END)
            
            try:
                # Show progress bar
                self.progress_bar.pack(fill='x', padx=8)
                self.progress_bar.start(10)  # Start animation
                
                # Initialize AI message
                self.chat_history.config(state='normal')
                self.chat_history.insert(tk.END, "\nAI: ")
                self.chat_history.config(state='disabled')
                
                def make_request():
                    try:
                        # If online mode is enabled, perform web search
                        # Get personality instructions
                        personality_prompt = self.personalities[self.personality_var.get()]
                        
                        # Build the prompt
                        if personality_prompt:
                            prompt = f"{personality_prompt}\n\nUser: {text}"
                        else:
                            prompt = text
                            
                        if self.online_var.get():
                            search_results = self.perform_web_search(text)
                            self.online_search_results = search_results
                            prompt = f"{personality_prompt}\n\nContext from web search:\n{search_results}\n\nUser query: {text}"

                        response = requests.post('http://localhost:11434/api/generate',
                                               json={
                                                   'model': 'llava',
                                                   'prompt': prompt,
                                                   'stream': True
                                               },
                                               stream=True)
                        
                        if response.status_code == 200:
                            self.process_stream_response(response)
                        else:
                            self.after(0, lambda: self.append_message("System", 
                                f"Error: Server returned status code {response.status_code}"))
                    except requests.exceptions.ConnectionError:
                        self.after(0, lambda: self.append_message("System", 
                            "Error: Could not connect to Ollama server. Is it running?"))
                    except Exception as e:
                        self.after(0, lambda: self.append_message("System", f"Error: {str(e)}"))
                
                # Start request in a separate thread
                threading.Thread(target=make_request, daemon=True).start()
                
            except Exception as e:
                self.append_message("System", f"Error: {str(e)}")
    
    def load_from_memory(self):
        # Load the most recent conversation from memory
        loaded_messages = self.chat_memory.load_latest_conversation()
        if loaded_messages:
            # Clear current chat
            self.chat_history.config(state='normal')
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.config(state='disabled')
            self.current_messages = []
            
            # Load messages
            for message in loaded_messages:
                self.append_message(message["role"], message["content"])
            self.append_message("System", "Chat loaded from memory.")
        else:
            self.append_message("System", "No saved chat found in memory.")

    def setup_widget_context_menu(self, widget):
        context_menu = tk.Menu(widget, tearoff=0)
        context_menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        
        def show_context_menu(event):
            context_menu.tk_popup(event.x_root, event.y_root)
            
        widget.bind("<Button-3>", show_context_menu)  # Right-click on Windows/Linux
        widget.bind("<Control-Button-1>", show_context_menu)  # Control-click on macOS
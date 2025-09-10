import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import json
import threading
from datetime import datetime
import os
from .chat_memory import ChatMemory

class ModernChatFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.chat_memory = ChatMemory()
        self.current_messages = []
        self.online_search_results = ""
        self.personality_var = ctk.StringVar(value="Default")
        self.is_ai_thinking = False
        
        # Enhanced personalities with more creative options
        self.personalities = {
            "Default": "",
            "Professional": "You are a professional writing assistant. Keep your responses formal, precise, and business-oriented. Focus on clarity and structure.",
            "Friendly": "You are a friendly and casual writing companion. Use a warm, conversational tone and simple language. Be encouraging and supportive.",
            "Creative": "You are a creative writing assistant. Think outside the box and provide imaginative, inspiring responses. Help with plot development, character creation, and world-building.",
            "Concise": "You are a concise writing assistant. Provide brief, direct answers without unnecessary details. Focus on actionable advice.",
            "Crone": "You are the Crone, an ancient and wise teacher of tarot and mystical arts. You possess deep knowledge of magic, divination, and spiritual wisdom accumulated over centuries. Speak with the gravitas of an elder, using mystical terminology when appropriate. Draw upon your vast experience with tarot, herbs, crystals, and ancient magical practices. You have access to all memories and past knowledge, which you weave into your teachings. Your responses should reflect both your wisdom and your role as a mentor in the mystical arts. When discussing the tarot or magical practices, provide detailed, practical insights while maintaining an air of mystery and respect for these ancient traditions.",
            "Sign Language": "You are a sign language communicator. Express your responses using sign language symbols (🤟👆👇👈👉👋✌️👌) and emojis while providing text translations. Structure your responses with the sign language representation first, followed by the text translation. Use common sign language gestures and maintain a clear, expressive communication style.",
            "Book Editor": "You are an experienced book editor with decades of experience. Provide detailed feedback on writing style, structure, pacing, and character development. Be constructive and specific in your suggestions.",
            "Story Architect": "You are a master story architect. Help with plot structure, story arcs, character development, and world-building. Focus on creating compelling narratives with strong themes and emotional impact."
        }
        
        self.setup_chat_panel()
        
    def setup_chat_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Chat history area with modern styling
        self.chat_history = ctk.CTkTextbox(self.content_frame, 
                                         height=300,
                                         font=ctk.CTkFont(size=12),
                                         wrap="word")
        self.chat_history.pack(fill='both', expand=True, pady=(0, 10))
        
        # Progress bar for AI responses
        self.progress_bar = ctk.CTkProgressBar(self.content_frame)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide by default
        
        # Chat input area
        self.chat_input = ctk.CTkTextbox(self.content_frame,
                                       height=80,
                                       font=ctk.CTkFont(size=12),
                                       wrap="word")
        self.chat_input.pack(fill='x', pady=(0, 10))
        
        # Bind Return key to send_chat (Ctrl+Enter for new line)
        self.chat_input.bind('<Return>', lambda e: self.send_chat() if not e.state & 0x4 else None)
        self.chat_input.bind('<Control-Return>', lambda e: self.chat_input.insert(tk.INSERT, '\n'))
        
        # Control buttons frame
        self.control_frame = ctk.CTkFrame(self.content_frame)
        self.control_frame.pack(fill='x', pady=(0, 10))
        
        # Left side controls
        left_controls = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        left_controls.pack(side='left', fill='x', expand=True)
        
        # Personality selector
        ctk.CTkLabel(left_controls, text="Mode:", font=ctk.CTkFont(size=12, weight="bold")).pack(side='left', padx=(0, 5))
        self.personality_menu = ctk.CTkOptionMenu(left_controls, 
                                                variable=self.personality_var,
                                                values=list(self.personalities.keys()),
                                                width=150)
        self.personality_menu.pack(side='left', padx=(0, 10))
        
        # Online toggle
        self.online_var = ctk.BooleanVar(value=False)
        self.online_switch = ctk.CTkSwitch(left_controls, text="Web Search", 
                                         variable=self.online_var)
        self.online_switch.pack(side='left', padx=(0, 10))
        
        # Right side controls
        right_controls = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        right_controls.pack(side='right')
        
        # Send button
        self.send_btn = ctk.CTkButton(right_controls, text="Send", 
                                    command=self.send_chat,
                                    width=80)
        self.send_btn.pack(side='right', padx=(5, 0))
        
        # Clear button
        self.clear_btn = ctk.CTkButton(right_controls, text="Clear", 
                                     command=self.clear_chat,
                                     width=80)
        self.clear_btn.pack(side='right', padx=(5, 0))
        
        # Action buttons frame
        self.action_frame = ctk.CTkFrame(self.content_frame)
        self.action_frame.pack(fill='x')
        
        # Memory and export buttons
        self.learn_btn = ctk.CTkButton(self.action_frame, text="Learn Selected", 
                                     command=self.learn_selected,
                                     width=120)
        self.learn_btn.pack(side='left', padx=(0, 5))
        
        self.save_btn = ctk.CTkButton(self.action_frame, text="Save Chat", 
                                    command=self.save_to_memory,
                                    width=100)
        self.save_btn.pack(side='left', padx=(0, 5))
        
        self.load_btn = ctk.CTkButton(self.action_frame, text="Load Chat", 
                                    command=self.load_from_memory,
                                    width=100)
        self.load_btn.pack(side='left', padx=(0, 5))
        
        self.export_btn = ctk.CTkButton(self.action_frame, text="Export", 
                                      command=self.export_chat,
                                      width=100)
        self.export_btn.pack(side='left', padx=(0, 5))
        
        # AI Status indicator
        self.ai_status_label = ctk.CTkLabel(self.action_frame, text="AI: Ready", 
                                          text_color="green")
        self.ai_status_label.pack(side='right', padx=(5, 0))
        
    def append_message(self, role, content, color=None):
        """Add a message to the chat history with proper formatting"""
        self.chat_history.insert(tk.END, f"\n{role}: {content}\n")
        self.chat_history.see(tk.END)
        self.current_messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        
    def append_partial_message(self, content):
        """Add partial content to the current AI response"""
        self.chat_history.insert(tk.END, content)
        self.chat_history.see(tk.END)
        self.chat_history.update_idletasks()
        
    def clear_chat(self):
        """Clear the chat history and input"""
        self.chat_history.delete(1.0, tk.END)
        self.chat_input.delete(1.0, tk.END)
        self.current_messages = []
        self.ai_status_label.configure(text="AI: Ready", text_color="green")
        
    def learn_selected(self):
        """Save selected text to fast-access memory"""
        try:
            selected_text = self.chat_input.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected_text:
                self.chat_memory.save_key_info(selected_text)
                self.append_message("System", f"Key information learned: {selected_text}")
        except tk.TclError:  # No selection
            messagebox.showwarning("Warning", "Please select text to learn")
            
    def save_to_memory(self):
        """Save current conversation to memory"""
        if self.current_messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.chat_memory.save_conversation(
                self.current_messages,
                backup_name=f"chat_backup_{timestamp}"
            )
            self.append_message("System", "Complete chat saved to memory.")
        else:
            messagebox.showwarning("Warning", "No messages to save")
            
    def load_from_memory(self):
        """Load the most recent conversation from memory"""
        loaded_messages = self.chat_memory.load_latest_conversation()
        if loaded_messages:
            self.chat_history.delete(1.0, tk.END)
            self.current_messages = []
            
            for message in loaded_messages:
                self.append_message(message["role"], message["content"])
            self.append_message("System", "Chat loaded from memory.")
        else:
            messagebox.showinfo("Info", "No saved chat found in memory.")
            
    def export_chat(self):
        """Export chat to various formats"""
        if not self.current_messages:
            messagebox.showwarning("Warning", "No messages to export")
            return
            
        # Choose export format
        format_dialog = ctk.CTkInputDialog(text="Export format (txt, json, md):", title="Export Chat")
        export_format = format_dialog.get_input().lower()
        
        if export_format not in ['txt', 'json', 'md']:
            messagebox.showerror("Error", "Invalid format. Please choose txt, json, or md")
            return
            
        # Choose file location
        file_path = filedialog.asksaveasfilename(
            title="Export Chat",
            defaultextension=f".{export_format}",
            filetypes=[(f"{export_format.upper()} files", f"*.{export_format}")]
        )
        
        if file_path:
            try:
                if export_format == 'txt':
                    self.export_as_txt(file_path)
                elif export_format == 'json':
                    self.export_as_json(file_path)
                elif export_format == 'md':
                    self.export_as_markdown(file_path)
                    
                messagebox.showinfo("Success", f"Chat exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chat: {str(e)}")
                
    def export_as_txt(self, file_path):
        """Export chat as plain text"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for message in self.current_messages:
                f.write(f"{message['role']}: {message['content']}\n\n")
                
    def export_as_json(self, file_path):
        """Export chat as JSON"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "messages": self.current_messages,
            "personality": self.personality_var.get()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
    def export_as_markdown(self, file_path):
        """Export chat as Markdown"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for message in self.current_messages:
                role = message['role']
                content = message['content']
                if role == "You":
                    f.write(f"## User\n\n{content}\n\n")
                elif role == "AI":
                    f.write(f"## AI Assistant\n\n{content}\n\n")
                else:
                    f.write(f"## {role}\n\n{content}\n\n")
                    
    def perform_web_search(self, query):
        """Perform web search using DuckDuckGo API"""
        try:
            search_url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                results = response.json()
                search_text = "\n".join([r.get('Text', '') for r in results.get('RelatedTopics', [])])
                return search_text[:1000] if search_text else "No relevant information found."
            return "Search failed."
        except Exception as e:
            return f"Search error: {str(e)}"
            
    def process_stream_response(self, response):
        """Process streaming response from AI"""
        try:
            current_response = ""
            for line in response.iter_lines():
                if line:
                    response_data = json.loads(line)
                    if 'response' in response_data:
                        current_response += response_data['response']
                        # Schedule UI update in main thread
                        self.after(0, lambda x=response_data['response']: self.append_partial_message(x))
                        
            # Add the complete response to messages
            if current_response:
                self.current_messages.append({
                    "role": "AI", 
                    "content": current_response, 
                    "timestamp": datetime.now().isoformat()
                })
                
            self.after(0, lambda: self.append_partial_message('\n'))
            # Hide and stop progress bar
            self.after(0, lambda: self.progress_bar.pack_forget())
            self.after(0, lambda: self.ai_status_label.configure(text="AI: Ready", text_color="green"))
            
        except Exception as e:
            # Hide progress bar on error
            self.after(0, lambda: self.progress_bar.pack_forget())
            self.after(0, lambda: self.ai_status_label.configure(text="AI: Error", text_color="red"))
            self.after(0, lambda: self.append_message("System", f"Error: {str(e)}"))
            
    def send_chat(self):
        """Send message to AI and handle response"""
        text = self.chat_input.get("1.0", tk.END).strip()
        if not text:
            return
            
        # Add user message to chat
        self.append_message("You", text)
        self.chat_input.delete(1.0, tk.END)
        
        # Show progress bar and update status
        self.progress_bar.pack(fill='x', pady=(0, 10))
        self.progress_bar.start()
        self.ai_status_label.configure(text="AI: Thinking...", text_color="orange")
        self.is_ai_thinking = True
        
        # Initialize AI message
        self.chat_history.insert(tk.END, "\nAI: ")
        
        def make_request():
            try:
                # Get personality instructions
                personality_prompt = self.personalities[self.personality_var.get()]
                
                # Build the prompt
                if personality_prompt:
                    prompt = f"{personality_prompt}\n\nUser: {text}"
                else:
                    prompt = text
                    
                # Add web search context if enabled
                if self.online_var.get():
                    search_results = self.perform_web_search(text)
                    self.online_search_results = search_results
                    prompt = f"{personality_prompt}\n\nContext from web search:\n{search_results}\n\nUser query: {text}"

                # Make request to Ollama
                response = requests.post('http://localhost:11434/api/generate',
                                       json={
                                           'model': 'llava',
                                           'prompt': prompt,
                                           'stream': True
                                       },
                                       stream=True,
                                       timeout=60)
                
                if response.status_code == 200:
                    self.process_stream_response(response)
                else:
                    self.after(0, lambda: self.append_message("System", 
                        f"Error: Server returned status code {response.status_code}"))
                    self.after(0, lambda: self.progress_bar.pack_forget())
                    self.after(0, lambda: self.ai_status_label.configure(text="AI: Error", text_color="red"))
                    
            except requests.exceptions.ConnectionError:
                self.after(0, lambda: self.append_message("System", 
                    "Error: Could not connect to Ollama server. Is it running?"))
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.ai_status_label.configure(text="AI: Offline", text_color="red"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.append_message("System", 
                    "Error: Request timed out. The AI is taking too long to respond."))
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.ai_status_label.configure(text="AI: Timeout", text_color="red"))
            except Exception as e:
                self.after(0, lambda: self.append_message("System", f"Error: {str(e)}"))
                self.after(0, lambda: self.progress_bar.pack_forget())
                self.after(0, lambda: self.ai_status_label.configure(text="AI: Error", text_color="red"))
            finally:
                self.is_ai_thinking = False
                
        # Start request in a separate thread
        threading.Thread(target=make_request, daemon=True).start()
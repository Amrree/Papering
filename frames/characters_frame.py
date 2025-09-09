import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from datetime import datetime
import os

class CharactersFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.characters = []
        self.current_character = None
        self.setup_characters_panel()
        
    def setup_characters_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(self.content_frame, text="Character Management", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Create two-column layout
        self.main_container = ctk.CTkFrame(self.content_frame)
        self.main_container.pack(fill='both', expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Character list
        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Character list header
        list_header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(list_header, text="Characters", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side='left')
        
        self.add_char_btn = ctk.CTkButton(list_header, text="+ Add", 
                                        command=self.add_character,
                                        width=60)
        self.add_char_btn.pack(side='right')
        
        # Character list
        self.char_listbox = tk.Listbox(self.left_panel, 
                                     bg="#2b2b2b", fg="white",
                                     selectbackground="#1f538d",
                                     font=("Arial", 12))
        self.char_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.char_listbox.bind('<Double-Button-1>', self.edit_character)
        self.char_listbox.bind('<<ListboxSelect>>', self.select_character)
        
        # Character actions
        char_actions = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        char_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        self.edit_btn = ctk.CTkButton(char_actions, text="Edit", 
                                    command=self.edit_character,
                                    width=60)
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(char_actions, text="Delete", 
                                      command=self.delete_character,
                                      width=60,
                                      fg_color="red", hover_color="darkred")
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        self.export_btn = ctk.CTkButton(char_actions, text="Export", 
                                      command=self.export_characters,
                                      width=60)
        self.export_btn.pack(side='left')
        
        # Right panel - Character details
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Character details header
        details_header = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        details_header.pack(fill='x', padx=10, pady=10)
        
        self.details_title = ctk.CTkLabel(details_header, text="Character Details", 
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.details_title.pack(side='left')
        
        self.save_btn = ctk.CTkButton(details_header, text="Save", 
                                    command=self.save_character,
                                    width=60)
        self.save_btn.pack(side='right')
        
        # Character details form
        self.details_frame = ctk.CTkScrollableFrame(self.right_panel)
        self.details_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Basic Information
        basic_frame = ctk.CTkFrame(self.details_frame)
        basic_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(basic_frame, text="Basic Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Name
        name_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        name_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(name_frame, text="Name:").pack(side='left', padx=(0, 10))
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Character name")
        self.name_entry.pack(side='right', fill='x', expand=True)
        
        # Age
        age_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        age_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(age_frame, text="Age:").pack(side='left', padx=(0, 10))
        self.age_entry = ctk.CTkEntry(age_frame, placeholder_text="Age or age range")
        self.age_entry.pack(side='right', fill='x', expand=True)
        
        # Gender
        gender_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        gender_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(gender_frame, text="Gender:").pack(side='left', padx=(0, 10))
        self.gender_var = ctk.StringVar(value="")
        self.gender_menu = ctk.CTkOptionMenu(gender_frame, variable=self.gender_var,
                                           values=["", "Male", "Female", "Non-binary", "Other"])
        self.gender_menu.pack(side='right', fill='x', expand=True)
        
        # Role
        role_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        role_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(role_frame, text="Role:").pack(side='left', padx=(0, 10))
        self.role_var = ctk.StringVar(value="")
        self.role_menu = ctk.CTkOptionMenu(role_frame, variable=self.role_var,
                                         values=["", "Protagonist", "Antagonist", "Supporting", "Minor", "Background"])
        self.role_menu.pack(side='right', fill='x', expand=True)
        
        # Physical Description
        physical_frame = ctk.CTkFrame(self.details_frame)
        physical_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(physical_frame, text="Physical Description", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.physical_text = ctk.CTkTextbox(physical_frame, height=100,
                                          placeholder_text="Describe physical appearance, height, build, hair, eyes, etc.")
        self.physical_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Personality
        personality_frame = ctk.CTkFrame(self.details_frame)
        personality_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(personality_frame, text="Personality", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.personality_text = ctk.CTkTextbox(personality_frame, height=100,
                                             placeholder_text="Describe personality traits, quirks, habits, etc.")
        self.personality_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Background
        background_frame = ctk.CTkFrame(self.details_frame)
        background_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(background_frame, text="Background & History", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.background_text = ctk.CTkTextbox(background_frame, height=100,
                                            placeholder_text="Describe backstory, family, education, career, etc.")
        self.background_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Goals & Motivations
        goals_frame = ctk.CTkFrame(self.details_frame)
        goals_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(goals_frame, text="Goals & Motivations", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.goals_text = ctk.CTkTextbox(goals_frame, height=100,
                                       placeholder_text="What does this character want? What drives them?")
        self.goals_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Relationships
        relationships_frame = ctk.CTkFrame(self.details_frame)
        relationships_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(relationships_frame, text="Relationships", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.relationships_text = ctk.CTkTextbox(relationships_frame, height=100,
                                               placeholder_text="Describe relationships with other characters")
        self.relationships_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Notes
        notes_frame = ctk.CTkFrame(self.details_frame)
        notes_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(notes_frame, text="Additional Notes", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(notes_frame, height=100,
                                       placeholder_text="Any additional notes, ideas, or details")
        self.notes_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Load sample characters
        self.load_sample_characters()
        
    def load_sample_characters(self):
        """Load some sample characters"""
        sample_characters = [
            {
                "name": "Alex Morgan",
                "age": "28",
                "gender": "Non-binary",
                "role": "Protagonist",
                "physical": "Tall and lean with short, curly brown hair and piercing green eyes. Always wears practical clothing.",
                "personality": "Intelligent, curious, and determined. Has a dry sense of humor and is fiercely loyal to friends.",
                "background": "Former journalist turned detective. Grew up in a small town but moved to the city for college.",
                "goals": "Wants to solve the mystery that destroyed their career and find justice for the victims.",
                "relationships": "Close with their former editor Sarah, estranged from their family.",
                "notes": "Has a photographic memory and excellent observation skills."
            },
            {
                "name": "Dr. Elena Vasquez",
                "age": "45",
                "gender": "Female",
                "role": "Supporting",
                "physical": "Medium height with silver-streaked black hair and warm brown eyes. Dresses professionally.",
                "personality": "Wise, patient, and empathetic. Excellent listener with a calming presence.",
                "background": "Renowned psychologist with 20 years of experience. Specializes in trauma therapy.",
                "goals": "Helps Alex process their trauma and provides psychological insights into the case.",
                "relationships": "Mentor figure to Alex, respected by the police department.",
                "notes": "Has a private practice and occasionally consults on criminal cases."
            }
        ]
        
        for char in sample_characters:
            self.characters.append(char)
            self.char_listbox.insert(tk.END, char["name"])
            
    def add_character(self):
        """Add a new character"""
        dialog = ctk.CTkInputDialog(text="Enter character name:", title="New Character")
        name = dialog.get_input()
        
        if name:
            new_character = {
                "name": name,
                "age": "",
                "gender": "",
                "role": "",
                "physical": "",
                "personality": "",
                "background": "",
                "goals": "",
                "relationships": "",
                "notes": ""
            }
            
            self.characters.append(new_character)
            self.char_listbox.insert(tk.END, name)
            self.char_listbox.selection_clear(0, tk.END)
            self.char_listbox.selection_set(tk.END)
            self.select_character(None)
            
    def select_character(self, event):
        """Select a character from the list"""
        selection = self.char_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_character = index
            self.load_character_details(index)
            
    def load_character_details(self, index):
        """Load character details into the form"""
        if 0 <= index < len(self.characters):
            char = self.characters[index]
            
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, char.get("name", ""))
            
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, char.get("age", ""))
            
            self.gender_var.set(char.get("gender", ""))
            self.role_var.set(char.get("role", ""))
            
            self.physical_text.delete("1.0", tk.END)
            self.physical_text.insert("1.0", char.get("physical", ""))
            
            self.personality_text.delete("1.0", tk.END)
            self.personality_text.insert("1.0", char.get("personality", ""))
            
            self.background_text.delete("1.0", tk.END)
            self.background_text.insert("1.0", char.get("background", ""))
            
            self.goals_text.delete("1.0", tk.END)
            self.goals_text.insert("1.0", char.get("goals", ""))
            
            self.relationships_text.delete("1.0", tk.END)
            self.relationships_text.insert("1.0", char.get("relationships", ""))
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", char.get("notes", ""))
            
    def save_character(self):
        """Save current character details"""
        if self.current_character is not None:
            char = self.characters[self.current_character]
            
            char["name"] = self.name_entry.get()
            char["age"] = self.age_entry.get()
            char["gender"] = self.gender_var.get()
            char["role"] = self.role_var.get()
            char["physical"] = self.physical_text.get("1.0", tk.END).strip()
            char["personality"] = self.personality_text.get("1.0", tk.END).strip()
            char["background"] = self.background_text.get("1.0", tk.END).strip()
            char["goals"] = self.goals_text.get("1.0", tk.END).strip()
            char["relationships"] = self.relationships_text.get("1.0", tk.END).strip()
            char["notes"] = self.notes_text.get("1.0", tk.END).strip()
            
            # Update listbox
            self.char_listbox.delete(self.current_character)
            self.char_listbox.insert(self.current_character, char["name"])
            self.char_listbox.selection_set(self.current_character)
            
            messagebox.showinfo("Success", "Character saved successfully!")
            
    def edit_character(self):
        """Edit selected character"""
        if self.current_character is not None:
            self.save_character()
            
    def delete_character(self):
        """Delete selected character"""
        if self.current_character is not None:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this character?"):
                del self.characters[self.current_character]
                self.char_listbox.delete(self.current_character)
                self.current_character = None
                self.clear_form()
                
    def clear_form(self):
        """Clear the character details form"""
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.gender_var.set("")
        self.role_var.set("")
        self.physical_text.delete("1.0", tk.END)
        self.personality_text.delete("1.0", tk.END)
        self.background_text.delete("1.0", tk.END)
        self.goals_text.delete("1.0", tk.END)
        self.relationships_text.delete("1.0", tk.END)
        self.notes_text.delete("1.0", tk.END)
        
    def export_characters(self):
        """Export characters to file"""
        if not self.characters:
            messagebox.showwarning("Warning", "No characters to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Characters",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.characters, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Character Database\n")
                        f.write("=" * 50 + "\n\n")
                        for i, char in enumerate(self.characters, 1):
                            f.write(f"{i}. {char['name']}\n")
                            f.write("-" * 30 + "\n")
                            for key, value in char.items():
                                if key != 'name' and value:
                                    f.write(f"{key.title()}: {value}\n")
                            f.write("\n")
                            
                messagebox.showinfo("Success", f"Characters exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export characters: {str(e)}")
                
    def get_characters(self):
        """Get all characters"""
        return self.characters
        
    def get_character_names(self):
        """Get list of character names"""
        return [char["name"] for char in self.characters if char["name"]]
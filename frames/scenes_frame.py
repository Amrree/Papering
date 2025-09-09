import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from datetime import datetime
import os

class ScenesFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.scenes = []
        self.current_scene = None
        self.setup_scenes_panel()
        
    def setup_scenes_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(self.content_frame, text="Scene Management", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Create two-column layout
        self.main_container = ctk.CTkFrame(self.content_frame)
        self.main_container.pack(fill='both', expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Scene list
        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Scene list header
        list_header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(list_header, text="Scenes", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side='left')
        
        self.add_scene_btn = ctk.CTkButton(list_header, text="+ Add", 
                                         command=self.add_scene,
                                         width=60)
        self.add_scene_btn.pack(side='right')
        
        # Scene list
        self.scene_listbox = tk.Listbox(self.left_panel, 
                                      bg="#2b2b2b", fg="white",
                                      selectbackground="#1f538d",
                                      font=("Arial", 12))
        self.scene_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.scene_listbox.bind('<Double-Button-1>', self.edit_scene)
        self.scene_listbox.bind('<<ListboxSelect>>', self.select_scene)
        
        # Scene actions
        scene_actions = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        scene_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        self.edit_btn = ctk.CTkButton(scene_actions, text="Edit", 
                                    command=self.edit_scene,
                                    width=60)
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(scene_actions, text="Delete", 
                                      command=self.delete_scene,
                                      width=60,
                                      fg_color="red", hover_color="darkred")
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        self.export_btn = ctk.CTkButton(scene_actions, text="Export", 
                                      command=self.export_scenes,
                                      width=60)
        self.export_btn.pack(side='left')
        
        # Right panel - Scene details
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Scene details header
        details_header = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        details_header.pack(fill='x', padx=10, pady=10)
        
        self.details_title = ctk.CTkLabel(details_header, text="Scene Details", 
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.details_title.pack(side='left')
        
        self.save_btn = ctk.CTkButton(details_header, text="Save", 
                                    command=self.save_scene,
                                    width=60)
        self.save_btn.pack(side='right')
        
        # Scene details form
        self.details_frame = ctk.CTkScrollableFrame(self.right_panel)
        self.details_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Basic Information
        basic_frame = ctk.CTkFrame(self.details_frame)
        basic_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(basic_frame, text="Basic Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Scene title
        title_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        title_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(title_frame, text="Title:").pack(side='left', padx=(0, 10))
        self.title_entry = ctk.CTkEntry(title_frame, placeholder_text="Scene title")
        self.title_entry.pack(side='right', fill='x', expand=True)
        
        # Chapter
        chapter_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        chapter_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(chapter_frame, text="Chapter:").pack(side='left', padx=(0, 10))
        self.chapter_entry = ctk.CTkEntry(chapter_frame, placeholder_text="Chapter number or name")
        self.chapter_entry.pack(side='right', fill='x', expand=True)
        
        # Scene number
        number_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        number_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(number_frame, text="Scene #:").pack(side='left', padx=(0, 10))
        self.number_entry = ctk.CTkEntry(number_frame, placeholder_text="Scene number")
        self.number_entry.pack(side='right', fill='x', expand=True)
        
        # Scene type
        type_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        type_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(type_frame, text="Type:").pack(side='left', padx=(0, 10))
        self.type_var = ctk.StringVar(value="")
        self.type_menu = ctk.CTkOptionMenu(type_frame, variable=self.type_var,
                                         values=["", "Action", "Dialogue", "Description", "Flashback", "Transition", "Climax", "Resolution"])
        self.type_menu.pack(side='right', fill='x', expand=True)
        
        # POV Character
        pov_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        pov_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(pov_frame, text="POV Character:").pack(side='left', padx=(0, 10))
        self.pov_entry = ctk.CTkEntry(pov_frame, placeholder_text="Point of view character")
        self.pov_entry.pack(side='right', fill='x', expand=True)
        
        # Setting
        setting_frame = ctk.CTkFrame(self.details_frame)
        setting_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(setting_frame, text="Setting", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Location
        location_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
        location_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(location_frame, text="Location:").pack(side='left', padx=(0, 10))
        self.location_entry = ctk.CTkEntry(location_frame, placeholder_text="Where does this scene take place?")
        self.location_entry.pack(side='right', fill='x', expand=True)
        
        # Time
        time_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
        time_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(time_frame, text="Time:").pack(side='left', padx=(0, 10))
        self.time_entry = ctk.CTkEntry(time_frame, placeholder_text="When does this scene take place?")
        self.time_entry.pack(side='right', fill='x', expand=True)
        
        # Weather/Mood
        mood_frame = ctk.CTkFrame(setting_frame, fg_color="transparent")
        mood_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(mood_frame, text="Mood/Weather:").pack(side='left', padx=(0, 10))
        self.mood_entry = ctk.CTkEntry(mood_frame, placeholder_text="Atmosphere, weather, mood")
        self.mood_entry.pack(side='right', fill='x', expand=True)
        
        # Characters in scene
        characters_frame = ctk.CTkFrame(self.details_frame)
        characters_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(characters_frame, text="Characters in Scene", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.characters_text = ctk.CTkTextbox(characters_frame, height=80,
                                            placeholder_text="List all characters present in this scene")
        self.characters_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Scene content
        content_frame = ctk.CTkFrame(self.details_frame)
        content_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(content_frame, text="Scene Content", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.content_text = ctk.CTkTextbox(content_frame, height=150,
                                         placeholder_text="Write the scene content here...")
        self.content_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Scene purpose
        purpose_frame = ctk.CTkFrame(self.details_frame)
        purpose_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(purpose_frame, text="Scene Purpose", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.purpose_text = ctk.CTkTextbox(purpose_frame, height=100,
                                         placeholder_text="What is the purpose of this scene? What should it accomplish?")
        self.purpose_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Conflict/Tension
        conflict_frame = ctk.CTkFrame(self.details_frame)
        conflict_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(conflict_frame, text="Conflict & Tension", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.conflict_text = ctk.CTkTextbox(conflict_frame, height=100,
                                          placeholder_text="What conflict or tension exists in this scene?")
        self.conflict_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Notes
        notes_frame = ctk.CTkFrame(self.details_frame)
        notes_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(notes_frame, text="Additional Notes", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(notes_frame, height=100,
                                       placeholder_text="Any additional notes, ideas, or details")
        self.notes_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Load sample scenes
        self.load_sample_scenes()
        
    def load_sample_scenes(self):
        """Load some sample scenes"""
        sample_scenes = [
            {
                "title": "The Discovery",
                "chapter": "1",
                "number": "1",
                "type": "Action",
                "pov": "Alex Morgan",
                "location": "Abandoned warehouse",
                "time": "Late evening",
                "mood": "Dark and foreboding",
                "characters": "Alex Morgan, Detective Sarah Chen",
                "content": "Alex pushes open the creaking door to the warehouse. The beam of their flashlight cuts through the darkness, revealing dust motes dancing in the air. 'This is where it happened,' Alex whispers, their voice echoing off the metal walls.",
                "purpose": "Introduce the protagonist and the central mystery. Establish the tone and setting.",
                "conflict": "Alex is investigating a case that destroyed their career. They're risking everything to find the truth.",
                "notes": "This scene sets up the main conflict and introduces the protagonist's determination."
            },
            {
                "title": "The Confession",
                "chapter": "3",
                "number": "5",
                "type": "Dialogue",
                "pov": "Alex Morgan",
                "location": "Dr. Vasquez's office",
                "time": "Afternoon",
                "mood": "Intimate and vulnerable",
                "characters": "Alex Morgan, Dr. Elena Vasquez",
                "content": "'I can't sleep,' Alex admits, staring at their hands. 'Every time I close my eyes, I see their faces.' Dr. Vasquez leans forward, her expression gentle but professional. 'Tell me about the faces, Alex.'",
                "purpose": "Reveal Alex's emotional state and trauma. Develop the relationship with Dr. Vasquez.",
                "conflict": "Alex is struggling with PTSD from the case. They need to trust Dr. Vasquez to help them heal.",
                "notes": "Important character development scene. Shows Alex's vulnerability and Dr. Vasquez's role as a mentor."
            }
        ]
        
        for scene in sample_scenes:
            self.scenes.append(scene)
            self.scene_listbox.insert(tk.END, f"{scene['chapter']}.{scene['number']} - {scene['title']}")
            
    def add_scene(self):
        """Add a new scene"""
        dialog = ctk.CTkInputDialog(text="Enter scene title:", title="New Scene")
        title = dialog.get_input()
        
        if title:
            new_scene = {
                "title": title,
                "chapter": "",
                "number": "",
                "type": "",
                "pov": "",
                "location": "",
                "time": "",
                "mood": "",
                "characters": "",
                "content": "",
                "purpose": "",
                "conflict": "",
                "notes": ""
            }
            
            self.scenes.append(new_scene)
            self.scene_listbox.insert(tk.END, f"New - {title}")
            self.scene_listbox.selection_clear(0, tk.END)
            self.scene_listbox.selection_set(tk.END)
            self.select_scene(None)
            
    def select_scene(self, event):
        """Select a scene from the list"""
        selection = self.scene_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_scene = index
            self.load_scene_details(index)
            
    def load_scene_details(self, index):
        """Load scene details into the form"""
        if 0 <= index < len(self.scenes):
            scene = self.scenes[index]
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, scene.get("title", ""))
            
            self.chapter_entry.delete(0, tk.END)
            self.chapter_entry.insert(0, scene.get("chapter", ""))
            
            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, scene.get("number", ""))
            
            self.type_var.set(scene.get("type", ""))
            self.pov_entry.delete(0, tk.END)
            self.pov_entry.insert(0, scene.get("pov", ""))
            
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, scene.get("location", ""))
            
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, scene.get("time", ""))
            
            self.mood_entry.delete(0, tk.END)
            self.mood_entry.insert(0, scene.get("mood", ""))
            
            self.characters_text.delete("1.0", tk.END)
            self.characters_text.insert("1.0", scene.get("characters", ""))
            
            self.content_text.delete("1.0", tk.END)
            self.content_text.insert("1.0", scene.get("content", ""))
            
            self.purpose_text.delete("1.0", tk.END)
            self.purpose_text.insert("1.0", scene.get("purpose", ""))
            
            self.conflict_text.delete("1.0", tk.END)
            self.conflict_text.insert("1.0", scene.get("conflict", ""))
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", scene.get("notes", ""))
            
    def save_scene(self):
        """Save current scene details"""
        if self.current_scene is not None:
            scene = self.scenes[self.current_scene]
            
            scene["title"] = self.title_entry.get()
            scene["chapter"] = self.chapter_entry.get()
            scene["number"] = self.number_entry.get()
            scene["type"] = self.type_var.get()
            scene["pov"] = self.pov_entry.get()
            scene["location"] = self.location_entry.get()
            scene["time"] = self.time_entry.get()
            scene["mood"] = self.mood_entry.get()
            scene["characters"] = self.characters_text.get("1.0", tk.END).strip()
            scene["content"] = self.content_text.get("1.0", tk.END).strip()
            scene["purpose"] = self.purpose_text.get("1.0", tk.END).strip()
            scene["conflict"] = self.conflict_text.get("1.0", tk.END).strip()
            scene["notes"] = self.notes_text.get("1.0", tk.END).strip()
            
            # Update listbox
            display_text = f"{scene['chapter']}.{scene['number']} - {scene['title']}" if scene['chapter'] and scene['number'] else scene['title']
            self.scene_listbox.delete(self.current_scene)
            self.scene_listbox.insert(self.current_scene, display_text)
            self.scene_listbox.selection_set(self.current_scene)
            
            messagebox.showinfo("Success", "Scene saved successfully!")
            
    def edit_scene(self):
        """Edit selected scene"""
        if self.current_scene is not None:
            self.save_scene()
            
    def delete_scene(self):
        """Delete selected scene"""
        if self.current_scene is not None:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this scene?"):
                del self.scenes[self.current_scene]
                self.scene_listbox.delete(self.current_scene)
                self.current_scene = None
                self.clear_form()
                
    def clear_form(self):
        """Clear the scene details form"""
        self.title_entry.delete(0, tk.END)
        self.chapter_entry.delete(0, tk.END)
        self.number_entry.delete(0, tk.END)
        self.type_var.set("")
        self.pov_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.mood_entry.delete(0, tk.END)
        self.characters_text.delete("1.0", tk.END)
        self.content_text.delete("1.0", tk.END)
        self.purpose_text.delete("1.0", tk.END)
        self.conflict_text.delete("1.0", tk.END)
        self.notes_text.delete("1.0", tk.END)
        
    def export_scenes(self):
        """Export scenes to file"""
        if not self.scenes:
            messagebox.showwarning("Warning", "No scenes to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Scenes",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.scenes, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Scene Database\n")
                        f.write("=" * 50 + "\n\n")
                        for i, scene in enumerate(self.scenes, 1):
                            f.write(f"{i}. {scene['title']}\n")
                            f.write("-" * 30 + "\n")
                            for key, value in scene.items():
                                if key != 'title' and value:
                                    f.write(f"{key.title()}: {value}\n")
                            f.write("\n")
                            
                messagebox.showinfo("Success", f"Scenes exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export scenes: {str(e)}")
                
    def get_scenes(self):
        """Get all scenes"""
        return self.scenes
        
    def get_scenes_by_chapter(self, chapter):
        """Get scenes for a specific chapter"""
        return [scene for scene in self.scenes if scene.get("chapter") == str(chapter)]
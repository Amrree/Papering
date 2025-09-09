import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
from datetime import datetime
import os

class OutlineFrame(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.chapters = []
        self.current_chapter = None
        self.setup_outline_panel()
        
    def setup_outline_panel(self):
        # Main content frame
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(self.content_frame, text="Book Outline", 
                                 font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 10))
        
        # Create two-column layout
        self.main_container = ctk.CTkFrame(self.content_frame)
        self.main_container.pack(fill='both', expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=2)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Chapter list
        self.left_panel = ctk.CTkFrame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Chapter list header
        list_header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        list_header.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(list_header, text="Chapters", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side='left')
        
        self.add_chapter_btn = ctk.CTkButton(list_header, text="+ Add", 
                                           command=self.add_chapter,
                                           width=60)
        self.add_chapter_btn.pack(side='right')
        
        # Chapter list
        self.chapter_listbox = tk.Listbox(self.left_panel, 
                                        bg="#2b2b2b", fg="white",
                                        selectbackground="#1f538d",
                                        font=("Arial", 12))
        self.chapter_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.chapter_listbox.bind('<Double-Button-1>', self.edit_chapter)
        self.chapter_listbox.bind('<<ListboxSelect>>', self.select_chapter)
        
        # Chapter actions
        chapter_actions = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        chapter_actions.pack(fill='x', padx=10, pady=(0, 10))
        
        self.edit_btn = ctk.CTkButton(chapter_actions, text="Edit", 
                                    command=self.edit_chapter,
                                    width=60)
        self.edit_btn.pack(side='left', padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(chapter_actions, text="Delete", 
                                      command=self.delete_chapter,
                                      width=60,
                                      fg_color="red", hover_color="darkred")
        self.delete_btn.pack(side='left', padx=(0, 5))
        
        self.move_up_btn = ctk.CTkButton(chapter_actions, text="↑", 
                                       command=self.move_chapter_up,
                                       width=30)
        self.move_up_btn.pack(side='left', padx=(0, 5))
        
        self.move_down_btn = ctk.CTkButton(chapter_actions, text="↓", 
                                         command=self.move_chapter_down,
                                         width=30)
        self.move_down_btn.pack(side='left', padx=(0, 5))
        
        self.export_btn = ctk.CTkButton(chapter_actions, text="Export", 
                                      command=self.export_outline,
                                      width=60)
        self.export_btn.pack(side='left')
        
        # Right panel - Chapter details
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Chapter details header
        details_header = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        details_header.pack(fill='x', padx=10, pady=10)
        
        self.details_title = ctk.CTkLabel(details_header, text="Chapter Details", 
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.details_title.pack(side='left')
        
        self.save_btn = ctk.CTkButton(details_header, text="Save", 
                                    command=self.save_chapter,
                                    width=60)
        self.save_btn.pack(side='right')
        
        # Chapter details form
        self.details_frame = ctk.CTkScrollableFrame(self.right_panel)
        self.details_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Basic Information
        basic_frame = ctk.CTkFrame(self.details_frame)
        basic_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(basic_frame, text="Basic Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Chapter number
        number_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        number_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(number_frame, text="Chapter #:").pack(side='left', padx=(0, 10))
        self.number_entry = ctk.CTkEntry(number_frame, placeholder_text="Chapter number")
        self.number_entry.pack(side='right', fill='x', expand=True)
        
        # Chapter title
        title_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        title_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(title_frame, text="Title:").pack(side='left', padx=(0, 10))
        self.title_entry = ctk.CTkEntry(title_frame, placeholder_text="Chapter title")
        self.title_entry.pack(side='right', fill='x', expand=True)
        
        # POV Character
        pov_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        pov_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(pov_frame, text="POV Character:").pack(side='left', padx=(0, 10))
        self.pov_entry = ctk.CTkEntry(pov_frame, placeholder_text="Point of view character")
        self.pov_entry.pack(side='right', fill='x', expand=True)
        
        # Chapter summary
        summary_frame = ctk.CTkFrame(self.details_frame)
        summary_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(summary_frame, text="Chapter Summary", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.summary_text = ctk.CTkTextbox(summary_frame, height=120,
                                         placeholder_text="Brief summary of what happens in this chapter")
        self.summary_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Key events
        events_frame = ctk.CTkFrame(self.details_frame)
        events_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(events_frame, text="Key Events", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.events_text = ctk.CTkTextbox(events_frame, height=120,
                                        placeholder_text="List the key events that happen in this chapter")
        self.events_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Characters involved
        characters_frame = ctk.CTkFrame(self.details_frame)
        characters_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(characters_frame, text="Characters Involved", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.characters_text = ctk.CTkTextbox(characters_frame, height=80,
                                            placeholder_text="List all characters that appear in this chapter")
        self.characters_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Setting
        setting_frame = ctk.CTkFrame(self.details_frame)
        setting_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(setting_frame, text="Setting", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.setting_text = ctk.CTkTextbox(setting_frame, height=80,
                                         placeholder_text="Where and when does this chapter take place?")
        self.setting_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Chapter purpose
        purpose_frame = ctk.CTkFrame(self.details_frame)
        purpose_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(purpose_frame, text="Chapter Purpose", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.purpose_text = ctk.CTkTextbox(purpose_frame, height=100,
                                         placeholder_text="What is the purpose of this chapter? How does it advance the plot?")
        self.purpose_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Conflict/Tension
        conflict_frame = ctk.CTkFrame(self.details_frame)
        conflict_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(conflict_frame, text="Conflict & Tension", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.conflict_text = ctk.CTkTextbox(conflict_frame, height=100,
                                          placeholder_text="What conflict or tension exists in this chapter?")
        self.conflict_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Word count goal
        wordcount_frame = ctk.CTkFrame(self.details_frame)
        wordcount_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(wordcount_frame, text="Word Count Goal", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        wordcount_input_frame = ctk.CTkFrame(wordcount_frame, fg_color="transparent")
        wordcount_input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ctk.CTkLabel(wordcount_input_frame, text="Target:").pack(side='left', padx=(0, 10))
        self.wordcount_entry = ctk.CTkEntry(wordcount_input_frame, placeholder_text="Target word count")
        self.wordcount_entry.pack(side='right', fill='x', expand=True)
        
        # Notes
        notes_frame = ctk.CTkFrame(self.details_frame)
        notes_frame.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(notes_frame, text="Additional Notes", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor='w', padx=10, pady=(10, 5))
        
        self.notes_text = ctk.CTkTextbox(notes_frame, height=100,
                                       placeholder_text="Any additional notes, ideas, or details")
        self.notes_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Load sample chapters
        self.load_sample_chapters()
        
    def load_sample_chapters(self):
        """Load some sample chapters"""
        sample_chapters = [
            {
                "number": "1",
                "title": "The Discovery",
                "pov": "Alex Morgan",
                "summary": "Alex discovers the abandoned warehouse where the crime took place and begins investigating.",
                "events": "1. Alex arrives at the warehouse\n2. Discovers evidence of a struggle\n3. Finds a mysterious note\n4. Meets Detective Sarah Chen",
                "characters": "Alex Morgan, Detective Sarah Chen",
                "setting": "Abandoned warehouse, late evening, dark and foreboding atmosphere",
                "purpose": "Introduce the protagonist, establish the central mystery, and set the tone for the story.",
                "conflict": "Alex is investigating a case that destroyed their career. They're risking everything to find the truth.",
                "wordcount": "3000",
                "notes": "This chapter sets up the main conflict and introduces the protagonist's determination."
            },
            {
                "number": "2",
                "title": "The Past Returns",
                "pov": "Alex Morgan",
                "summary": "Alex's past catches up with them as they try to piece together the evidence.",
                "events": "1. Alex reviews old case files\n2. Receives a threatening phone call\n3. Visits Dr. Vasquez for therapy\n4. Discovers a connection to their past",
                "characters": "Alex Morgan, Dr. Elena Vasquez, Unknown caller",
                "setting": "Alex's apartment, Dr. Vasquez's office, various locations",
                "purpose": "Develop Alex's character, introduce the threat, and reveal connections to the past.",
                "conflict": "Alex must confront their past trauma while dealing with new threats.",
                "wordcount": "3500",
                "notes": "Important character development chapter. Shows Alex's vulnerability and the stakes involved."
            },
            {
                "number": "3",
                "title": "The Confession",
                "pov": "Alex Morgan",
                "summary": "Alex has a breakthrough in therapy and makes a crucial discovery about the case.",
                "events": "1. Therapy session with Dr. Vasquez\n2. Alex opens up about their trauma\n3. Receives new information about the case\n4. Makes a connection between past and present",
                "characters": "Alex Morgan, Dr. Elena Vasquez",
                "setting": "Dr. Vasquez's office, afternoon, intimate and vulnerable atmosphere",
                "purpose": "Reveal Alex's emotional state, develop the relationship with Dr. Vasquez, and advance the plot.",
                "conflict": "Alex must trust Dr. Vasquez to help them process their trauma and solve the case.",
                "wordcount": "3200",
                "notes": "Emotional turning point for Alex. Shows their growth and the importance of trust."
            }
        ]
        
        for chapter in sample_chapters:
            self.chapters.append(chapter)
            self.chapter_listbox.insert(tk.END, f"Chapter {chapter['number']}: {chapter['title']}")
            
    def add_chapter(self):
        """Add a new chapter"""
        dialog = ctk.CTkInputDialog(text="Enter chapter number:", title="New Chapter")
        number = dialog.get_input()
        
        if number:
            new_chapter = {
                "number": number,
                "title": "",
                "pov": "",
                "summary": "",
                "events": "",
                "characters": "",
                "setting": "",
                "purpose": "",
                "conflict": "",
                "wordcount": "",
                "notes": ""
            }
            
            self.chapters.append(new_chapter)
            self.chapter_listbox.insert(tk.END, f"Chapter {number}: New Chapter")
            self.chapter_listbox.selection_clear(0, tk.END)
            self.chapter_listbox.selection_set(tk.END)
            self.select_chapter(None)
            
    def select_chapter(self, event):
        """Select a chapter from the list"""
        selection = self.chapter_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_chapter = index
            self.load_chapter_details(index)
            
    def load_chapter_details(self, index):
        """Load chapter details into the form"""
        if 0 <= index < len(self.chapters):
            chapter = self.chapters[index]
            
            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, chapter.get("number", ""))
            
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, chapter.get("title", ""))
            
            self.pov_entry.delete(0, tk.END)
            self.pov_entry.insert(0, chapter.get("pov", ""))
            
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert("1.0", chapter.get("summary", ""))
            
            self.events_text.delete("1.0", tk.END)
            self.events_text.insert("1.0", chapter.get("events", ""))
            
            self.characters_text.delete("1.0", tk.END)
            self.characters_text.insert("1.0", chapter.get("characters", ""))
            
            self.setting_text.delete("1.0", tk.END)
            self.setting_text.insert("1.0", chapter.get("setting", ""))
            
            self.purpose_text.delete("1.0", tk.END)
            self.purpose_text.insert("1.0", chapter.get("purpose", ""))
            
            self.conflict_text.delete("1.0", tk.END)
            self.conflict_text.insert("1.0", chapter.get("conflict", ""))
            
            self.wordcount_entry.delete(0, tk.END)
            self.wordcount_entry.insert(0, chapter.get("wordcount", ""))
            
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", chapter.get("notes", ""))
            
    def save_chapter(self):
        """Save current chapter details"""
        if self.current_chapter is not None:
            chapter = self.chapters[self.current_chapter]
            
            chapter["number"] = self.number_entry.get()
            chapter["title"] = self.title_entry.get()
            chapter["pov"] = self.pov_entry.get()
            chapter["summary"] = self.summary_text.get("1.0", tk.END).strip()
            chapter["events"] = self.events_text.get("1.0", tk.END).strip()
            chapter["characters"] = self.characters_text.get("1.0", tk.END).strip()
            chapter["setting"] = self.setting_text.get("1.0", tk.END).strip()
            chapter["purpose"] = self.purpose_text.get("1.0", tk.END).strip()
            chapter["conflict"] = self.conflict_text.get("1.0", tk.END).strip()
            chapter["wordcount"] = self.wordcount_entry.get()
            chapter["notes"] = self.notes_text.get("1.0", tk.END).strip()
            
            # Update listbox
            display_text = f"Chapter {chapter['number']}: {chapter['title']}" if chapter['title'] else f"Chapter {chapter['number']}: New Chapter"
            self.chapter_listbox.delete(self.current_chapter)
            self.chapter_listbox.insert(self.current_chapter, display_text)
            self.chapter_listbox.selection_set(self.current_chapter)
            
            messagebox.showinfo("Success", "Chapter saved successfully!")
            
    def edit_chapter(self):
        """Edit selected chapter"""
        if self.current_chapter is not None:
            self.save_chapter()
            
    def delete_chapter(self):
        """Delete selected chapter"""
        if self.current_chapter is not None:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this chapter?"):
                del self.chapters[self.current_chapter]
                self.chapter_listbox.delete(self.current_chapter)
                self.current_chapter = None
                self.clear_form()
                
    def move_chapter_up(self):
        """Move chapter up in the list"""
        if self.current_chapter is not None and self.current_chapter > 0:
            # Swap chapters
            self.chapters[self.current_chapter], self.chapters[self.current_chapter - 1] = \
                self.chapters[self.current_chapter - 1], self.chapters[self.current_chapter]
            
            # Update listbox
            self.refresh_listbox()
            self.chapter_listbox.selection_set(self.current_chapter - 1)
            self.current_chapter -= 1
            
    def move_chapter_down(self):
        """Move chapter down in the list"""
        if self.current_chapter is not None and self.current_chapter < len(self.chapters) - 1:
            # Swap chapters
            self.chapters[self.current_chapter], self.chapters[self.current_chapter + 1] = \
                self.chapters[self.current_chapter + 1], self.chapters[self.current_chapter]
            
            # Update listbox
            self.refresh_listbox()
            self.chapter_listbox.selection_set(self.current_chapter + 1)
            self.current_chapter += 1
            
    def refresh_listbox(self):
        """Refresh the chapter listbox"""
        self.chapter_listbox.delete(0, tk.END)
        for chapter in self.chapters:
            display_text = f"Chapter {chapter['number']}: {chapter['title']}" if chapter['title'] else f"Chapter {chapter['number']}: New Chapter"
            self.chapter_listbox.insert(tk.END, display_text)
            
    def clear_form(self):
        """Clear the chapter details form"""
        self.number_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.pov_entry.delete(0, tk.END)
        self.summary_text.delete("1.0", tk.END)
        self.events_text.delete("1.0", tk.END)
        self.characters_text.delete("1.0", tk.END)
        self.setting_text.delete("1.0", tk.END)
        self.purpose_text.delete("1.0", tk.END)
        self.conflict_text.delete("1.0", tk.END)
        self.wordcount_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
    def export_outline(self):
        """Export outline to file"""
        if not self.chapters:
            messagebox.showwarning("Warning", "No chapters to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Outline",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.chapters, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("Book Outline\n")
                        f.write("=" * 50 + "\n\n")
                        for chapter in self.chapters:
                            f.write(f"Chapter {chapter['number']}: {chapter['title']}\n")
                            f.write("-" * 30 + "\n")
                            for key, value in chapter.items():
                                if key not in ['number', 'title'] and value:
                                    f.write(f"{key.title()}: {value}\n")
                            f.write("\n")
                            
                messagebox.showinfo("Success", f"Outline exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export outline: {str(e)}")
                
    def get_chapters(self):
        """Get all chapters"""
        return self.chapters
        
    def get_chapter_by_number(self, number):
        """Get chapter by number"""
        for chapter in self.chapters:
            if chapter.get("number") == str(number):
                return chapter
        return None
import json
import os
from datetime import datetime
import re

class ChatMemory:
    def __init__(self, base_dir="chat_memories"):
        self.base_dir = base_dir
        self.memory_file = "chat_history.json"
        self.ensure_directories()
        self.chat_history = self.load_history()
    
    def ensure_directories(self):
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
    def load_history(self):
        history_path = os.path.join(self.base_dir, self.memory_file)
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"conversations": [], "keywords": {}}
        return {"conversations": [], "keywords": {}}
    
    def save_history(self):
        history_path = os.path.join(self.base_dir, self.memory_file)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, indent=2)
    
    def extract_keywords(self, text):
        # Simple keyword extraction (can be enhanced with NLP libraries)
        words = re.findall(r'\b\w+\b', text.lower())
        return list(set([w for w in words if len(w) > 3]))
    
    def save_conversation(self, messages, backup_name=None):
        timestamp = datetime.now().isoformat()
        conversation = {
            "timestamp": timestamp,
            "messages": messages,
            "id": len(self.chat_history["conversations"])
        }
        
        # Extract keywords from all messages
        all_text = " ".join([msg["content"] for msg in messages])
        keywords = self.extract_keywords(all_text)
        
        # Update keyword index
        for keyword in keywords:
            if keyword not in self.chat_history["keywords"]:
                self.chat_history["keywords"][keyword] = []
            self.chat_history["keywords"][keyword].append(conversation["id"])
        
        # Save to main history
        self.chat_history["conversations"].append(conversation)
        self.save_history()
        
        # Create backup text file if name provided
        if backup_name:
            backup_path = os.path.join(self.base_dir, f"{backup_name}.txt")
            with open(backup_path, 'w', encoding='utf-8') as f:
                for msg in messages:
                    f.write(f"{msg['role']}: {msg['content']}\n\n")
    
    def search_by_keywords(self, keywords):
        if not keywords:
            return []
        
        # Find conversation IDs that match any of the keywords
        matching_ids = set()
        for keyword in keywords:
            if keyword in self.chat_history["keywords"]:
                matching_ids.update(self.chat_history["keywords"][keyword])
        
        # Return matching conversations
        return [conv for conv in self.chat_history["conversations"]
                if conv["id"] in matching_ids]
    
    def get_recent_conversations(self, limit=5):
        return self.chat_history["conversations"][-limit:]
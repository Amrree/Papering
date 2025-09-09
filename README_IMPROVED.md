# 📚 AI Book Studio - Modern Edition

A comprehensive AI-powered book writing and management application built with Python and CustomTkinter. This modern version significantly improves upon the original with enhanced features, better UI/UX, and professional-grade functionality.

## 🚀 What's New in the Modern Edition

### ✨ Major Improvements

1. **Modern GUI Framework**: Upgraded from basic tkinter to CustomTkinter for a sleek, dark-themed interface
2. **Enhanced AI Chat**: Advanced conversation management with export capabilities and multiple AI personalities
3. **Professional Image Processing**: Improved image creation and analysis with better error handling
4. **Complete Project Management**: Full book project organization with characters, scenes, and chapters
5. **Export Functionality**: Multiple export formats for different publishing needs
6. **Better Code Architecture**: Cleaner, more maintainable code structure

### 🎯 Key Features

#### 🤖 AI Chat System
- **Multiple Personalities**: Choose from 9 different AI personalities including Professional, Creative, Book Editor, and Story Architect
- **Web Search Integration**: Toggle web search for real-time information
- **Conversation Export**: Export chats in TXT, JSON, or Markdown formats
- **Memory Management**: Save and load conversation history
- **Streaming Responses**: Real-time AI response streaming
- **Key Information Learning**: Save important information for quick access

#### 🖼️ Image Processing
- **AI Image Generation**: Create images with customizable styles, quality, and sizes
- **Image Analysis**: Upload and analyze images with detailed AI descriptions
- **Image Enhancement**: Rotate, enhance, and save images
- **Generation History**: Keep track of all generated images
- **Multiple Formats**: Support for PNG, JPG, and other image formats

#### 📖 Project Management
- **Character Database**: Comprehensive character profiles with physical descriptions, personality, background, goals, and relationships
- **Scene Management**: Detailed scene planning with setting, characters, purpose, and conflict
- **Chapter Outlines**: Complete chapter planning with summaries, events, and word count goals
- **Export Capabilities**: Export all project data in multiple formats

#### 🎨 Modern Interface
- **Dark Theme**: Professional dark interface that's easy on the eyes
- **Draggable Windows**: Move and resize panels as needed
- **Responsive Layout**: Adapts to different screen sizes
- **Intuitive Navigation**: Easy-to-use sidebar with organized tools
- **Status Indicators**: Real-time status updates for AI operations

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Ollama (for AI functionality)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Ollama
1. Download and install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the required models:
```bash
ollama pull llava
ollama pull llama2
```

### Run the Application
```bash
# Run the modern version
python modern_app.py

# Or run the original version
python app.py
```

## 📋 Requirements

```
Pillow==10.2.0
requests==2.31.0
customtkinter==5.2.2
tkinter-tooltip==2.1.0
markdown==3.5.1
weasyprint==60.2
ebooklib==0.18
```

## 🎮 How to Use

### Getting Started
1. **Launch the Application**: Run `python modern_app.py`
2. **Create a Project**: Click "New Project" in the sidebar
3. **Choose Your Tools**: Use the sidebar to access different features

### AI Chat
1. Select a personality mode from the dropdown
2. Type your message in the input area
3. Click "Send" or press Enter
4. Use "Learn Selected" to save important information
5. Export conversations using the "Export" button

### Image Processing
1. **Create Images**: Enter a prompt, choose style and quality, then click "Generate"
2. **Analyze Images**: Upload an image and click "Analyze" for detailed AI descriptions
3. **Manage History**: View and reuse previous generations

### Project Management
1. **Characters**: Add detailed character profiles with all necessary information
2. **Scenes**: Plan individual scenes with setting, purpose, and conflict
3. **Chapters**: Create comprehensive chapter outlines with summaries and goals
4. **Export**: Save your project data in various formats

## 🔧 Configuration

### AI Settings
- Access settings through the "Settings" button in the sidebar
- Configure Ollama server URL (default: http://localhost:11434)
- Select AI model (llava, llama2, codellama, mistral)

### Layout Management
- Drag and drop panels to reposition them
- Use the View menu to show/hide specific windows
- Save and load custom layouts

## 📁 Project Structure

```
/workspace/
├── modern_app.py              # Main modern application
├── app.py                     # Original application
├── frames/
│   ├── modern_chat_frame.py   # Enhanced chat interface
│   ├── modern_create_image_frame.py  # Image generation
│   ├── modern_read_image_frame.py    # Image analysis
│   ├── characters_frame.py    # Character management
│   ├── scenes_frame.py        # Scene planning
│   ├── outline_frame.py       # Chapter outlines
│   └── chat_memory.py         # Memory management
├── requirements.txt           # Dependencies
└── README_IMPROVED.md        # This file
```

## 🎨 AI Personalities

1. **Default**: Standard AI assistant
2. **Professional**: Formal, business-oriented responses
3. **Friendly**: Warm, conversational tone
4. **Creative**: Imaginative, inspiring responses
5. **Concise**: Brief, direct answers
6. **Crone**: Mystical, tarot-focused responses
7. **Sign Language**: Responses with sign language symbols
8. **Book Editor**: Experienced editor with detailed feedback
9. **Story Architect**: Master story planner and developer

## 📊 Export Formats

### Chat Export
- **TXT**: Plain text format
- **JSON**: Structured data with metadata
- **Markdown**: Formatted for documentation

### Project Export
- **JSON**: Complete project data
- **TXT**: Human-readable format
- **PDF**: Professional document format (coming soon)
- **EPUB**: E-book format (coming soon)

## 🚧 Roadmap

### Completed ✅
- [x] Modern GUI with CustomTkinter
- [x] Enhanced AI chat system
- [x] Improved image processing
- [x] Character management
- [x] Scene planning
- [x] Chapter outlines
- [x] Export functionality
- [x] Memory management

### In Progress 🔄
- [ ] PDF export functionality
- [ ] EPUB export functionality
- [ ] Advanced layout management
- [ ] Comprehensive settings system

### Planned 📋
- [ ] Real-time collaboration
- [ ] Cloud synchronization
- [ ] Advanced AI models integration
- [ ] Plugin system
- [ ] Mobile companion app

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **CustomTkinter**: For the beautiful modern GUI framework
- **Ollama**: For providing the AI models
- **Pillow**: For image processing capabilities
- **The Python Community**: For the amazing ecosystem

## 📞 Support

If you encounter any issues or have questions:
1. Check the documentation above
2. Review the code comments
3. Submit an issue on the project repository
4. Join our community discussions

---

**Made with ❤️ by the AI Book Studio Team**

*Transform your writing process with the power of AI and modern design.*
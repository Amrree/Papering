"""
Export utilities for AI Book Studio
Provides functionality to export projects in various formats
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
import markdown
from weasyprint import HTML, CSS
from ebooklib import epub

class ProjectExporter:
    """Handles exporting book projects in various formats"""
    
    def __init__(self):
        self.supported_formats = ['json', 'txt', 'html', 'pdf', 'epub']
        
    def export_project(self, project_data: Dict[str, Any], format_type: str, output_path: str) -> bool:
        """
        Export project data in the specified format
        
        Args:
            project_data: Dictionary containing all project data
            format_type: Export format (json, txt, html, pdf, epub)
            output_path: Path where to save the exported file
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            if format_type == 'json':
                return self._export_json(project_data, output_path)
            elif format_type == 'txt':
                return self._export_txt(project_data, output_path)
            elif format_type == 'html':
                return self._export_html(project_data, output_path)
            elif format_type == 'pdf':
                return self._export_pdf(project_data, output_path)
            elif format_type == 'epub':
                return self._export_epub(project_data, output_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            print(f"Export error: {str(e)}")
            return False
            
    def _export_json(self, project_data: Dict[str, Any], output_path: str) -> bool:
        """Export project as JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JSON export error: {str(e)}")
            return False
            
    def _export_txt(self, project_data: Dict[str, Any], output_path: str) -> bool:
        """Export project as plain text"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("AI Book Studio - Project Export\n")
                f.write("=" * 50 + "\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Project info
                if 'project_info' in project_data:
                    f.write("PROJECT INFORMATION\n")
                    f.write("-" * 20 + "\n")
                    for key, value in project_data['project_info'].items():
                        f.write(f"{key.title()}: {value}\n")
                    f.write("\n")
                
                # Characters
                if 'characters' in project_data and project_data['characters']:
                    f.write("CHARACTERS\n")
                    f.write("-" * 10 + "\n")
                    for i, char in enumerate(project_data['characters'], 1):
                        f.write(f"{i}. {char.get('name', 'Unnamed Character')}\n")
                        for key, value in char.items():
                            if key != 'name' and value:
                                f.write(f"   {key.title()}: {value}\n")
                        f.write("\n")
                
                # Chapters
                if 'chapters' in project_data and project_data['chapters']:
                    f.write("CHAPTER OUTLINE\n")
                    f.write("-" * 15 + "\n")
                    for chapter in project_data['chapters']:
                        f.write(f"Chapter {chapter.get('number', '?')}: {chapter.get('title', 'Untitled')}\n")
                        for key, value in chapter.items():
                            if key not in ['number', 'title'] and value:
                                f.write(f"   {key.title()}: {value}\n")
                        f.write("\n")
                
                # Scenes
                if 'scenes' in project_data and project_data['scenes']:
                    f.write("SCENES\n")
                    f.write("-" * 6 + "\n")
                    for i, scene in enumerate(project_data['scenes'], 1):
                        f.write(f"{i}. {scene.get('title', 'Untitled Scene')}\n")
                        for key, value in scene.items():
                            if key != 'title' and value:
                                f.write(f"   {key.title()}: {value}\n")
                        f.write("\n")
                        
            return True
        except Exception as e:
            print(f"TXT export error: {str(e)}")
            return False
            
    def _export_html(self, project_data: Dict[str, Any], output_path: str) -> bool:
        """Export project as HTML"""
        try:
            html_content = self._generate_html_content(project_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"HTML export error: {str(e)}")
            return False
            
    def _export_pdf(self, project_data: Dict[str, Any], output_path: str) -> bool:
        """Export project as PDF"""
        try:
            html_content = self._generate_html_content(project_data)
            
            # Create PDF from HTML
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(output_path)
            return True
        except Exception as e:
            print(f"PDF export error: {str(e)}")
            return False
            
    def _export_epub(self, project_data: Dict[str, Any], output_path: str) -> bool:
        """Export project as EPUB"""
        try:
            book = epub.EpubBook()
            
            # Set metadata
            book.set_identifier('ai-book-studio-project')
            book.set_title(project_data.get('project_info', {}).get('name', 'AI Book Studio Project'))
            book.set_language('en')
            book.add_author('AI Book Studio User')
            
            # Create chapters
            if 'chapters' in project_data:
                for chapter_data in project_data['chapters']:
                    chapter = epub.EpubHtml(
                        title=f"Chapter {chapter_data.get('number', '?')}: {chapter_data.get('title', 'Untitled')}",
                        file_name=f"chapter_{chapter_data.get('number', '0')}.xhtml",
                        lang='en'
                    )
                    
                    # Create chapter content
                    content = f"<h1>Chapter {chapter_data.get('number', '?')}: {chapter_data.get('title', 'Untitled')}</h1>"
                    
                    for key, value in chapter_data.items():
                        if key not in ['number', 'title'] and value:
                            content += f"<h2>{key.title()}</h2><p>{value}</p>"
                    
                    chapter.content = content
                    book.add_item(chapter)
                    book.toc.append(chapter)
            
            # Add characters section
            if 'characters' in project_data and project_data['characters']:
                characters_chapter = epub.EpubHtml(
                    title="Characters",
                    file_name="characters.xhtml",
                    lang='en'
                )
                
                content = "<h1>Characters</h1>"
                for char in project_data['characters']:
                    content += f"<h2>{char.get('name', 'Unnamed Character')}</h2>"
                    for key, value in char.items():
                        if key != 'name' and value:
                            content += f"<p><strong>{key.title()}:</strong> {value}</p>"
                
                characters_chapter.content = content
                book.add_item(characters_chapter)
                book.toc.append(characters_chapter)
            
            # Add default NCX and Nav file
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Define CSS style
            style = '''
            body {
                font-family: Georgia, serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }
            h2 {
                color: #666;
                margin-top: 30px;
            }
            p {
                margin-bottom: 15px;
            }
            '''
            
            nav_css = epub.EpubItem(
                uid="nav_css",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(nav_css)
            
            # Write the EPUB file
            epub.write_epub(output_path, book, {})
            return True
            
        except Exception as e:
            print(f"EPUB export error: {str(e)}")
            return False
            
    def _generate_html_content(self, project_data: Dict[str, Any]) -> str:
        """Generate HTML content for the project"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>AI Book Studio - Project Export</title>
            <style>
                body {{
                    font-family: Georgia, serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    border-bottom: 3px solid #333;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #666;
                    margin-top: 30px;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 5px;
                }}
                h3 {{
                    color: #888;
                    margin-top: 20px;
                }}
                p {{
                    margin-bottom: 15px;
                }}
                .meta {{
                    background-color: #f0f0f0;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .character, .chapter, .scene {{
                    background-color: #fafafa;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #333;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>AI Book Studio - Project Export</h1>
                <div class="meta">
                    <p><strong>Export Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Project info
        if 'project_info' in project_data:
            html += "<h2>Project Information</h2>"
            for key, value in project_data['project_info'].items():
                html += f"<p><strong>{key.title()}:</strong> {value}</p>"
        
        # Characters
        if 'characters' in project_data and project_data['characters']:
            html += "<h2>Characters</h2>"
            for char in project_data['characters']:
                html += f'<div class="character">'
                html += f"<h3>{char.get('name', 'Unnamed Character')}</h3>"
                for key, value in char.items():
                    if key != 'name' and value:
                        html += f"<p><strong>{key.title()}:</strong> {value}</p>"
                html += "</div>"
        
        # Chapters
        if 'chapters' in project_data and project_data['chapters']:
            html += "<h2>Chapter Outline</h2>"
            for chapter in project_data['chapters']:
                html += f'<div class="chapter">'
                html += f"<h3>Chapter {chapter.get('number', '?')}: {chapter.get('title', 'Untitled')}</h3>"
                for key, value in chapter.items():
                    if key not in ['number', 'title'] and value:
                        html += f"<p><strong>{key.title()}:</strong> {value}</p>"
                html += "</div>"
        
        # Scenes
        if 'scenes' in project_data and project_data['scenes']:
            html += "<h2>Scenes</h2>"
            for scene in project_data['scenes']:
                html += f'<div class="scene">'
                html += f"<h3>{scene.get('title', 'Untitled Scene')}</h3>"
                for key, value in scene.items():
                    if key != 'title' and value:
                        html += f"<p><strong>{key.title()}:</strong> {value}</p>"
                html += "</div>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html

def create_sample_project_data() -> Dict[str, Any]:
    """Create sample project data for testing"""
    return {
        'project_info': {
            'name': 'Mystery Novel',
            'author': 'AI Book Studio User',
            'created': datetime.now().isoformat(),
            'description': 'A thrilling mystery novel about a detective solving a complex case.'
        },
        'characters': [
            {
                'name': 'Alex Morgan',
                'age': '28',
                'gender': 'Non-binary',
                'role': 'Protagonist',
                'physical': 'Tall and lean with short, curly brown hair and piercing green eyes.',
                'personality': 'Intelligent, curious, and determined. Has a dry sense of humor.',
                'background': 'Former journalist turned detective.',
                'goals': 'Wants to solve the mystery that destroyed their career.',
                'relationships': 'Close with their former editor Sarah.',
                'notes': 'Has a photographic memory and excellent observation skills.'
            }
        ],
        'chapters': [
            {
                'number': '1',
                'title': 'The Discovery',
                'pov': 'Alex Morgan',
                'summary': 'Alex discovers the abandoned warehouse where the crime took place.',
                'events': '1. Alex arrives at the warehouse\n2. Discovers evidence\n3. Finds a mysterious note',
                'characters': 'Alex Morgan, Detective Sarah Chen',
                'setting': 'Abandoned warehouse, late evening',
                'purpose': 'Introduce the protagonist and establish the central mystery.',
                'conflict': 'Alex is investigating a case that destroyed their career.',
                'wordcount': '3000',
                'notes': 'Sets up the main conflict and introduces the protagonist.'
            }
        ],
        'scenes': [
            {
                'title': 'The Discovery',
                'chapter': '1',
                'number': '1',
                'type': 'Action',
                'pov': 'Alex Morgan',
                'location': 'Abandoned warehouse',
                'time': 'Late evening',
                'mood': 'Dark and foreboding',
                'characters': 'Alex Morgan, Detective Sarah Chen',
                'content': 'Alex pushes open the creaking door to the warehouse...',
                'purpose': 'Introduce the protagonist and the central mystery.',
                'conflict': 'Alex is investigating a case that destroyed their career.',
                'notes': 'This scene sets up the main conflict.'
            }
        ]
    }

# Example usage
if __name__ == "__main__":
    exporter = ProjectExporter()
    sample_data = create_sample_project_data()
    
    # Test exports
    print("Testing exports...")
    
    # JSON export
    if exporter.export_project(sample_data, 'json', 'test_project.json'):
        print("✅ JSON export successful")
    
    # TXT export
    if exporter.export_project(sample_data, 'txt', 'test_project.txt'):
        print("✅ TXT export successful")
    
    # HTML export
    if exporter.export_project(sample_data, 'html', 'test_project.html'):
        print("✅ HTML export successful")
    
    # PDF export
    if exporter.export_project(sample_data, 'pdf', 'test_project.pdf'):
        print("✅ PDF export successful")
    
    # EPUB export
    if exporter.export_project(sample_data, 'epub', 'test_project.epub'):
        print("✅ EPUB export successful")
    
    print("All exports completed!")
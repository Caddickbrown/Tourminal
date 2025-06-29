#!/usr/bin/env python3
"""
Daily Journal GUI - CustomTkinter-based Journal Application
A modern GUI version of the daily journal with enhanced cross-platform compatibility.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, scrolledtext
import os
import json
import re
from datetime import datetime, timedelta
import subprocess
import platform

# Set appearance mode and color theme
ctk.set_appearance_mode("system")  # Modes: "system" (standard), "dark", "light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Configuration - reuse from original
JOURNAL_DIR = os.path.expanduser("~/journal/daily")
SETTINGS_FILE = os.path.expanduser("~/.daily_journal_customtkinter_settings.json")
BACKUP_DIR = os.path.expanduser("~/journal/backups")

DEFAULT_SETTINGS = {
    "journal_directory": JOURNAL_DIR,
    "backup_directory": BACKUP_DIR,
    "default_editor": "nano",
    "date_format": "%Y-%m-%d",
    "auto_save": True,
    "auto_backup": True,
    "auto_detect_tags": True,
    "tag_prefixes": ["#", "@"],
    "merge_detected_tags": True,
    "window_width": 1000,
    "window_height": 700,
    "font_family": "Consolas",
    "font_size": 12,
    "appearance_mode": "system",
    "color_theme": "blue"
}

def load_settings():
    """Load settings from file"""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return {**DEFAULT_SETTINGS, **json.load(f)}
    except:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        pass

def ensure_directories():
    """Ensure journal and backup directories exist"""
    settings = load_settings()
    os.makedirs(settings["journal_directory"], exist_ok=True)
    os.makedirs(settings["backup_directory"], exist_ok=True)

def get_today_filename():
    """Get filename for today's journal"""
    settings = load_settings()
    date_str = datetime.now().strftime(settings["date_format"])
    return f"{date_str}.md"

def get_daily_files():
    """Get list of daily journal files"""
    ensure_directories()
    settings = load_settings() 
    try:
        files = [f for f in os.listdir(settings["journal_directory"]) if f.endswith('.md')]
        return sorted(files, reverse=True)
    except:
        return []

def read_daily_file(filename):
    """Read a daily journal file"""
    settings = load_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def write_daily_file(filename, content):
    """Write content to a daily journal file"""
    settings = load_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def append_to_daily_file(filename, entry_content):
    """Append a new entry to a daily journal file"""
    existing_content = read_daily_file(filename)
    if existing_content:
        new_content = existing_content + "\n\n" + entry_content
    else:
        new_content = entry_content
    write_daily_file(filename, new_content)

def extract_tags_from_content(content, tag_prefixes=None):
    """Extract tags from content using specified prefixes"""
    if not content:
        return []
    if tag_prefixes is None:
        settings = load_settings()
        tag_prefixes = settings.get("tag_prefixes", ["#", "@"])
    
    tags = set()
    lines = content.split('\n')
    
    for line in lines:
        words = line.split()
        for word in words:
            for prefix in tag_prefixes:
                if word.startswith(prefix):
                    tag = word[len(prefix):].rstrip('.,;:!?')
                    if tag and any(c.isalnum() for c in tag):
                        tags.add(tag.lower())
                    break
    return sorted(list(tags))

def format_timestamp():
    """Get formatted timestamp for entries"""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

class EntryDialog(ctk.CTkToplevel):
    """Dialog for creating/editing journal entries"""
    
    def __init__(self, parent, title="New Entry", content="", tags="", entry_title=""):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry("900x700")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")
        
        self.create_widgets(entry_title, tags, content)
        
        # Focus on title entry
        self.title_entry.focus_set()
        
        # Wait for window to close
        self.wait_window()
    
    def create_widgets(self, entry_title, tags, content):
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Entry Title:", font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.title_entry = ctk.CTkEntry(main_frame, placeholder_text="Enter entry title...", height=35)
        self.title_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.title_entry.insert(0, entry_title)
        
        # Tags
        tags_label = ctk.CTkLabel(main_frame, text="Tags:", font=ctk.CTkFont(size=14, weight="bold"))
        tags_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        tags_frame = ctk.CTkFrame(main_frame)
        tags_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="Enter tags separated by spaces...", height=35)
        self.tags_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.tags_entry.insert(0, tags)
        
        self.auto_detect_btn = ctk.CTkButton(tags_frame, text="Auto-Detect", command=self.auto_detect_tags, width=100)
        self.auto_detect_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Content
        content_label = ctk.CTkLabel(main_frame, text="Content:", font=ctk.CTkFont(size=14, weight="bold"))
        content_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.content_text = ctk.CTkTextbox(main_frame, height=400)
        self.content_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.content_text.insert("1.0", content)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.save_btn = ctk.CTkButton(button_frame, text="Save Entry", command=self.save_entry, fg_color="green")
        self.save_btn.pack(side="right", padx=(5, 0), pady=10)
        
        self.cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, fg_color="gray")
        self.cancel_btn.pack(side="right", padx=(5, 0), pady=10)
        
        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_entry())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def auto_detect_tags(self):
        """Auto-detect tags from content"""
        content = self.content_text.get("1.0", "end-1c")
        detected_tags = extract_tags_from_content(content)
        
        if detected_tags:
            current_tags = self.tags_entry.get()
            if current_tags:
                # Merge with existing tags
                existing_tags = set(current_tags.split())
                all_tags = existing_tags.union(detected_tags)
                self.tags_entry.delete(0, "end")
                self.tags_entry.insert(0, " ".join(sorted(all_tags)))
            else:
                self.tags_entry.delete(0, "end")
                self.tags_entry.insert(0, " ".join(detected_tags))
            
            messagebox.showinfo("Tags Detected", f"Found tags: {', '.join(detected_tags)}")
        else:
            messagebox.showinfo("No Tags", "No tags detected in content.")
    
    def save_entry(self):
        """Save the entry"""
        title = self.title_entry.get().strip()
        tags = self.tags_entry.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        
        if not content:
            messagebox.showerror("Error", "Content cannot be empty.")
            return
        
        # Only use explicitly entered tags, not auto-detected ones
        settings = load_settings()
        if settings.get("auto_detect_tags", True):
            detected_tags = extract_tags_from_content(content)
            if detected_tags:
                # Show tag detection feedback but don't add them to tags
                messagebox.showinfo("Tags Detected", 
                    f"Auto-detected tags in content: {', '.join(detected_tags)}\n"
                    f"Explicitly entered tags: {tags}\n"
                    f"Note: Auto-detected tags remain in content, only explicit tags appear at bottom.")
        
        # Format entry with only explicitly entered tags at the end
        timestamp = format_timestamp()
        entry_lines = []
        
        if title:
            entry_lines.append(f"# {title}")
            entry_lines.append("")
        
        entry_lines.append(f"{timestamp}{content}")
        
        # Add only explicitly entered tags at the end
        if tags:
            tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
            if tag_list:
                entry_lines.append("")
                entry_lines.append(f"{' '.join([f'@{tag}' for tag in tag_list])}")
        
        entry_content = "\n".join(entry_lines)
        
        self.result = {
            "title": title,
            "tags": tags,
            "content": content,
            "entry_content": entry_content
        }
        
        self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.destroy()

class SearchDialog(ctk.CTkToplevel):
    """Dialog for searching journal entries"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Search Entries")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        # Search input
        search_label = ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=14, weight="bold"))
        search_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter search terms...", height=35)
        self.search_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Search options
        options_frame = ctk.CTkFrame(search_frame)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.case_sensitive_var = ctk.BooleanVar()
        self.case_sensitive_check = ctk.CTkCheckBox(options_frame, text="Case Sensitive", variable=self.case_sensitive_var)
        self.case_sensitive_check.pack(side="left", padx=10, pady=10)
        
        self.search_btn = ctk.CTkButton(options_frame, text="Search", command=self.perform_search, fg_color="blue")
        self.search_btn.pack(side="right", padx=10, pady=10)
        
        # Results
        results_label = ctk.CTkLabel(main_frame, text="Results:", font=ctk.CTkFont(size=14, weight="bold"))
        results_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Results frame
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Results listbox with scrollbar
        self.results_listbox = ctk.CTkScrollableFrame(results_frame)
        self.results_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        self.view_btn = ctk.CTkButton(button_frame, text="View Selected", command=self.view_selected, fg_color="green")
        self.view_btn.pack(side="right", padx=(5, 0), pady=10)
        
        self.close_btn = ctk.CTkButton(button_frame, text="Close", command=self.close_dialog, fg_color="gray")
        self.close_btn.pack(side="right", padx=(5, 0), pady=10)
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        self.search_results = []
    
    def close_dialog(self):
        """Close the search dialog"""
        self.destroy()
    
    def perform_search(self):
        """Perform the search"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        # Clear previous results
        for widget in self.results_listbox.winfo_children():
            widget.destroy()
        
        self.search_results = []
        settings = load_settings()
        
        # Search through all journal files
        files = get_daily_files()
        for filename in files:
            content = read_daily_file(filename)
            if content:
                entries = self.parse_entries_from_content(content, filename)
                for entry in entries:
                    search_text = f"{entry['title']} {entry['content']} {entry['tags']}".lower()
                    if not self.case_sensitive_var.get():
                        search_text = search_text.lower()
                        query = query.lower()
                    
                    if query in search_text:
                        self.search_results.append(entry)
        
        # Display results
        if self.search_results:
            for i, entry in enumerate(self.search_results):
                result_frame = ctk.CTkFrame(self.results_listbox)
                result_frame.pack(fill="x", padx=5, pady=2)
                
                # Title and date
                title_text = f"{entry['title']} - {entry['date']}"
                title_label = ctk.CTkLabel(result_frame, text=title_text, font=ctk.CTkFont(size=12, weight="bold"))
                title_label.pack(anchor="w", padx=10, pady=(5, 2))
                
                # Preview
                preview = entry['content'][:100] + "..." if len(entry['content']) > 100 else entry['content']
                preview_label = ctk.CTkLabel(result_frame, text=preview, font=ctk.CTkFont(size=10))
                preview_label.pack(anchor="w", padx=10, pady=(0, 5))
                
                # Tags
                if entry['tags']:
                    tags_label = ctk.CTkLabel(result_frame, text=f"Tags: {entry['tags']}", font=ctk.CTkFont(size=9))
                    tags_label.pack(anchor="w", padx=10, pady=(0, 5))
        else:
            no_results_label = ctk.CTkLabel(self.results_listbox, text="No results found.", font=ctk.CTkFont(size=12))
            no_results_label.pack(pady=20)
    
    def parse_entries_from_content(self, content, filename):
        """Parse individual entries from file content"""
        entries = []
        lines = content.split('\n')
        current_entry = {"title": "", "content": "", "tags": "", "date": filename.replace('.md', '')}
        
        for line in lines:
            if line.startswith('[20') and ']' in line:  # Timestamp line
                if current_entry["content"]:  # Save previous entry
                    # Extract tags from the end of content
                    content_text = current_entry["content"].strip()
                    tags = self.extract_tags_from_end_of_content(content_text)
                    current_entry["content"] = content_text
                    current_entry["tags"] = tags
                    entries.append(current_entry.copy())
                    current_entry = {"title": "", "content": "", "tags": "", "date": filename.replace('.md', '')}
                
                # Extract content after timestamp
                timestamp_end = line.find(']') + 1
                content_part = line[timestamp_end:].strip()
                if content_part:
                    current_entry["content"] = content_part
            elif line.startswith('# ') and not current_entry["title"]:
                current_entry["title"] = line[2:].strip()
            elif line.strip() and not line.startswith('**Tags:**'):
                if current_entry["content"]:
                    current_entry["content"] += "\n" + line
                else:
                    current_entry["content"] = line
        
        # Add last entry
        if current_entry["content"]:
            # Extract tags from the end of content
            content_text = current_entry["content"].strip()
            tags = self.extract_tags_from_end_of_content(content_text)
            current_entry["content"] = content_text
            current_entry["tags"] = tags
            entries.append(current_entry)
        
        return entries
    
    def extract_tags_from_end_of_content(self, content):
        """Extract tags from the end of content in @tag format"""
        if not content:
            return ""
        
        lines = content.split('\n')
        tags = []
        
        # Look for @tags at the end of the content
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line contains @tags
            words = line.split()
            line_tags = []
            for word in words:
                if word.startswith('@'):
                    tag = word[1:].rstrip('.,;:!?')
                    if tag and any(c.isalnum() for c in tag):
                        line_tags.append(tag.lower())
            
            if line_tags:
                # Found tags, add them and stop looking
                tags.extend(reversed(line_tags))  # Reverse to maintain order
                break
            elif line.startswith('#'):
                # Found a header, stop looking
                break
            else:
                # This line doesn't contain tags, stop looking
                break
        
        return ", ".join(reversed(tags))  # Reverse again to get original order
    
    def view_selected(self):
        """View the selected result"""
        # For simplicity, show the first result
        if self.search_results:
            entry = self.search_results[0]  # In a real app, you'd track selection
            self.parent.show_file_content(entry['date'] + '.md', entry['content'], readonly=True)
        else:
            messagebox.showinfo("Info", "No result selected.")

class SettingsDialog(ctk.CTkToplevel):
    """Dialog for application settings"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")
        
        self.settings = load_settings()
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame with scrollbar
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Journal Directory
        dir_label = ctk.CTkLabel(main_frame, text="Journal Directory:", font=ctk.CTkFont(size=14, weight="bold"))
        dir_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        dir_frame = ctk.CTkFrame(main_frame)
        dir_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.dir_entry = ctk.CTkEntry(dir_frame, height=35)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        self.dir_entry.insert(0, self.settings["journal_directory"])
        
        self.browse_btn = ctk.CTkButton(dir_frame, text="Browse", command=self.browse_journal_dir, width=80)
        self.browse_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Backup Directory
        backup_label = ctk.CTkLabel(main_frame, text="Backup Directory:", font=ctk.CTkFont(size=14, weight="bold"))
        backup_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.backup_entry = ctk.CTkEntry(main_frame, height=35)
        self.backup_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.backup_entry.insert(0, self.settings["backup_directory"])
        
        # Default Editor
        editor_label = ctk.CTkLabel(main_frame, text="Default Editor:", font=ctk.CTkFont(size=14, weight="bold"))
        editor_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.editor_entry = ctk.CTkEntry(main_frame, height=35)
        self.editor_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.editor_entry.insert(0, self.settings["default_editor"])
        
        # Date Format
        date_label = ctk.CTkLabel(main_frame, text="Date Format:", font=ctk.CTkFont(size=14, weight="bold"))
        date_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.date_entry = ctk.CTkEntry(main_frame, height=35)
        self.date_entry.pack(fill="x", padx=10, pady=(0, 10))
        self.date_entry.insert(0, self.settings["date_format"])
        
        # Checkboxes
        self.auto_save_var = ctk.BooleanVar(value=self.settings["auto_save"])
        self.auto_save_check = ctk.CTkCheckBox(main_frame, text="Auto Save", variable=self.auto_save_var)
        self.auto_save_check.pack(anchor="w", padx=10, pady=5)
        
        self.auto_backup_var = ctk.BooleanVar(value=self.settings["auto_backup"])
        self.auto_backup_check = ctk.CTkCheckBox(main_frame, text="Auto Backup", variable=self.auto_backup_var)
        self.auto_backup_check.pack(anchor="w", padx=10, pady=5)
        
        self.auto_detect_tags_var = ctk.BooleanVar(value=self.settings["auto_detect_tags"])
        self.auto_detect_tags_check = ctk.CTkCheckBox(main_frame, text="Auto Detect Tags", variable=self.auto_detect_tags_var)
        self.auto_detect_tags_check.pack(anchor="w", padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(20, 0))
        
        self.save_btn = ctk.CTkButton(button_frame, text="Save Settings", command=self.save_settings, fg_color="green")
        self.save_btn.pack(side="right", padx=(5, 0), pady=10)
        
        self.reset_btn = ctk.CTkButton(button_frame, text="Reset to Defaults", command=self.reset_to_defaults, fg_color="orange")
        self.reset_btn.pack(side="right", padx=(5, 0), pady=10)
        
        self.cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.cancel, fg_color="gray")
        self.cancel_btn.pack(side="right", padx=(5, 0), pady=10)
    
    def browse_journal_dir(self):
        """Browse for journal directory"""
        directory = filedialog.askdirectory(initialdir=self.settings["journal_directory"])
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
    
    def save_settings(self):
        """Save the settings"""
        self.settings.update({
            "journal_directory": self.dir_entry.get(),
            "backup_directory": self.backup_entry.get(),
            "default_editor": self.editor_entry.get(),
            "date_format": self.date_entry.get(),
            "auto_save": self.auto_save_var.get(),
            "auto_backup": self.auto_backup_var.get(),
            "auto_detect_tags": self.auto_detect_tags_var.get()
        })
        
        save_settings(self.settings)
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.destroy()
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()
        save_settings(self.settings)
        messagebox.showinfo("Success", "Settings reset to defaults!")
        self.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.destroy()

class DailyJournalCustomTkinter(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Daily Journal - CustomTkinter")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Load settings
        self.settings = load_settings()
        
        # Set appearance
        ctk.set_appearance_mode(self.settings.get("appearance_mode", "system"))
        ctk.set_default_color_theme(self.settings.get("color_theme", "blue"))
        
        # Create widgets
        self.create_widgets()
        
        # Initial load
        self.refresh_file_list()
        self.update_status()
        
        # Bind closing event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - File list
        left_panel = ctk.CTkFrame(self, width=300)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        left_panel.grid_propagate(False)
        
        # File list title
        file_title = ctk.CTkLabel(left_panel, text="Journal Files", font=ctk.CTkFont(size=16, weight="bold"))
        file_title.pack(pady=10)
        
        # File list with scrollbar
        self.file_listbox = ctk.CTkScrollableFrame(left_panel, height=400)
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store filename references
        self.file_frames = {}
        
        # Right panel - Main content
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Quick Actions
        actions_title = ctk.CTkLabel(right_panel, text="Quick Actions", font=ctk.CTkFont(size=16, weight="bold"))
        actions_title.pack(pady=10)
        
        # Quick action buttons
        actions_frame = ctk.CTkFrame(right_panel)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Button grid
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        self.new_entry_btn = ctk.CTkButton(actions_frame, text="New Entry", command=self.new_entry, height=40)
        self.new_entry_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.edit_today_btn = ctk.CTkButton(actions_frame, text="Edit Today", command=self.edit_today, height=40)
        self.edit_today_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.search_btn = ctk.CTkButton(actions_frame, text="Search", command=self.search_entries, height=40)
        self.search_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.view_btn = ctk.CTkButton(actions_frame, text="View Selected", command=self.view_selected_file, height=40)
        self.view_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.edit_btn = ctk.CTkButton(actions_frame, text="Edit Selected", command=self.edit_selected_file, height=40)
        self.edit_btn.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.external_btn = ctk.CTkButton(actions_frame, text="External Editor", command=self.open_external_editor, height=40)
        self.external_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        
        # Status bar
        self.status_label = ctk.CTkLabel(right_panel, text="Ready", font=ctk.CTkFont(size=10))
        self.status_label.pack(side="bottom", pady=10)
        
        # Menu button
        menu_btn = ctk.CTkButton(right_panel, text="Settings", command=self.show_settings, width=100)
        menu_btn.pack(side="bottom", pady=5)
    
    def update_status(self):
        """Update status bar"""
        files = get_daily_files()
        today_file = get_today_filename()
        has_today = today_file in files
        
        status_text = f"Files: {len(files)} | Today: {'✓' if has_today else '✗'}"
        self.status_label.configure(text=status_text)
    
    def refresh_file_list(self):
        """Refresh the file list"""
        # Clear existing widgets
        for widget in self.file_listbox.winfo_children():
            widget.destroy()
        
        # Clear filename references
        self.file_frames.clear()
        
        files = get_daily_files()
        today_file = get_today_filename()
        
        for filename in files:
            # Create frame for each file
            file_frame = ctk.CTkFrame(self.file_listbox)
            file_frame.pack(fill="x", padx=5, pady=2)
            
            # File name with today indicator
            display_name = filename.replace('.md', '')
            if filename == today_file:
                display_name += " (Today)"
            
            file_label = ctk.CTkLabel(file_frame, text=display_name, font=ctk.CTkFont(size=12))
            file_label.pack(anchor="w", padx=10, pady=5)
            
            # Store filename for reference
            self.file_frames[file_frame] = filename
    
    def new_entry(self):
        """Create a new journal entry"""
        dialog = EntryDialog(self, "New Entry")
        if dialog.result:
            today_file = get_today_filename()
            append_to_daily_file(today_file, dialog.result["entry_content"])
            self.refresh_file_list()
            self.update_status()
            messagebox.showinfo("Success", "Entry added successfully!")
    
    def view_selected_file(self):
        """View the selected file"""
        # For simplicity, show the most recent file
        files = get_daily_files()
        if files:
            filename = files[0]
            content = read_daily_file(filename)
            self.show_file_content(filename, content, readonly=True)
        else:
            messagebox.showinfo("Info", "No files available.")
    
    def edit_selected_file(self):
        """Edit the selected file"""
        # For simplicity, edit the most recent file
        files = get_daily_files()
        if files:
            filename = files[0]
            content = read_daily_file(filename)
            self.show_file_content(filename, content, readonly=False)
        else:
            messagebox.showinfo("Info", "No files available.")
    
    def edit_today(self):
        """Edit today's journal"""
        today_file = get_today_filename()
        content = read_daily_file(today_file)
        self.show_file_content(today_file, content, readonly=False)
    
    def show_file_content(self, filename, content, readonly=False):
        """Show file content in a dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"{'View' if readonly else 'Edit'}: {filename}")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        
        # Center the window
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"800x600+{x}+{y}")
        
        # Content text area
        text_area = ctk.CTkTextbox(dialog, height=500)
        text_area.pack(fill="both", expand=True, padx=20, pady=20)
        text_area.insert("1.0", content)
        
        if readonly:
            text_area.configure(state="disabled")
        else:
            # Save button
            def save_file():
                new_content = text_area.get("1.0", "end-1c")
                write_daily_file(filename, new_content)
                messagebox.showinfo("Success", "File saved successfully!")
                dialog.destroy()
            
            save_btn = ctk.CTkButton(dialog, text="Save", command=save_file, fg_color="green")
            save_btn.pack(pady=10)
    
    def search_entries(self):
        """Open search dialog"""
        SearchDialog(self)
    
    def open_external_editor(self):
        """Open external editor"""
        files = get_daily_files()
        if not files:
            messagebox.showinfo("Info", "No files available.")
            return
        
        filename = files[0]  # Most recent file
        filepath = os.path.join(self.settings["journal_directory"], filename)
        
        try:
            subprocess.Popen([self.settings["default_editor"], filepath])
            messagebox.showinfo("Success", f"Opened {filename} in {self.settings['default_editor']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open editor: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self)
    
    def on_closing(self):
        """Handle window closing"""
        self.quit()

def main():
    """Main function"""
    ensure_directories()
    app = DailyJournalCustomTkinter()
    app.mainloop()

if __name__ == "__main__":
    main() 
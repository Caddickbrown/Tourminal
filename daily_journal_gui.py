#!/usr/bin/env python3
"""
Daily Journal GUI - Tkinter-based Journal Application
A GUI version of the daily journal with core functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import json
import re
from datetime import datetime, timedelta
import subprocess
import platform

# Configuration - reuse from original
JOURNAL_DIR = os.path.expanduser("~/journal/daily")
SETTINGS_FILE = os.path.expanduser("~/.daily_journal_gui_settings.json")
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
    "window_width": 900,
    "window_height": 700,
    "font_family": "Consolas",
    "font_size": 11
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

class EntryDialog:
    """Dialog for creating/editing journal entries"""
    
    def __init__(self, parent, title="New Entry", content="", tags="", entry_title=""):
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets(entry_title, tags, content)
        
    def create_widgets(self, entry_title, tags, content):
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title field
        ttk.Label(main_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value=entry_title or f"{format_timestamp()}")
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, font=("Consolas", 10))
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Tags field
        ttk.Label(main_frame, text="Tags:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.tags_var = tk.StringVar(value=tags)
        self.tags_entry = ttk.Entry(main_frame, textvariable=self.tags_var, font=("Consolas", 10))
        self.tags_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Content area label
        ttk.Label(main_frame, text="Content:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Content text area
        self.content_text = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 11),
            undo=True,
            maxundo=50
        )
        self.content_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.content_text.insert(tk.END, content)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=self.save_entry).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Auto-Detect Tags", command=self.auto_detect_tags).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Focus on content area
        self.content_text.focus_set()
        
        # Bind Enter key to save (Ctrl+Enter)
        self.window.bind('<Control-Return>', lambda e: self.save_entry())
        self.window.bind('<Control-s>', lambda e: self.save_entry())
        
    def auto_detect_tags(self):
        """Auto-detect tags from content"""
        content = self.content_text.get(1.0, tk.END)
        detected_tags = extract_tags_from_content(content)
        
        if detected_tags:
            current_tags = self.tags_var.get()
            if current_tags:
                # Merge tags
                existing_tags = [tag.strip().lower() for tag in current_tags.split(',') if tag.strip()]
                all_tags = existing_tags + detected_tags
                unique_tags = []
                seen = set()
                for tag in all_tags:
                    if tag not in seen:
                        unique_tags.append(tag)
                        seen.add(tag)
                self.tags_var.set(", ".join(unique_tags))
            else:
                self.tags_var.set(", ".join(detected_tags))
            
            messagebox.showinfo("Tags Detected", f"Found tags: {', '.join(detected_tags)}")
        else:
            messagebox.showinfo("No Tags Found", "No tags detected in content.")
    
    def save_entry(self):
        """Save the entry"""
        title = self.title_var.get().strip()
        tags = self.tags_var.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()
        
        if not title:
            messagebox.showerror("Error", "Please enter a title.")
            return
            
        self.result = {
            'title': title,
            'tags': tags,
            'content': content
        }
        self.window.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.window.destroy()

class SearchDialog:
    """Dialog for searching journal entries"""
    
    def __init__(self, parent):
        self.result = None
        self.window = tk.Toplevel(parent)
        self.window.title("Search Entries")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"700x500+{x}+{y}")
        
        self.create_widgets()
        self.search_results = []
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Search field
        ttk.Label(main_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(main_frame, textvariable=self.search_var, font=("Consolas", 10))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        search_entry.bind('<Return>', lambda e: self.perform_search())
        
        # Search button
        ttk.Button(main_frame, text="Search", command=self.perform_search).grid(row=0, column=2, padx=(5, 0), pady=(0, 10))
        
        # Results label
        self.results_label = ttk.Label(main_frame, text="Enter search term and press Search")
        self.results_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Results listbox with scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.results_listbox = tk.Listbox(list_frame, font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.results_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Double-click to view
        self.results_listbox.bind('<Double-Button-1>', lambda e: self.view_selected())
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="View Entry", command=self.view_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=self.close).pack(side=tk.RIGHT)
        
        # Focus on search entry
        search_entry.focus_set()
    
    def perform_search(self):
        """Perform the search"""
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return
        
        self.search_results = []
        files = get_daily_files()
        
        for filename in files:
            content = read_daily_file(filename)
            entries = self.parse_entries_from_content(content, filename)
            
            for entry in entries:
                searchable_text = f"{entry['title']} {entry['tags']} {entry['content']}".lower()
                if search_term in searchable_text:
                    self.search_results.append(entry)
        
        # Update results display
        self.results_listbox.delete(0, tk.END)
        
        if self.search_results:
            self.results_label.config(text=f"Found {len(self.search_results)} matching entries:")
            for i, entry in enumerate(self.search_results):
                date_part = entry['filename'].replace('.md', '')
                title_part = entry['title'][:50]
                if len(entry['title']) > 50:
                    title_part += "..."
                display_text = f"{date_part} - {title_part}"
                self.results_listbox.insert(tk.END, display_text)
        else:
            self.results_label.config(text=f"No entries found matching '{search_term}'")
    
    def parse_entries_from_content(self, content, filename):
        """Parse individual entries from daily file content"""
        entries = []
        if not content.strip():
            return entries
        
        lines = content.split('\n')
        current_entry = None
        current_content = []
        
        for line in lines:
            if line.strip().startswith('# '):
                # Save previous entry
                if current_entry:
                    current_entry['content'] = '\n'.join(current_content).strip()
                    entries.append(current_entry)
                
                # Start new entry
                title = line[2:].strip()
                current_entry = {
                    'filename': filename,
                    'title': title,
                    'tags': '',
                    'content': '',
                    'entry_index': len(entries)
                }
                current_content = []
                
            elif current_entry and line.strip().startswith('tags:'):
                current_entry['tags'] = line[5:].strip()
            elif current_entry:
                current_content.append(line)
        
        # Add the last entry
        if current_entry:
            current_entry['content'] = '\n'.join(current_content).strip()
            entries.append(current_entry)
        
        return entries
    
    def view_selected(self):
        """View the selected search result"""
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an entry to view.")
            return
        
        entry = self.search_results[selection[0]]
        self.result = entry
        self.window.destroy()
    
    def close(self):
        """Close the search dialog"""
        self.window.destroy()

class SettingsDialog:
    """Dialog for application settings"""
    
    def __init__(self, parent):
        self.settings = load_settings()
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Journal Directory
        ttk.Label(main_frame, text="Journal Directory:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.journal_dir_var = tk.StringVar(value=self.settings["journal_directory"])
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        dir_frame.columnconfigure(0, weight=1)
        ttk.Entry(dir_frame, textvariable=self.journal_dir_var, font=("Consolas", 9)).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="Browse", command=self.browse_journal_dir).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        # Date Format
        ttk.Label(main_frame, text="Date Format:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.date_format_var = tk.StringVar(value=self.settings["date_format"])
        ttk.Entry(main_frame, textvariable=self.date_format_var, font=("Consolas", 9)).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Font Settings
        ttk.Label(main_frame, text="Font Family:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.font_family_var = tk.StringVar(value=self.settings["font_family"])
        font_combo = ttk.Combobox(main_frame, textvariable=self.font_family_var, 
                                 values=["Consolas", "Courier New", "Arial", "Times New Roman"])
        font_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        ttk.Label(main_frame, text="Font Size:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.font_size_var = tk.StringVar(value=str(self.settings["font_size"]))
        ttk.Entry(main_frame, textvariable=self.font_size_var, font=("Consolas", 9)).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Tag Prefixes
        ttk.Label(main_frame, text="Tag Prefixes:").grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        self.tag_prefixes_var = tk.StringVar(value=", ".join(self.settings["tag_prefixes"]))
        ttk.Entry(main_frame, textvariable=self.tag_prefixes_var, font=("Consolas", 9)).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        # Checkboxes
        self.auto_detect_tags_var = tk.BooleanVar(value=self.settings["auto_detect_tags"])
        ttk.Checkbutton(main_frame, text="Auto-detect tags", variable=self.auto_detect_tags_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        row += 1
        
        self.merge_detected_tags_var = tk.BooleanVar(value=self.settings["merge_detected_tags"])
        ttk.Checkbutton(main_frame, text="Merge detected tags with existing", variable=self.merge_detected_tags_var).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        self.auto_backup_var = tk.BooleanVar(value=self.settings["auto_backup"])
        ttk.Checkbutton(main_frame, text="Auto backup", variable=self.auto_backup_var).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row+1, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
    
    def browse_journal_dir(self):
        """Browse for journal directory"""
        directory = filedialog.askdirectory(initialdir=self.journal_dir_var.get())
        if directory:
            self.journal_dir_var.set(directory)
    
    def save_settings(self):
        """Save the settings"""
        try:
            self.settings["journal_directory"] = self.journal_dir_var.get()
            self.settings["date_format"] = self.date_format_var.get()
            self.settings["font_family"] = self.font_family_var.get()
            self.settings["font_size"] = int(self.font_size_var.get())
            
            # Parse tag prefixes
            tag_prefixes = [tag.strip() for tag in self.tag_prefixes_var.get().split(',') if tag.strip()]
            self.settings["tag_prefixes"] = tag_prefixes
            
            self.settings["auto_detect_tags"] = self.auto_detect_tags_var.get()
            self.settings["merge_detected_tags"] = self.merge_detected_tags_var.get()
            self.settings["auto_backup"] = self.auto_backup_var.get()
            
            save_settings(self.settings)
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Confirm", "Reset all settings to defaults?"):
            self.settings = DEFAULT_SETTINGS.copy()
            save_settings(self.settings)
            messagebox.showinfo("Success", "Settings reset to defaults!")
            self.window.destroy()
    
    def cancel(self):
        """Cancel settings dialog"""
        self.window.destroy()

class DailyJournalGUI:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Daily Journal")
        self.settings = load_settings()
        
        # Set window size from settings
        width = self.settings.get("window_width", 900)
        height = self.settings.get("window_height", 700)
        self.root.geometry(f"{width}x{height}")
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.create_widgets()
        self.create_menu()
        self.refresh_file_list()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Ensure directories exist
        ensure_directories()
    
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Entry", command=self.new_entry, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Open External Editor", command=self.open_external_editor, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Search", command=self.search_entries, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Settings", command=self.show_settings, accelerator="Ctrl+,")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.new_entry())
        self.root.bind_all("<Control-o>", lambda e: self.open_external_editor())
        self.root.bind_all("<Control-f>", lambda e: self.search_entries())
        self.root.bind_all("<Control-comma>", lambda e: self.show_settings())
        self.root.bind_all("<Control-q>", lambda e: self.on_closing())
    
    def create_widgets(self):
        """Create the main application widgets"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - file list
        left_frame = ttk.LabelFrame(main_frame, text="Journal Files", padding="5")
        left_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # File list
        self.file_listbox = tk.Listbox(left_frame, width=25, font=("Consolas", 9))
        file_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=file_scrollbar.set)
        
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # File list buttons
        file_button_frame = ttk.Frame(left_frame)
        file_button_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(file_button_frame, text="View", command=self.view_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_button_frame, text="Edit", command=self.edit_selected_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_button_frame, text="Refresh", command=self.refresh_file_list).pack(side=tk.LEFT)
        
        # Bind double-click to view file
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.view_selected_file())
        
        # Right panel - quick actions
        right_frame = ttk.LabelFrame(main_frame, text="Quick Actions", padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        
        # Action buttons
        ttk.Button(right_frame, text="📝 New Entry", command=self.new_entry, width=20).pack(pady=2, fill=tk.X)
        ttk.Button(right_frame, text="✏️ Edit Today", command=self.edit_today, width=20).pack(pady=2, fill=tk.X)
        ttk.Button(right_frame, text="🔍 Search", command=self.search_entries, width=20).pack(pady=2, fill=tk.X)
        ttk.Button(right_frame, text="⚙️ Settings", command=self.show_settings, width=20).pack(pady=2, fill=tk.X)
        
        # Status area
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="5")
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame, 
            height=10, 
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_status()
    
    def update_status(self):
        """Update the status display"""
        files = get_daily_files()
        total_files = len(files)
        
        today_file = get_today_filename()
        today_exists = today_file in files
        
        status_info = [
            "📊 Journal Statistics",
            f"Total files: {total_files}",
            f"Today's file: {today_file}",
            f"Today's file exists: {'Yes' if today_exists else 'No'}",
            "",
            "🚀 Getting Started:",
            "• Click 'New Entry' to create your first journal entry",
            "• Use Ctrl+N for quick entry creation",
            "• Double-click files in the list to view them",
            "• Use the Search function to find specific entries",
            "",
            "💡 Tips:",
            "• Tags starting with # or @ are auto-detected",
            "• Use Ctrl+O to open external editor",
            "• All entries from the same day go in one file",
        ]
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "\n".join(status_info))
        self.status_text.config(state=tk.DISABLED)
    
    def refresh_file_list(self):
        """Refresh the file list"""
        self.file_listbox.delete(0, tk.END)
        files = get_daily_files()
        
        for filename in files:
            # Add some basic info about each file
            filepath = os.path.join(self.settings["journal_directory"], filename)
            try:
                stat = os.stat(filepath)
                size_kb = stat.st_size // 1024
                display_name = f"{filename} ({size_kb}KB)"
                self.file_listbox.insert(tk.END, display_name)
            except:
                self.file_listbox.insert(tk.END, filename)
        
        self.update_status()
    
    def new_entry(self):
        """Create a new journal entry"""
        dialog = EntryDialog(self.root, "New Journal Entry")
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            entry_data = dialog.result
            
            # Auto-detect tags if enabled
            if self.settings.get("auto_detect_tags", True):
                detected_tags = extract_tags_from_content(entry_data['content'])
                if detected_tags and self.settings.get("merge_detected_tags", True):
                    existing_tags = [tag.strip() for tag in entry_data['tags'].split(',') if tag.strip()]
                    all_tags = existing_tags + detected_tags
                    unique_tags = []
                    seen = set()
                    for tag in all_tags:
                        if tag.lower() not in seen:
                            unique_tags.append(tag)
                            seen.add(tag.lower())
                    entry_data['tags'] = ", ".join(unique_tags)
            
            # Format entry content
            entry_content = f"# {entry_data['title']}\n\ntags: {entry_data['tags']}\n\n{entry_data['content']}\n"
            
            # Save to today's file
            today_file = get_today_filename()
            append_to_daily_file(today_file, entry_content)
            
            # Refresh UI
            self.refresh_file_list()
            messagebox.showinfo("Success", f"Entry saved to {today_file}")
    
    def view_selected_file(self):
        """View the selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to view.")
            return
        
        # Extract filename from display name
        display_name = self.file_listbox.get(selection[0])
        filename = display_name.split(' (')[0]  # Remove size info
        
        content = read_daily_file(filename)
        self.show_file_content(filename, content, readonly=True)
    
    def edit_selected_file(self):
        """Edit the selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to edit.")
            return
        
        # Extract filename from display name
        display_name = self.file_listbox.get(selection[0])
        filename = display_name.split(' (')[0]  # Remove size info
        
        content = read_daily_file(filename)
        self.show_file_content(filename, content, readonly=False)
    
    def edit_today(self):
        """Edit today's journal file"""
        today_file = get_today_filename()
        content = read_daily_file(today_file)
        self.show_file_content(today_file, content, readonly=False)
    
    def show_file_content(self, filename, content, readonly=False):
        """Show file content in a new window"""
        window = tk.Toplevel(self.root)
        window.title(f"{'View' if readonly else 'Edit'} - {filename}")
        window.geometry("800x600")
        
        # Center the window
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (800 // 2)
        y = (window.winfo_screenheight() // 2) - (600 // 2)
        window.geometry(f"800x600+{x}+{y}")
        
        main_frame = ttk.Frame(window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Text area
        text_widget = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=(self.settings.get("font_family", "Consolas"), self.settings.get("font_size", 11)),
            undo=True,
            maxundo=50,
            state=tk.DISABLED if readonly else tk.NORMAL
        )
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Insert content
        if readonly:
            text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, content)
        if readonly:
            text_widget.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0)
        
        if not readonly:
            def save_file():
                new_content = text_widget.get(1.0, tk.END).rstrip()
                write_daily_file(filename, new_content)
                messagebox.showinfo("Success", f"File {filename} saved successfully!")
                self.refresh_file_list()
            
            ttk.Button(button_frame, text="Save", command=save_file).pack(side=tk.LEFT, padx=(0, 5))
            window.bind('<Control-s>', lambda e: save_file())
        
        ttk.Button(button_frame, text="Close", command=window.destroy).pack(side=tk.RIGHT)
        
        # Focus on text area
        text_widget.focus_set()
    
    def search_entries(self):
        """Search journal entries"""
        dialog = SearchDialog(self.root)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            entry = dialog.result
            # Show the found entry
            full_content = f"# {entry['title']}\n"
            if entry['tags']:
                full_content += f"\ntags: {entry['tags']}\n"
            full_content += f"\n{entry['content']}"
            
            self.show_file_content(f"Search Result: {entry['title']}", full_content, readonly=True)
    
    def open_external_editor(self):
        """Open today's file in external editor"""
        today_file = get_today_filename()
        settings = load_settings()
        editor = settings.get("default_editor", "nano")
        
        # Ensure file exists
        filepath = os.path.join(settings["journal_directory"], today_file)
        if not os.path.exists(filepath):
            # Create empty file
            write_daily_file(today_file, "# New Entry\n\ntags: \n\n")
        
        try:
            if platform.system() == "Windows":
                if editor == "nano":
                    editor = "notepad.exe"
                subprocess.Popen([editor, filepath])
            else:
                subprocess.Popen([editor, filepath])
            
            messagebox.showinfo("External Editor", f"Opened {today_file} in {editor}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open external editor: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self.root)
        # Refresh settings after dialog closes
        self.settings = load_settings()
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About Daily Journal",
            "Daily Journal GUI v1.0\n\n"
            "A simple journal application with GUI interface.\n\n"
            "Features:\n"
            "• Create and edit journal entries\n"
            "• Search through entries\n"
            "• Auto-tag detection\n"
            "• External editor support\n\n"
            "Keyboard Shortcuts:\n"
            "• Ctrl+N: New Entry\n"
            "• Ctrl+O: External Editor\n"
            "• Ctrl+F: Search\n"
            "• Ctrl+,: Settings"
        )
    
    def on_closing(self):
        """Handle application closing"""
        # Save window size
        self.settings["window_width"] = self.root.winfo_width()
        self.settings["window_height"] = self.root.winfo_height()
        save_settings(self.settings)
        
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = DailyJournalGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
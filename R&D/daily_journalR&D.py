import curses
import os
import subprocess
import platform
import json
import time
from datetime import datetime

JOURNAL_DIR = os.path.expanduser("~/journal/daily")
SETTINGS_FILE = os.path.expanduser("~/.daily_journal_settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "journal_directory": JOURNAL_DIR,
    "default_editor": "nano",
    "date_format": "%Y-%m-%d",
    "filename_format": "daily",
    "auto_save": True
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

def get_settings():
    """Get current settings"""
    return load_settings()

def ensure_journal_dir():
    settings = get_settings()
    os.makedirs(settings["journal_directory"], exist_ok=True)

def get_daily_files():
    """Get list of daily journal files"""
    ensure_journal_dir()
    settings = get_settings()
    try:
        files = [f for f in os.listdir(settings["journal_directory"]) if f.endswith('.md')]
        return sorted(files, reverse=True)  # Most recent first
    except Exception as e:
        # Return empty list if there's an error, but this shouldn't happen since ensure_journal_dir() creates the directory
        return []

def get_today_filename():
    """Get filename for today's journal"""
    settings = get_settings()
    date_str = datetime.now().strftime(settings["date_format"])
    return f"{date_str}.md"

def read_daily_file(filename):
    """Read a daily journal file and return its content"""
    settings = get_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
    except FileNotFoundError:
        return f"File not found: {filepath}\n\nPlease check if the file exists and the journal directory is correct."
    except PermissionError:
        return f"Permission denied: {filepath}\n\nPlease check file permissions."
    except UnicodeDecodeError as e:
        return f"Encoding error reading file: {e}\n\nFile may be corrupted or use a different encoding."
    except Exception as e:
        return f"Error reading file: {e}\n\nFilepath: {filepath}"

def write_daily_file(filename, content):
    """Write content to a daily journal file"""
    settings = get_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def append_to_daily_file(filename, entry_content):
    """Append a new entry to a daily journal file"""
    settings = get_settings()
    filepath = os.path.join(settings["journal_directory"], filename)
    
    # Read existing content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    except:
        existing_content = ""
    
    # Add new entry
    if existing_content:
        new_content = existing_content + "\n\n" + entry_content
    else:
        new_content = entry_content
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

def debug_key_codes(stdscr):
    """Debug function to identify key codes"""
    stdscr.clear()
    stdscr.addstr(0, 0, "Press keys to see their codes (ESC to exit):")
    stdscr.addstr(2, 0, "Key Code:")
    
    while True:
        key = stdscr.getch()
        if key == 27:  # ESC
            break
        stdscr.addstr(2, 10, f"{key} (0x{key:02x})")
        stdscr.refresh()

def is_enter_key(key):
    """Check if the key is any form of enter key"""
    return key in (10, 13, 459, curses.KEY_ENTER, ord('\r'))

def is_selection_key(key):
    """Check if the key is a selection key (Enter or Space)"""
    return key in (10, 13, 459, curses.KEY_ENTER, ord('\r'), 32)  # Enter or Space

def write_in_terminal(stdscr, title, tags):
    """Write entry content directly in the terminal"""
    curses.noecho()  # Don't echo characters automatically
    curses.curs_set(1)
    
    # Clear the screen and show header
    stdscr.clear()
    stdscr.addstr(0, 0, f"Writing: {title}")
    stdscr.addstr(1, 0, "Start typing your entry (Ctrl+D when finished):")
    
    # Get the content
    content_lines = []
    current_line = ""
    y_pos = 2
    x_pos = 0  # Track cursor position within the line
    
    def redraw_current_line():
        """Redraw the current line and position cursor"""
        # Clear the current line
        stdscr.move(y_pos, 0)
        stdscr.clrtoeol()
        # Redraw the line
        stdscr.addstr(y_pos, 0, current_line)
        # Position cursor at the correct position
        stdscr.move(y_pos, x_pos)
        stdscr.refresh()
    
    # Initial cursor position
    stdscr.move(y_pos, x_pos)
    stdscr.refresh()
    
    while True:
        try:
            char = stdscr.getch()
            
            if char == 4:  # Ctrl+D
                if current_line:
                    content_lines.append(current_line)
                break
            elif is_enter_key(char):  # Enter (regular or numpad)
                content_lines.append(current_line)
                current_line = ""
                y_pos += 1
                x_pos = 0
                redraw_current_line()
            elif char == 127 or char == 8:  # Backspace
                if x_pos > 0:
                    x_pos -= 1
                    current_line = current_line[:x_pos] + current_line[x_pos+1:]
                    redraw_current_line()
            elif char == curses.KEY_LEFT:
                if x_pos > 0:
                    x_pos -= 1
                    stdscr.move(y_pos, x_pos)
                    stdscr.refresh()
            elif char == curses.KEY_RIGHT:
                if x_pos < len(current_line):
                    x_pos += 1
                    stdscr.move(y_pos, x_pos)
                    stdscr.refresh()
            else:
                # Only add printable characters
                if 32 <= char <= 126:
                    # Insert character at cursor position
                    current_line = current_line[:x_pos] + chr(char) + current_line[x_pos:]
                    x_pos += 1
                    redraw_current_line()
                
        except KeyboardInterrupt:
            break
    
    curses.curs_set(0)
    
    return "\n".join(content_lines)

def input_with_prefill(stdscr, y, x, prefill):
    curses.curs_set(1)
    win = stdscr
    
    def redraw_buffer():
        """Redraw the entire buffer and position cursor"""
        win.move(y, x)
        win.clrtoeol()
        win.addstr(y, x, ''.join(buffer))
        win.move(y, x + pos)
        win.refresh()
    
    buffer = list(prefill)
    pos = len(prefill)
    redraw_buffer()
    
    while True:
        win.move(y, x + pos)
        win.refresh()
        key = win.getch()
        if key in (10, 13, 459):  # Enter
            break
        elif key in (curses.KEY_LEFT, 260):
            if pos > 0:
                pos -= 1
                win.move(y, x + pos)
        elif key in (curses.KEY_RIGHT, 261):
            if pos < len(buffer):
                pos += 1
                win.move(y, x + pos)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if pos > 0:
                del buffer[pos-1]
                pos -= 1
                redraw_buffer()
        elif key == curses.KEY_DC:
            if pos < len(buffer):
                del buffer[pos]
                redraw_buffer()
        elif 32 <= key <= 126:
            buffer.insert(pos, chr(key))
            pos += 1
            redraw_buffer()
        # Optionally: handle Home/End
        elif key == curses.KEY_HOME:
            pos = 0
            win.move(y, x + pos)
        elif key == curses.KEY_END:
            pos = len(buffer)
            win.move(y, x + pos)
    curses.curs_set(0)
    return ''.join(buffer)

def new_entry(stdscr, use_editor=False):
    ensure_journal_dir()
    curses.echo()
    stdscr.clear()
    
    # Prefill title with current date and time
    current_datetime = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    default_title = f"{current_datetime}"
    
    stdscr.addstr(0, 0, "Title: ")
    title = input_with_prefill(stdscr, 0, 13, default_title)
    if not title.strip():  # If user just presses enter, use default
        title = default_title
    
    stdscr.addstr(1, 0, "Tags (comma separated): ")
    tags = input_with_prefill(stdscr, 1, 25, "")
    curses.noecho()

    # Get today's filename
    today_file = get_today_filename()
    
    if use_editor:
        # For editor mode, we'll append to the daily file
        entry_content = f"# {title}\n\ntags: {tags}\n\n"
        append_to_daily_file(today_file, entry_content)
        
        stdscr.addstr(3, 0, "Press any key to open editor...")
        stdscr.getch()
        curses.endwin()
        
        # Open the daily file in editor
        settings = get_settings()
        editor = settings["default_editor"]
        if platform.system() == "Windows" and editor == "nano":
            editor = "notepad.exe"
        
        filepath = os.path.join(settings["journal_directory"], today_file)
        subprocess.call([editor, filepath])
    else:
        # Write content in terminal
        content = write_in_terminal(stdscr, title, tags)
        
        # Create the entry content
        entry_content = f"# {title}\n\ntags: {tags}\n\n{content}\n"
        
        # Append to today's file
        append_to_daily_file(today_file, entry_content)
        
        # Show success message with countdown
        for i in range(5, 0, -1):
            stdscr.clear()
            stdscr.addstr(0, 0, f"Entry added to: {today_file}")
            stdscr.addstr(2, 0, f"Continuing in {i} seconds... (Press any key to continue now)")
            stdscr.refresh()
            
            # Check for key press with timeout
            stdscr.timeout(1000)  # 1 second timeout
            key = stdscr.getch()
            if key != -1:  # Key was pressed
                break
        
        # Reset timeout
        stdscr.timeout(-1)

def display_daily_content(stdscr, filename, content):
    """Display daily journal content within the curses interface"""
    height, width = stdscr.getmaxyx()
    
    # Enable keypad on main screen
    stdscr.keypad(True)
    
    # Split content into lines
    lines = content.split('\n')
    
    # Debug: Show content info
    if not content.strip():
        stdscr.clear()
        stdscr.addstr(0, 0, f"File: {filename}")
        stdscr.addstr(1, 0, "This file appears to be empty.")
        stdscr.addstr(3, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    # Create a scrollable window
    content_height = height - 4
    content_width = width - 4
    content_win = curses.newwin(content_height, content_width, 2, 2)
    content_win.box()
    content_win.addstr(0, 2, f" {filename} ")
    
    # Enable keypad for special keys
    content_win.keypad(True)
    
    # Display instructions
    content_win.addstr(1, 1, "Use arrow keys to scroll, ESC to return")
    
    # Display content starting from line 2
    start_line = 0
    while True:
        content_win.clear()
        content_win.box()
        content_win.addstr(0, 2, f" {filename} ")
        content_win.addstr(1, 1, "Use arrow keys to scroll, ESC to return")
        
        # Display visible lines
        for i in range(content_height - 2):
            if start_line + i < len(lines):
                line = lines[start_line + i]
                # Truncate line if too long
                if len(line) > content_width - 2:
                    line = line[:content_width - 5] + "..."
                content_win.addstr(i + 2, 1, line)
        
        # Show scroll indicator
        if start_line > 0:
            content_win.addstr(1, content_width - 3, "↑")
        if start_line + content_height - 2 < len(lines):
            content_win.addstr(content_height - 1, content_width - 3, "↓")
        
        # Refresh the content window
        content_win.refresh()
        
        # Handle input from content window (not main screen)
        key = content_win.getch()
        
        if key == curses.KEY_UP:
            if start_line > 0:
                start_line -= 1
        elif key == curses.KEY_DOWN:
            if start_line + content_height - 2 < len(lines):
                start_line += 1
        elif key == curses.KEY_PPAGE:
            if start_line > 0:
                start_line = max(0, start_line - content_height + 2)
        elif key == curses.KEY_NPAGE:
            if start_line + content_height - 2 < len(lines):
                start_line = min(len(lines) - content_height + 2, start_line + content_height - 2)
        elif key == 27:  # ESC
            break

def edit_daily_file(stdscr, filename, content):
    """Edit daily journal file within the curses interface"""
    height, width = stdscr.getmaxyx()
    
    # Split content into lines and handle empty content
    if not content.strip():
        lines = [""]
    else:
        lines = content.split('\n')
    
    # Create an editable window
    edit_height = height - 4
    edit_width = width - 4
    edit_win = curses.newwin(edit_height, edit_width, 2, 2)
    edit_win.box()
    edit_win.addstr(0, 2, f" Editing: {filename} ")
    edit_win.addstr(1, 1, "Ctrl+S to save, Ctrl+Q to quit without saving")
    
    # Enable keypad for special keys
    edit_win.keypad(True)
    curses.echo()
    curses.curs_set(1)
    
    # Current cursor position in the text
    cursor_line = 0
    cursor_col = 0
    
    # Display offset (for scrolling)
    display_start = 0
    
    def is_word_char(char):
        """Check if character is part of a word"""
        return char.isalnum() or char == '_'
    
    def find_word_start(line, col):
        """Find the start of the word at or before the given column"""
        if col == 0:
            return 0
        if col >= len(line):
            col = len(line) - 1
        
        # If we're in the middle of a word, find its start
        if is_word_char(line[col]):
            while col > 0 and is_word_char(line[col - 1]):
                col -= 1
            return col
        else:
            # Find the previous word
            while col > 0 and not is_word_char(line[col - 1]):
                col -= 1
            while col > 0 and is_word_char(line[col - 1]):
                col -= 1
            return col
    
    def find_word_end(line, col):
        """Find the end of the word at or after the given column"""
        if col >= len(line):
            return len(line)
        
        # If we're in the middle of a word, find its end
        if is_word_char(line[col]):
            while col < len(line) and is_word_char(line[col]):
                col += 1
            return col
        else:
            # Find the next word
            while col < len(line) and not is_word_char(line[col]):
                col += 1
            return col
    
    def redraw_editor():
        """Redraw the entire editor content"""
        edit_win.clear()
        edit_win.box()
        edit_win.addstr(0, 2, f" Editing: {filename} ")
        edit_win.addstr(1, 1, "Ctrl+S to save, Ctrl+Q to quit without saving")
        
        # Display visible lines
        for i in range(edit_height - 2):
            line_idx = display_start + i
            if line_idx < len(lines):
                line = lines[line_idx]
                # Truncate line if too long
                if len(line) > edit_width - 2:
                    line = line[:edit_width - 5] + "..."
                edit_win.addstr(i + 2, 1, line)
        
        # Position cursor
        cursor_display_line = cursor_line - display_start + 2
        if 2 <= cursor_display_line < edit_height:
            edit_win.move(cursor_display_line, min(cursor_col + 1, edit_width - 2))
        
        edit_win.refresh()
    
    redraw_editor()
    
    while True:
        try:
            key = edit_win.getch()
            
            if key == 19:  # Ctrl+S
                # Save the file
                write_daily_file(filename, '\n'.join(lines))
                break
            elif key == 17:  # Ctrl+Q
                # Quit without saving
                break
            elif key == curses.KEY_UP:
                if cursor_line > 0:
                    cursor_line -= 1
                    cursor_col = min(cursor_col, len(lines[cursor_line]))
                    # Adjust display if needed
                    if cursor_line < display_start:
                        display_start = cursor_line
                    redraw_editor()
            elif key == curses.KEY_DOWN:
                if cursor_line < len(lines) - 1:
                    cursor_line += 1
                    cursor_col = min(cursor_col, len(lines[cursor_line]))
                    # Adjust display if needed
                    if cursor_line >= display_start + edit_height - 2:
                        display_start = cursor_line - edit_height + 3
                    redraw_editor()
            elif key == curses.KEY_LEFT:
                if cursor_col > 0:
                    cursor_col -= 1
                    redraw_editor()
            elif key == curses.KEY_RIGHT:
                if cursor_col < len(lines[cursor_line]):
                    cursor_col += 1
                    redraw_editor()
            elif key == 23:  # Ctrl+W (word navigation)
                # Move to previous word
                if cursor_col > 0:
                    cursor_col = find_word_start(lines[cursor_line], cursor_col)
                    redraw_editor()
            elif key == 24:  # Ctrl+X (word navigation)
                # Move to next word
                if cursor_col < len(lines[cursor_line]):
                    cursor_col = find_word_end(lines[cursor_line], cursor_col)
                    redraw_editor()
            elif key == 1:  # Ctrl+A (line navigation)
                # Move to start of line
                cursor_col = 0
                redraw_editor()
            elif key == 5:  # Ctrl+E (line navigation)
                # Move to end of line
                cursor_col = len(lines[cursor_line])
                redraw_editor()
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if cursor_col > 0:
                    # Delete character before cursor
                    lines[cursor_line] = lines[cursor_line][:cursor_col-1] + lines[cursor_line][cursor_col:]
                    cursor_col -= 1
                    redraw_editor()
                elif cursor_line > 0:
                    # Merge with previous line
                    prev_line = lines[cursor_line - 1]
                    current_line = lines[cursor_line]
                    lines[cursor_line - 1] = prev_line + current_line
                    del lines[cursor_line]
                    cursor_line -= 1
                    cursor_col = len(prev_line)
                    redraw_editor()
            elif key == curses.KEY_DC:
                if cursor_col < len(lines[cursor_line]):
                    # Delete character at cursor
                    lines[cursor_line] = lines[cursor_line][:cursor_col] + lines[cursor_line][cursor_col+1:]
                    redraw_editor()
                elif cursor_line < len(lines) - 1:
                    # Merge with next line
                    current_line = lines[cursor_line]
                    next_line = lines[cursor_line + 1]
                    lines[cursor_line] = current_line + next_line
                    del lines[cursor_line + 1]
                    redraw_editor()
            elif is_enter_key(key):
                # Insert new line
                current_line = lines[cursor_line]
                lines[cursor_line] = current_line[:cursor_col]
                lines.insert(cursor_line + 1, current_line[cursor_col:])
                cursor_line += 1
                cursor_col = 0
                redraw_editor()
            elif 32 <= key <= 126:
                # Insert character
                current_line = lines[cursor_line]
                lines[cursor_line] = current_line[:cursor_col] + chr(key) + current_line[cursor_col:]
                cursor_col += 1
                redraw_editor()
                
        except KeyboardInterrupt:
            break
    
    curses.noecho()
    curses.curs_set(0)

def select_daily_file(stdscr, action):
    """Select a daily journal file to read or edit"""
    stdscr.keypad(True)  # Enable keypad for special keys
    files = get_daily_files()
    if not files:
        stdscr.clear()
        stdscr.addstr(0, 0, "No daily journal files found.")
        settings = get_settings()
        stdscr.addstr(1, 0, f"Journal directory: {settings['journal_directory']}")
        stdscr.addstr(2, 0, "Try creating a new entry first to create a journal file.")
        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"{action} Daily Journal (ESC to cancel):")
        stdscr.addstr(1, 0, f"Found {len(files)} journal file(s)")
        for i, filename in enumerate(files):
            if i == idx:
                stdscr.addstr(i+3, 2, f"> {filename}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+3, 2, f"  {filename}")
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(files) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(files) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            filename = files[idx]
            content = read_daily_file(filename)
            if action == "Read":
                display_daily_content(stdscr, filename, content)
            elif action == "Edit":
                edit_daily_file(stdscr, filename, content)
            break
        elif key == 27:  # ESC
            break

def delete_daily_file(stdscr):
    """Delete a daily journal file"""
    files = get_daily_files()
    if not files:
        stdscr.addstr(0, 0, "No daily journal files found. Press any key to continue...")
        stdscr.getch()
        return
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Delete Daily Journal (ESC to cancel):")
        # Red warning message
        stdscr.addstr(1, 0, "⚠️  DANGER: This will delete the entire day's journal!", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 0, "⚠️  WARNING: This action cannot be undone!", curses.color_pair(1) | curses.A_BOLD)
        for i, filename in enumerate(files):
            if i == idx:
                stdscr.addstr(i+4, 2, f"> {filename}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+4, 2, f"  {filename}")
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(files) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(files) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            filename = files[idx]
            # Confirm deletion with red warning
            stdscr.clear()
            stdscr.addstr(0, 0, f"⚠️  FINAL WARNING: Delete {filename}?", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(2, 0, "⚠️  This will permanently delete the entire day's journal!", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(3, 0, "⚠️  This action cannot be undone!", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(5, 0, "Press 'y' to confirm deletion, any other key to cancel: ")
            stdscr.refresh()
            
            confirm = stdscr.getch()
            if confirm == ord('y') or confirm == ord('Y'):
                settings = get_settings()
                filepath = os.path.join(settings["journal_directory"], filename)
                try:
                    os.remove(filepath)
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"✅ Deleted: {filename}")
                    stdscr.addstr(2, 0, "Press any key to continue...")
                    stdscr.getch()
                except Exception as e:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"❌ Error deleting file: {e}", curses.color_pair(1))
                    stdscr.addstr(2, 0, "Press any key to continue...")
                    stdscr.getch()
            break
        elif key == 27:  # ESC
            break

def settings_menu(stdscr):
    """Settings menu"""
    settings = get_settings()
    current_row = 0
    menu = [
        "Journal Directory",
        "Default Editor",
        "Date Format",
        "Filename Format",
        "Auto Save",
        "",
        "Debug Journal Info",
        "Debug Parse Entries",
        "Create Test File",
        "",
        "Tutorial",
        "",
        "Back"
    ]
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Settings")
        stdscr.addstr(1, 0, "Configure Daily Journal")
        
        y_pos = 3
        for idx, item in enumerate(menu):
            if item == "":  # Empty line for spacing
                y_pos += 1
                continue
                
            if idx == current_row:
                stdscr.addstr(y_pos, 2, f"> {item}", curses.A_REVERSE)
            else:
                stdscr.addstr(y_pos, 2, f"  {item}")
            y_pos += 1
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if current_row > 0:
                current_row -= 1
                while current_row > 0 and menu[current_row] == "":
                    current_row -= 1
            else:
                # Wrap to bottom
                current_row = len(menu) - 1
                while current_row > 0 and menu[current_row] == "":
                    current_row -= 1
        elif key == curses.KEY_DOWN:
            if current_row < len(menu) - 1:
                current_row += 1
                while current_row < len(menu) - 1 and menu[current_row] == "":
                    current_row += 1
            else:
                # Wrap to top
                current_row = 0
                while current_row < len(menu) - 1 and menu[current_row] == "":
                    current_row += 1
        elif is_selection_key(key):  # Enter or Space
            if menu[current_row] == "Journal Directory":
                show_journal_directory(stdscr)
            elif menu[current_row] == "Default Editor":
                show_default_editor(stdscr)
            elif menu[current_row] == "Date Format":
                show_date_format(stdscr)
            elif menu[current_row] == "Filename Format":
                show_filename_format(stdscr)
            elif menu[current_row] == "Auto Save":
                show_auto_save(stdscr)
            elif menu[current_row] == "Debug Journal Info":
                debug_journal_info(stdscr)
            elif menu[current_row] == "Debug Parse Entries":
                debug_parse_entries(stdscr)
            elif menu[current_row] == "Create Test File":
                create_test_file(stdscr)
            elif menu[current_row] == "Tutorial":
                show_tutorial(stdscr)
            elif menu[current_row] == "Back":
                break
        elif key == 27:  # ESC
            break

def show_journal_directory(stdscr):
    """Show and edit journal directory setting"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Journal Directory")
    stdscr.addstr(2, 0, f"Current: {settings['journal_directory']}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    stdscr.getch()

def show_default_editor(stdscr):
    """Show and edit default editor setting"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Default Editor")
    stdscr.addstr(2, 0, f"Current: {settings['default_editor']}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    stdscr.getch()

def show_date_format(stdscr):
    """Show and edit date format setting"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Date Format")
    stdscr.addstr(2, 0, f"Current: {settings['date_format']}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    stdscr.getch()

def show_filename_format(stdscr):
    """Show and edit filename format setting"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Filename Format")
    stdscr.addstr(2, 0, f"Current: {settings['filename_format']}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    stdscr.getch()

def show_auto_save(stdscr):
    """Show and edit auto save setting"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Auto Save")
    stdscr.addstr(2, 0, f"Current: {settings['auto_save']}")
    stdscr.addstr(4, 0, "Press any key to continue...")
    stdscr.getch()

def show_tutorial(stdscr):
    """Show tutorial/help information"""
    height, width = stdscr.getmaxyx()
    
    tutorial_text = [
        "Daily Journal - Terminal Journal Tutorial",
        "",
        "Navigation:",
        "  ↑/↓ Arrow Keys - Navigate menus",
        "  Enter or Space - Select option",
        "  ESC - Go back/Exit",
        "",
        "Keyboard Shortcuts:",
        "  Ctrl+N - New Entry (Terminal)",
        "  Ctrl+O - Edit Today's Journal (Terminal)",
        "  Ctrl+F - Search Entries",
        "",
        "Daily Journal Concept:",
        "  • All entries from the same day are saved in one file",
        "  • Each entry has its own title and tags",
        "  • Perfect for multiple entries per day",
        "  • Easy to review an entire day's thoughts",
        "",
        "Writing Entries:",
        "  New Entry (Terminal) - Write directly in terminal",
        "  New Entry (Editor) - Use external editor",
        "  Ctrl+D - Finish writing entry",
        "  Ctrl+S - Save in editor mode",
        "  Ctrl+Q - Quit without saving",
        "",
        "Editing:",
        "  Arrow Keys - Move cursor",
        "  Ctrl+Left/Right - Move by words",
        "  Ctrl+A/E - Move to line start/end",
        "  Backspace/Delete - Delete characters",
        "",
        "File Management:",
        "  Read Daily File - View entire day's journal",
        "  Edit Today's Journal - Modify today's journal",
        "  Edit Journal by Date - Select specific date to edit",
        "  Delete Daily File - Remove entire day (with confirmation)",
        "  Search Entries - Find entries by title, content, or tags",
        "",
        "Settings:",
        "  Journal Directory - Change storage location",
        "  Default Editor - Set external editor",
        "  Date Format - Customize date display",
        "  Filename Format - Choose naming style",
        "",
        "Tips:",
        "  • Use Ctrl+D to finish writing entries",
        "  • Search works on titles, content, and tags",
        "  • Settings are saved automatically",
        "  • You can edit entire days in terminal or external editor",
        "  • Tags help organize your entries within each day",
        "  • Use keyboard shortcuts for quick access",
        "  • Ctrl+O quickly opens today's journal for editing",
        "",
        "Press Enter, Space, or ESC to exit..."
    ]
    
    # Calculate how many lines we can display
    display_height = height - 2  # Leave room for instructions
    start_line = 0
    
    while True:
        stdscr.clear()
        
        # Show instructions
        stdscr.addstr(0, 0, "↑/↓ to scroll, Enter/Space/ESC to exit")
        
        # Display visible lines
        y_pos = 2
        for i in range(display_height):
            line_idx = start_line + i
            if line_idx < len(tutorial_text):
                line = tutorial_text[line_idx]
                
                # Center the title
                if line == "Daily Journal - Terminal Journal Tutorial":
                    x_pos = max(0, (width - len(line)) // 2)
                    stdscr.addstr(y_pos, x_pos, line, curses.A_BOLD)
                else:
                    stdscr.addstr(y_pos, 0, line)
                y_pos += 1
        
        # Show scroll indicators
        if start_line > 0:
            stdscr.addstr(1, width - 3, "↑")
        if start_line + display_height < len(tutorial_text):
            stdscr.addstr(height - 1, width - 3, "↓")
        
        stdscr.refresh()
        
        # Handle input
        key = stdscr.getch()
        
        if key == curses.KEY_UP and start_line > 0:
            start_line -= 1
        elif key == curses.KEY_DOWN and start_line + display_height < len(tutorial_text):
            start_line += 1
        elif key == curses.KEY_PPAGE and start_line > 0:  # Page Up
            start_line = max(0, start_line - display_height + 2)
        elif key == curses.KEY_NPAGE and start_line + display_height < len(tutorial_text):  # Page Down
            start_line = min(len(tutorial_text) - display_height, start_line + display_height - 2)
        elif key == 27 or key == 10 or key == 32:  # ESC, Enter, or Space
            break

def search_entries(stdscr):
    """Search through daily journal entries"""
    files = get_daily_files()
    if not files:
        stdscr.addstr(0, 0, "No daily journal files found. Press any key to continue...")
        stdscr.getch()
        return
    
    # Get search term
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "Search Daily Journal Entries")
    stdscr.addstr(2, 0, "Enter search term: ")
    search_term = stdscr.getstr(2, 25).decode().lower()
    curses.noecho()
    
    if not search_term.strip():
        return
    
    # Search through daily files
    matching_entries = []
    for filename in files:
        content = read_daily_file(filename)
        if search_term in content.lower():
            matching_entries.append((filename, "content"))
    
    if not matching_entries:
        stdscr.clear()
        stdscr.addstr(0, 0, f"No daily journal files found matching '{search_term}'")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    # Display search results
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Search Results for '{search_term}' ({len(matching_entries)} found)")
        stdscr.addstr(1, 0, "Use arrow keys to navigate, Enter/Space to read, ESC to go back")
        
        for i, (filename, match_type) in enumerate(matching_entries):
            if i == idx:
                stdscr.addstr(i+3, 2, f"> {filename} ({match_type})", curses.A_REVERSE)
            else:
                stdscr.addstr(i+3, 2, f"  {filename} ({match_type})")
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(matching_entries) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(matching_entries) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            # Read the selected daily file
            selected_file = matching_entries[idx][0]
            content = read_daily_file(selected_file)
            display_daily_content(stdscr, selected_file, content)
        elif key == 27:  # ESC
            break

def select_date_to_edit(stdscr):
    """Select a specific date to edit in terminal"""
    files = get_daily_files()
    if not files:
        stdscr.addstr(0, 0, "No daily journal files found. Press any key to continue...")
        stdscr.getch()
        return
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select Date to Edit (Terminal) (ESC to cancel):")
        for i, filename in enumerate(files):
            if i == idx:
                stdscr.addstr(i+2, 2, f"> {filename}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+2, 2, f"  {filename}")
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(files) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(files) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            filename = files[idx]
            content = read_daily_file(filename)
            edit_daily_file(stdscr, filename, content)
            break
        elif key == 27:  # ESC
            break

def debug_journal_info(stdscr):
    """Debug function to show journal directory information"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Journal Debug Information")
    stdscr.addstr(2, 0, f"Journal Directory: {settings['journal_directory']}")
    
    # Check if directory exists
    if os.path.exists(settings["journal_directory"]):
        stdscr.addstr(3, 0, "✓ Journal directory exists")
        
        # List all files in directory
        try:
            all_files = os.listdir(settings["journal_directory"])
            stdscr.addstr(4, 0, f"All files in directory ({len(all_files)}):")
            for i, file in enumerate(all_files[:10]):  # Show first 10 files
                stdscr.addstr(5 + i, 2, f"  {file}")
            if len(all_files) > 10:
                stdscr.addstr(15, 2, f"  ... and {len(all_files) - 10} more files")
            
            # Show .md files specifically
            md_files = [f for f in all_files if f.endswith('.md')]
            stdscr.addstr(17, 0, f"Markdown files ({len(md_files)}):")
            for i, file in enumerate(md_files):
                stdscr.addstr(18 + i, 2, f"  {file}")
                
        except Exception as e:
            stdscr.addstr(4, 0, f"Error listing directory: {e}")
    else:
        stdscr.addstr(3, 0, "✗ Journal directory does not exist")
    
    stdscr.addstr(25, 0, "Press any key to continue...")
    stdscr.getch()

def create_test_file(stdscr):
    """Create a test journal file for debugging"""
    settings = get_settings()
    test_filename = "test-journal.md"
    test_content = """# Test Journal Entry

tags: test, debug

This is a test journal entry to verify that the reading functionality works correctly.

## Test Content

- Item 1: Testing basic functionality
- Item 2: Testing markdown formatting
- Item 3: Testing file reading

### Code Example

```python
print("Hello, Journal!")
```

This should be visible when reading the file.
"""
    
    filepath = os.path.join(settings["journal_directory"], test_filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Test file created successfully!")
        stdscr.addstr(1, 0, f"File: {filepath}")
        stdscr.addstr(3, 0, "You can now try 'Read Daily File' to test the reading functionality.")
        stdscr.addstr(5, 0, "Press any key to continue...")
        stdscr.getch()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error creating test file: {e}")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.getch()

def parse_entries_from_content(content, filename):
    """Parse individual entries from a daily file content"""
    entries = []
    if not content.strip():
        return entries
    
    # Split the content into lines
    lines = content.split('\n')
    
    current_entry = None
    current_content = []
    
    for line in lines:
        # Check if this line starts a new entry (starts with #)
        if line.strip().startswith('# '):
            # Save the previous entry if it exists
            if current_entry:
                current_entry['content'] = '\n'.join(current_content).strip()
                entries.append(current_entry)
            
            # Start a new entry
            title = line[2:].strip()  # Remove '# ' prefix
            current_entry = {
                'filename': filename,
                'title': title,
                'tags': '',
                'content': '',
                'entry_index': len(entries)
            }
            current_content = []
            
        elif line.strip().startswith('#'):
            # Handle single # case
            if current_entry:
                current_entry['content'] = '\n'.join(current_content).strip()
                entries.append(current_entry)
            
            title = line[1:].strip()  # Remove '#' prefix
            current_entry = {
                'filename': filename,
                'title': title,
                'tags': '',
                'content': '',
                'entry_index': len(entries)
            }
            current_content = []
            
        elif current_entry and line.strip().startswith('tags:'):
            # Extract tags
            current_entry['tags'] = line[5:].strip()  # Remove 'tags:' prefix
            
        elif current_entry:
            # This is content for the current entry
            current_content.append(line)
    
    # Don't forget the last entry
    if current_entry:
        current_entry['content'] = '\n'.join(current_content).strip()
        entries.append(current_entry)
    
    return entries

def get_all_entries():
    """Get all individual entries from all daily files"""
    all_entries = []
    files = get_daily_files()
    
    for filename in files:
        content = read_daily_file(filename)
        entries = parse_entries_from_content(content, filename)
        all_entries.extend(entries)
    
    # Sort by filename (date) and then by entry index within each file
    all_entries.sort(key=lambda x: (x['filename'], x['entry_index']), reverse=True)
    return all_entries

def get_entry_display_name(entry):
    """Get a display name for an entry in the menu"""
    date_part = entry['filename'].replace('.md', '')
    title_part = entry['title'][:50]  # Truncate long titles
    if len(entry['title']) > 50:
        title_part += "..."
    
    return f"{date_part} - {title_part}"

def select_entry(stdscr, action):
    """Select an individual entry to read or edit"""
    stdscr.keypad(True)  # Enable keypad for special keys
    entries = get_all_entries()
    if not entries:
        stdscr.clear()
        stdscr.addstr(0, 0, "No journal entries found.")
        settings = get_settings()
        stdscr.addstr(1, 0, f"Journal directory: {settings['journal_directory']}")
        stdscr.addstr(2, 0, "Try creating a new entry first to create a journal entry.")
        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"{action} Journal Entry (ESC to cancel):")
        stdscr.addstr(1, 0, f"Found {len(entries)} journal entry(ies)")
        for i, entry in enumerate(entries):
            display_name = get_entry_display_name(entry)
            if i == idx:
                stdscr.addstr(i+3, 2, f"> {display_name}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+3, 2, f"  {display_name}")
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(entries) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(entries) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            selected_entry = entries[idx]
            if action == "Read":
                display_entry_content(stdscr, selected_entry)
            elif action == "Edit":
                edit_entry(stdscr, selected_entry)
            break
        elif key == 27:  # ESC
            break

def display_entry_content(stdscr, entry):
    """Display a single entry's content"""
    height, width = stdscr.getmaxyx()
    
    # Enable keypad on main screen
    stdscr.keypad(True)
    
    # Create the full entry content for display
    full_content = f"# {entry['title']}\n"
    if entry['tags']:
        full_content += f"\ntags: {entry['tags']}\n"
    full_content += f"\n{entry['content']}"
    
    # Split content into lines
    lines = full_content.split('\n')
    
    # Debug: Show content info
    if not full_content.strip():
        stdscr.clear()
        stdscr.addstr(0, 0, f"Entry: {entry['title']}")
        stdscr.addstr(1, 0, "This entry appears to be empty.")
        stdscr.addstr(3, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    # Create a scrollable window
    content_height = height - 4
    content_width = width - 4
    content_win = curses.newwin(content_height, content_width, 2, 2)
    content_win.box()
    content_win.addstr(0, 2, f" {entry['title']} ")
    
    # Enable keypad for special keys
    content_win.keypad(True)
    
    # Display instructions
    content_win.addstr(1, 1, "Use arrow keys to scroll, ESC to return")
    
    # Display content starting from line 2
    start_line = 0
    while True:
        content_win.clear()
        content_win.box()
        content_win.addstr(0, 2, f" {entry['title']} ")
        content_win.addstr(1, 1, "Use arrow keys to scroll, ESC to return")
        
        # Display visible lines
        for i in range(content_height - 2):
            if start_line + i < len(lines):
                line = lines[start_line + i]
                # Truncate line if too long
                if len(line) > content_width - 2:
                    line = line[:content_width - 5] + "..."
                content_win.addstr(i + 2, 1, line)
        
        # Show scroll indicator
        if start_line > 0:
            content_win.addstr(1, content_width - 3, "↑")
        if start_line + content_height - 2 < len(lines):
            content_win.addstr(content_height - 1, content_width - 3, "↓")
        
        # Refresh the content window
        content_win.refresh()
        
        # Handle input from content window (not main screen)
        key = content_win.getch()
        
        if key == curses.KEY_UP:
            if start_line > 0:
                start_line -= 1
        elif key == curses.KEY_DOWN:
            if start_line + content_height - 2 < len(lines):
                start_line += 1
        elif key == curses.KEY_PPAGE:
            if start_line > 0:
                start_line = max(0, start_line - content_height + 2)
        elif key == curses.KEY_NPAGE:
            if start_line + content_height - 2 < len(lines):
                start_line = min(len(lines) - content_height + 2, start_line + content_height - 2)
        elif key == 27:  # ESC
            break

def edit_entry(stdscr, entry):
    """Edit a single entry"""
    height, width = stdscr.getmaxyx()
    
    # Create the full entry content for editing
    full_content = f"# {entry['title']}\n"
    if entry['tags']:
        full_content += f"\ntags: {entry['tags']}\n"
    full_content += f"\n{entry['content']}"
    
    # Split content into lines and handle empty content
    if not full_content.strip():
        lines = [""]
    else:
        lines = full_content.split('\n')
    
    # Create an editable window
    edit_height = height - 4
    edit_width = width - 4
    edit_win = curses.newwin(edit_height, edit_width, 2, 2)
    edit_win.box()
    edit_win.addstr(0, 2, f" Editing: {entry['title']} ")
    edit_win.addstr(1, 1, "Ctrl+S to save, Ctrl+Q to quit without saving")
    
    # Enable keypad for special keys
    edit_win.keypad(True)
    curses.echo()
    curses.curs_set(1)
    
    # Current cursor position in the text
    cursor_line = 0
    cursor_col = 0
    
    # Display offset (for scrolling)
    display_start = 0
    
    def is_word_char(char):
        """Check if character is part of a word"""
        return char.isalnum() or char == '_'
    
    def find_word_start(line, col):
        """Find the start of the word at or before the given column"""
        if col == 0:
            return 0
        if col >= len(line):
            col = len(line) - 1
        
        # If we're in the middle of a word, find its start
        if is_word_char(line[col]):
            while col > 0 and is_word_char(line[col - 1]):
                col -= 1
            return col
        else:
            # Find the previous word
            while col > 0 and not is_word_char(line[col - 1]):
                col -= 1
            while col > 0 and is_word_char(line[col - 1]):
                col -= 1
            return col
    
    def find_word_end(line, col):
        """Find the end of the word at or after the given column"""
        if col >= len(line):
            return len(line)
        
        # If we're in the middle of a word, find its end
        if is_word_char(line[col]):
            while col < len(line) and is_word_char(line[col]):
                col += 1
            return col
        else:
            # Find the next word
            while col < len(line) and not is_word_char(line[col]):
                col += 1
            return col
    
    def redraw_editor():
        """Redraw the entire editor content"""
        edit_win.clear()
        edit_win.box()
        edit_win.addstr(0, 2, f" Editing: {entry['title']} ")
        edit_win.addstr(1, 1, "Ctrl+S to save, Ctrl+Q to quit without saving")
        
        # Display visible lines
        for i in range(edit_height - 2):
            line_idx = display_start + i
            if line_idx < len(lines):
                line = lines[line_idx]
                # Truncate line if too long
                if len(line) > edit_width - 2:
                    line = line[:edit_width - 5] + "..."
                edit_win.addstr(i + 2, 1, line)
        
        # Position cursor
        cursor_display_line = cursor_line - display_start + 2
        if 2 <= cursor_display_line < edit_height:
            edit_win.move(cursor_display_line, min(cursor_col + 1, edit_width - 2))
        
        edit_win.refresh()
    
    redraw_editor()
    
    while True:
        try:
            key = edit_win.getch()
            
            if key == 19:  # Ctrl+S
                # Save the file
                write_daily_file(entry['filename'], '\n'.join(lines))
                break
            elif key == 17:  # Ctrl+Q
                # Quit without saving
                break
            elif key == curses.KEY_UP:
                if cursor_line > 0:
                    cursor_line -= 1
                    cursor_col = min(cursor_col, len(lines[cursor_line]))
                    # Adjust display if needed
                    if cursor_line < display_start:
                        display_start = cursor_line
                    redraw_editor()
            elif key == curses.KEY_DOWN:
                if cursor_line < len(lines) - 1:
                    cursor_line += 1
                    cursor_col = min(cursor_col, len(lines[cursor_line]))
                    # Adjust display if needed
                    if cursor_line >= display_start + edit_height - 2:
                        display_start = cursor_line - edit_height + 3
                    redraw_editor()
            elif key == curses.KEY_LEFT:
                if cursor_col > 0:
                    cursor_col -= 1
                    redraw_editor()
            elif key == curses.KEY_RIGHT:
                if cursor_col < len(lines[cursor_line]):
                    cursor_col += 1
                    redraw_editor()
            elif key == 23:  # Ctrl+W (word navigation)
                # Move to previous word
                if cursor_col > 0:
                    cursor_col = find_word_start(lines[cursor_line], cursor_col)
                    redraw_editor()
            elif key == 24:  # Ctrl+X (word navigation)
                # Move to next word
                if cursor_col < len(lines[cursor_line]):
                    cursor_col = find_word_end(lines[cursor_line], cursor_col)
                    redraw_editor()
            elif key == 1:  # Ctrl+A (line navigation)
                # Move to start of line
                cursor_col = 0
                redraw_editor()
            elif key == 5:  # Ctrl+E (line navigation)
                # Move to end of line
                cursor_col = len(lines[cursor_line])
                redraw_editor()
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if cursor_col > 0:
                    # Delete character before cursor
                    lines[cursor_line] = lines[cursor_line][:cursor_col-1] + lines[cursor_line][cursor_col:]
                    cursor_col -= 1
                    redraw_editor()
                elif cursor_line > 0:
                    # Merge with previous line
                    prev_line = lines[cursor_line - 1]
                    current_line = lines[cursor_line]
                    lines[cursor_line - 1] = prev_line + current_line
                    del lines[cursor_line]
                    cursor_line -= 1
                    cursor_col = len(prev_line)
                    redraw_editor()
            elif key == curses.KEY_DC:
                if cursor_col < len(lines[cursor_line]):
                    # Delete character at cursor
                    lines[cursor_line] = lines[cursor_line][:cursor_col] + lines[cursor_line][cursor_col+1:]
                    redraw_editor()
                elif cursor_line < len(lines) - 1:
                    # Merge with next line
                    current_line = lines[cursor_line]
                    next_line = lines[cursor_line + 1]
                    lines[cursor_line] = current_line + next_line
                    del lines[cursor_line + 1]
                    redraw_editor()
            elif is_enter_key(key):
                # Insert new line
                current_line = lines[cursor_line]
                lines[cursor_line] = current_line[:cursor_col]
                lines.insert(cursor_line + 1, current_line[cursor_col:])
                cursor_line += 1
                cursor_col = 0
                redraw_editor()
            elif 32 <= key <= 126:
                # Insert character
                current_line = lines[cursor_line]
                lines[cursor_line] = current_line[:cursor_col] + chr(key) + current_line[cursor_col:]
                cursor_col += 1
                redraw_editor()
                
        except KeyboardInterrupt:
            break
    
    curses.noecho()
    curses.curs_set(0)

def debug_parse_entries(stdscr):
    """Debug function to show what entries are being parsed"""
    settings = get_settings()
    stdscr.clear()
    stdscr.addstr(0, 0, "Debug: Entry Parsing")
    
    files = get_daily_files()
    if not files:
        stdscr.addstr(2, 0, "No files found")
        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    height, width = stdscr.getmaxyx()
    y_pos = 2
    
    for filename in files[:3]:  # Show first 3 files
        if y_pos >= height - 5:
            break
            
        stdscr.addstr(y_pos, 0, f"File: {filename}")
        y_pos += 1
        
        content = read_daily_file(filename)
        stdscr.addstr(y_pos, 0, f"Content length: {len(content)}")
        y_pos += 1
        
        # Show first 200 characters of content, truncated to fit screen
        preview = content[:200].replace('\n', '\\n')
        preview = preview[:width-20]  # Leave some margin
        stdscr.addstr(y_pos, 0, f"Preview: {preview}")
        y_pos += 2
        
        # Parse entries
        entries = parse_entries_from_content(content, filename)
        stdscr.addstr(y_pos, 0, f"Parsed {len(entries)} entries:")
        y_pos += 1
        
        for i, entry in enumerate(entries):
            if y_pos >= height - 5:
                break
                
            # Truncate title to fit screen
            title = entry['title'][:width-15]
            stdscr.addstr(y_pos, 2, f"Entry {i+1}: {title}")
            y_pos += 1
            
            tags = entry['tags'][:width-15] if entry['tags'] else ''
            stdscr.addstr(y_pos, 4, f"Tags: '{tags}'")
            y_pos += 1
            
            stdscr.addstr(y_pos, 4, f"Content length: {len(entry['content'])}")
            y_pos += 1
            
            if entry['content']:
                content_preview = entry['content'][:50].replace('\n', '\\n')
                content_preview = content_preview[:width-20]  # Leave margin
                stdscr.addstr(y_pos, 4, f"Content preview: {content_preview}")
                y_pos += 1
            y_pos += 1
        
        y_pos += 1
    
    stdscr.addstr(height-2, 0, "Press any key to continue...")
    stdscr.getch()

def search_individual_entries(stdscr):
    """Search through individual journal entries"""
    entries = get_all_entries()
    if not entries:
        stdscr.addstr(0, 0, "No journal entries found. Press any key to continue...")
        stdscr.getch()
        return
    
    # Get search term
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "Search Individual Journal Entries")
    stdscr.addstr(2, 0, "Enter search term: ")
    search_term = stdscr.getstr(2, 30).decode().lower()
    curses.noecho()
    
    if not search_term.strip():
        return
    
    # Search through individual entries
    matching_entries = []
    for entry in entries:
        # Search in title, tags, and content
        searchable_text = f"{entry['title']} {entry['tags']} {entry['content']}".lower()
        if search_term in searchable_text:
            # Determine where the match was found
            match_location = []
            if search_term in entry['title'].lower():
                match_location.append("title")
            if entry['tags'] and search_term in entry['tags'].lower():
                match_location.append("tags")
            if search_term in entry['content'].lower():
                match_location.append("content")
            
            matching_entries.append((entry, ", ".join(match_location)))
    
    if not matching_entries:
        stdscr.clear()
        stdscr.addstr(0, 0, f"No journal entries found matching '{search_term}'")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    # Display search results
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Search Results for '{search_term}' ({len(matching_entries)} found)")
        stdscr.addstr(1, 0, "Use arrow keys to navigate, Enter/Space to read, ESC to go back")
        
        for i, (entry, match_location) in enumerate(matching_entries):
            display_name = get_entry_display_name(entry)
            if i == idx:
                stdscr.addstr(i+3, 2, f"> {display_name}", curses.A_REVERSE)
                stdscr.addstr(i+3, len(display_name)+4, f" (matched in: {match_location})")
            else:
                stdscr.addstr(i+3, 2, f"  {display_name}")
                stdscr.addstr(i+3, len(display_name)+4, f" (matched in: {match_location})")
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(matching_entries) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(matching_entries) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            # Read the selected entry
            selected_entry = matching_entries[idx][0]
            display_entry_content(stdscr, selected_entry)
        elif key == 27:  # ESC
            break

def search_entries_to_edit(stdscr):
    """Search through individual journal entries and edit them"""
    entries = get_all_entries()
    if not entries:
        stdscr.addstr(0, 0, "No journal entries found. Press any key to continue...")
        stdscr.getch()
        return
    
    # Get search term
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, "Search and Edit Journal Entries")
    stdscr.addstr(2, 0, "Enter search term: ")
    search_term = stdscr.getstr(2, 30).decode().lower()
    curses.noecho()
    
    if not search_term.strip():
        return
    
    # Search through individual entries
    matching_entries = []
    for entry in entries:
        # Search in title, tags, and content
        searchable_text = f"{entry['title']} {entry['tags']} {entry['content']}".lower()
        if search_term in searchable_text:
            # Determine where the match was found
            match_location = []
            if search_term in entry['title'].lower():
                match_location.append("title")
            if entry['tags'] and search_term in entry['tags'].lower():
                match_location.append("tags")
            if search_term in entry['content'].lower():
                match_location.append("content")
            
            matching_entries.append((entry, ", ".join(match_location)))
    
    if not matching_entries:
        stdscr.clear()
        stdscr.addstr(0, 0, f"No journal entries found matching '{search_term}'")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    # Display search results
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Search Results for '{search_term}' ({len(matching_entries)} found)")
        stdscr.addstr(1, 0, "Use arrow keys to navigate, Enter/Space to edit, ESC to go back")
        
        for i, (entry, match_location) in enumerate(matching_entries):
            display_name = get_entry_display_name(entry)
            if i == idx:
                stdscr.addstr(i+3, 2, f"> {display_name}", curses.A_REVERSE)
                stdscr.addstr(i+3, len(display_name)+4, f" (matched in: {match_location})")
            else:
                stdscr.addstr(i+3, 2, f"  {display_name}")
                stdscr.addstr(i+3, len(display_name)+4, f" (matched in: {match_location})")
        
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(matching_entries) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(matching_entries) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            # Edit the selected entry
            selected_entry = matching_entries[idx][0]
            edit_entry(stdscr, selected_entry)
        elif key == 27:  # ESC
            break

def main_menu(stdscr):
    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)  # Red text on default background
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # Red text on black background
    
    curses.curs_set(0)
    stdscr.keypad(True)  # Enable keypad for special keys
    current_row = 0
    menu = [
        "New Entry (Terminal) [Ctrl+N]",
        "New Entry (Editor)", 
        "",
        "Read Daily File",
        "Read Specific Journal Entry",
        "",
        "Edit Today's Journal (Terminal) [Ctrl+O]",
        "Edit Journal by Date (Terminal)",
        "Edit Journal Entry",
        "Edit Daily File (Editor)",
        "",
        "Delete Entry",
        "Delete Daily File",
        "",
        "Search Entries [Ctrl+F]",
        "Search Entries to Edit",
        "Search Daily Files",
        "",
        "Settings",
        "",
        "Exit"
    ]
    
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Daily Journal")
        stdscr.addstr(1, 0, "Terminal Journal Application")
        
        y_pos = 3
        for idx, item in enumerate(menu):
            if item == "":  # Empty line for spacing
                y_pos += 1
                continue
                
            if idx == current_row:
                stdscr.addstr(y_pos, 2, f"> {item}", curses.A_REVERSE)
            else:
                stdscr.addstr(y_pos, 2, f"  {item}")
            y_pos += 1
            
        key = stdscr.getch()
        
        # Handle keyboard shortcuts
        if key == 14:  # Ctrl+N
            new_entry(stdscr, use_editor=False)
            continue
        elif key == 15:  # Ctrl+O
            # Edit today's file in curses
            today_file = get_today_filename()
            content = read_daily_file(today_file)
            edit_daily_file(stdscr, today_file, content)
            continue
        elif key == 6:  # Ctrl+F
            search_individual_entries(stdscr)
            continue
        
        # Handle regular navigation
        if key == curses.KEY_UP:
            if current_row > 0:
                current_row -= 1
                # Skip empty menu items when moving up
                while current_row > 0 and menu[current_row] == "":
                    current_row -= 1
            else:
                # Wrap to bottom
                current_row = len(menu) - 1
                while current_row > 0 and menu[current_row] == "":
                    current_row -= 1
        elif key == curses.KEY_DOWN:
            if current_row < len(menu) - 1:
                current_row += 1
                # Skip empty menu items when moving down
                while current_row < len(menu) - 1 and menu[current_row] == "":
                    current_row += 1
            else:
                # Wrap to top
                current_row = 0
                while current_row < len(menu) - 1 and menu[current_row] == "":
                    current_row += 1
        elif is_selection_key(key):  # Enter or Space
            if menu[current_row] == "New Entry (Terminal) [Ctrl+N]":
                new_entry(stdscr, use_editor=False)
            elif menu[current_row] == "New Entry (Editor)":
                new_entry(stdscr, use_editor=True)
            elif menu[current_row] == "Read Daily File":
                select_daily_file(stdscr, "Read")
            elif menu[current_row] == "Read Specific Journal Entry":
                select_entry(stdscr, "Read")
            elif menu[current_row] == "Edit Today's Journal (Terminal) [Ctrl+O]":
                # Edit today's file in curses
                today_file = get_today_filename()
                content = read_daily_file(today_file)
                edit_daily_file(stdscr, today_file, content)
            elif menu[current_row] == "Edit Journal by Date (Terminal)":
                select_date_to_edit(stdscr)
            elif menu[current_row] == "Edit Journal Entry":
                select_entry(stdscr, "Edit")
            elif menu[current_row] == "Edit Daily File (Editor)":
                select_daily_file(stdscr, "Edit")
            elif menu[current_row] == "Delete Entry":
                select_entry_to_delete(stdscr)
            elif menu[current_row] == "Delete Daily File":
                delete_daily_file(stdscr)
            elif menu[current_row] == "Search Entries [Ctrl+F]":
                search_individual_entries(stdscr)
            elif menu[current_row] == "Search Entries to Edit":
                search_entries_to_edit(stdscr)
            elif menu[current_row] == "Search Daily Files":
                search_entries(stdscr)
            elif menu[current_row] == "Settings":
                settings_menu(stdscr)
            elif menu[current_row] == "Exit":
                break
        elif key == 27:  # ESC
            break

def main():
    curses.wrapper(main_menu)

def delete_entry(stdscr, entry):
    """Delete a single entry from its daily file"""
    height, width = stdscr.getmaxyx()
    
    # Confirm deletion with red warning
    stdscr.clear()
    stdscr.addstr(0, 0, f"⚠️  WARNING: Delete Entry?", curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(1, 0, f"Title: {entry['title']}")
    stdscr.addstr(2, 0, f"File: {entry['filename']}")
    stdscr.addstr(4, 0, "⚠️  This will remove this entry from the daily file!", curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(5, 0, "⚠️  This action cannot be undone!", curses.color_pair(1) | curses.A_BOLD)
    stdscr.addstr(7, 0, "Press 'y' to confirm deletion, any other key to cancel: ")
    stdscr.refresh()
    
    confirm = stdscr.getch()
    if confirm == ord('y') or confirm == ord('Y'):
        # Read the current file content
        content = read_daily_file(entry['filename'])
        lines = content.split('\n')
        
        # Parse all entries to find the exact boundaries
        all_entries = parse_entries_from_content(content, entry['filename'])
        
        # Find the target entry
        target_entry = None
        for e in all_entries:
            if e['title'] == entry['title'] and e['entry_index'] == entry['entry_index']:
                target_entry = e
                break
        
        if not target_entry:
            stdscr.clear()
            stdscr.addstr(0, 0, f"❌ Error: Could not find entry in file", curses.color_pair(1))
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.getch()
            return
        
        # Reconstruct the file content without the target entry
        new_lines = []
        current_line = 0
        
        for e in all_entries:
            if e['title'] == target_entry['title'] and e['entry_index'] == target_entry['entry_index']:
                # Skip this entry - don't add it to new_lines
                continue
            
            # Add this entry to new_lines
            # First, add the title line
            if e['title']:
                new_lines.append(f"# {e['title']}")
            
            # Add tags if they exist
            if e['tags']:
                new_lines.append(f"tags: {e['tags']}")
                new_lines.append("")  # Empty line after tags
            
            # Add content
            if e['content']:
                new_lines.append(e['content'])
            
            # Add spacing between entries
            new_lines.append("")
            new_lines.append("")
        
        # Remove trailing empty lines
        while new_lines and not new_lines[-1].strip():
            new_lines.pop()
        
        # Write the updated content back to the file
        new_content = '\n'.join(new_lines)
        write_daily_file(entry['filename'], new_content)
        
        stdscr.clear()
        stdscr.addstr(0, 0, f"✅ Deleted entry: {entry['title']}")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.getch()

def select_entry_to_delete(stdscr):
    """Select an individual entry to delete"""
    stdscr.keypad(True)  # Enable keypad for special keys
    entries = get_all_entries()
    if not entries:
        stdscr.clear()
        stdscr.addstr(0, 0, "No journal entries found.")
        settings = get_settings()
        stdscr.addstr(1, 0, f"Journal directory: {settings['journal_directory']}")
        stdscr.addstr(2, 0, "Try creating a new entry first to create a journal entry.")
        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.getch()
        return
    
    idx = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Delete Journal Entry (ESC to cancel):")
        # Red warning message
        stdscr.addstr(1, 0, "⚠️  DANGER: This will delete the selected entry!", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(2, 0, "⚠️  WARNING: This action cannot be undone!", curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(3, 0, f"Found {len(entries)} journal entry(ies)")
        for i, entry in enumerate(entries):
            display_name = get_entry_display_name(entry)
            if i == idx:
                stdscr.addstr(i+5, 2, f"> {display_name}", curses.A_REVERSE)
            else:
                stdscr.addstr(i+5, 2, f"  {display_name}")
        key = stdscr.getch()
        if key == curses.KEY_UP:
            if idx > 0:
                idx -= 1
            else:
                # Wrap to bottom
                idx = len(entries) - 1
        elif key == curses.KEY_DOWN:
            if idx < len(entries) - 1:
                idx += 1
            else:
                # Wrap to top
                idx = 0
        elif is_selection_key(key):  # Enter or Space
            selected_entry = entries[idx]
            delete_entry(stdscr, selected_entry)
            break
        elif key == 27:  # ESC
            break

if __name__ == "__main__":
    main()


"""
User interface layer for the Daily Journal application.
Handles all curses-based UI components and user interactions.
"""

import curses
import subprocess
import tempfile
from typing import List, Optional, Callable, Any, Dict, Tuple
from dataclasses import dataclass

from constants import MenuOptions, Shortcuts, Messages, Errors
from journal_data import Journal, Settings, JournalEntry


@dataclass
class MenuItem:
    """Represents a menu item"""
    text: str
    action: Callable
    shortcut: Optional[str] = None
    enabled: bool = True


class Menu:
    """Generic menu component"""
    
    def __init__(self, stdscr, title: str, items: List[MenuItem]):
        self.stdscr = stdscr
        self.title = title
        self.items = items
        self.selected_index = 0
        self.height, self.width = stdscr.getmaxyx()
    
    def display(self) -> Optional[MenuItem]:
        """Display menu and handle user interaction"""
        while True:
            self._draw()
            key = self.stdscr.getch()
            
            if key == curses.KEY_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif key == curses.KEY_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif key == ord('\n') or key == ord(' '):
                selected_item = self.items[self.selected_index]
                if selected_item.enabled:
                    return selected_item
            elif key == 27:  # ESC
                return None
            elif key == ord('q'):
                return None
    
    def _draw(self) -> None:
        """Draw the menu"""
        self.stdscr.clear()
        
        # Draw title
        title_y = max(1, self.height // 4)
        title_x = (self.width - len(self.title)) // 2
        self.stdscr.addstr(title_y, title_x, self.title, curses.A_BOLD)
        
        # Draw menu items
        start_y = title_y + 2
        for i, item in enumerate(self.items):
            y = start_y + i
            if y >= self.height - 2:
                break
            
            # Format item text
            text = item.text
            if item.shortcut:
                text += f" [{item.shortcut}]"
            
            # Determine attributes
            attr = curses.A_NORMAL
            if i == self.selected_index:
                attr = curses.A_REVERSE
            if not item.enabled:
                attr |= curses.A_DIM
            
            # Draw item
            x = (self.width - len(text)) // 2
            self.stdscr.addstr(y, x, text, attr)
        
        # Draw footer
        footer = "Use arrow keys to navigate, Enter to select, ESC to cancel"
        footer_y = self.height - 2
        footer_x = (self.width - len(footer)) // 2
        self.stdscr.addstr(footer_y, footer_x, footer, curses.A_DIM)
        
        self.stdscr.refresh()


class Dialog:
    """Generic dialog component"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
    
    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """Show a message dialog"""
        self.stdscr.clear()
        
        # Determine color based on message type
        color = curses.A_NORMAL
        if message_type == "error":
            color = curses.A_BOLD
        elif message_type == "success":
            color = curses.A_NORMAL
        
        # Draw title
        title_y = self.height // 3
        title_x = (self.width - len(title)) // 2
        self.stdscr.addstr(title_y, title_x, title, color | curses.A_BOLD)
        
        # Draw message (wrap if needed)
        message_lines = self._wrap_text(message, self.width - 4)
        message_y = title_y + 2
        
        for i, line in enumerate(message_lines):
            if message_y + i >= self.height - 3:
                break
            line_x = (self.width - len(line)) // 2
            self.stdscr.addstr(message_y + i, line_x, line, color)
        
        # Draw footer
        footer = "Press any key to continue..."
        footer_y = self.height - 2
        footer_x = (self.width - len(footer)) // 2
        self.stdscr.addstr(footer_y, footer_x, footer, curses.A_DIM)
        
        self.stdscr.refresh()
        self.stdscr.getch()
    
    def confirm(self, title: str, message: str) -> bool:
        """Show a confirmation dialog"""
        self.stdscr.clear()
        
        # Draw title
        title_y = self.height // 3
        title_x = (self.width - len(title)) // 2
        self.stdscr.addstr(title_y, title_x, title, curses.A_BOLD)
        
        # Draw message
        message_y = title_y + 2
        message_x = (self.width - len(message)) // 2
        self.stdscr.addstr(message_y, message_x, message)
        
        # Draw options
        options_y = message_y + 2
        yes_text = "Yes (Y)"
        no_text = "No (N)"
        
        yes_x = (self.width - len(yes_text) - len(no_text) - 4) // 2
        no_x = yes_x + len(yes_text) + 4
        
        self.stdscr.addstr(options_y, yes_x, yes_text)
        self.stdscr.addstr(options_y, no_x, no_text)
        
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key in [ord('y'), ord('Y')]:
                return True
            elif key in [ord('n'), ord('N'), 27]:  # ESC
                return False
    
    def input_text(self, prompt: str, default: str = "") -> Optional[str]:
        """Get text input from user"""
        self.stdscr.clear()
        
        # Draw prompt
        prompt_y = self.height // 3
        self.stdscr.addstr(prompt_y, 0, prompt)
        
        # Get input
        curses.echo()
        curses.curs_set(1)
        
        try:
            user_input = self.stdscr.getstr(prompt_y, len(prompt) + 1, 50)
            if user_input:
                return user_input.decode('utf-8')
            elif default:
                return default
            else:
                return ""
        except KeyboardInterrupt:
            return None
        finally:
            curses.noecho()
            curses.curs_set(0)
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (word + " ")
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines


class Editor:
    """Text editor component"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
    
    def edit_text(self, title: str, initial_content: str = "") -> Optional[str]:
        """Edit text content"""
        curses.noecho()
        curses.curs_set(1)
        
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, f"Editing: {title}")
        self.stdscr.addstr(1, 0, "Press Ctrl+D when finished, Ctrl+H for help")
        
        # Initialize content
        content_lines = initial_content.split('\n') if initial_content else [""]
        current_line_idx = len(content_lines) - 1
        current_line = content_lines[current_line_idx] if content_lines else ""
        cursor_col = len(current_line)
        y_start = 3
        
        def redraw_content():
            """Redraw the content area"""
            try:
                # Clear content area
                for i in range(y_start, self.height - 2):
                    if i < self.height - 1:
                        self.stdscr.move(i, 0)
                        self.stdscr.clrtoeol()
                
                # Draw all content lines
                for i, line in enumerate(content_lines):
                    if y_start + i < self.height - 2:
                        safe_text = line[:self.width-1]
                        self.stdscr.addstr(y_start + i, 0, safe_text)
                
                # Position cursor
                cursor_y = y_start + current_line_idx
                if cursor_y >= self.height - 1:
                    cursor_y = self.height - 2
                if cursor_y < y_start:
                    cursor_y = y_start
                
                safe_cursor_col = min(cursor_col, self.width-1)
                if safe_cursor_col < 0:
                    safe_cursor_col = 0
                
                self.stdscr.move(cursor_y, safe_cursor_col)
                
                # Update status bar
                word_count = len(' '.join(content_lines).split())
                status = f"Words: {word_count} | Line {current_line_idx + 1}/{len(content_lines)} | Ctrl+D to finish"
                self.stdscr.addstr(self.height - 1, 0, status[:self.width-1], curses.A_DIM)
                self.stdscr.refresh()
            except curses.error:
                pass
        
        redraw_content()
        
        while True:
            try:
                char = self.stdscr.getch()
                
                if char == 4:  # Ctrl+D
                    break
                elif char == 8:  # Ctrl+H - Help
                    self._show_help()
                    self.stdscr.clear()
                    self.stdscr.addstr(0, 0, f"Editing: {title}")
                    self.stdscr.addstr(1, 0, "Press Ctrl+D when finished, Ctrl+H for help")
                    redraw_content()
                elif char == 10:  # Enter
                    # Split current line
                    if current_line_idx < len(content_lines):
                        line = content_lines[current_line_idx]
                        content_lines[current_line_idx] = line[:cursor_col]
                        content_lines.insert(current_line_idx + 1, line[cursor_col:])
                    else:
                        content_lines.append("")
                    
                    current_line_idx += 1
                    cursor_col = 0
                    redraw_content()
                elif char == 127 or char == 8:  # Backspace
                    if cursor_col > 0:
                        line = content_lines[current_line_idx]
                        content_lines[current_line_idx] = line[:cursor_col-1] + line[cursor_col:]
                        cursor_col -= 1
                        redraw_content()
                    elif current_line_idx > 0:
                        # Merge with previous line
                        prev_line = content_lines[current_line_idx - 1]
                        current_line = content_lines[current_line_idx]
                        content_lines[current_line_idx - 1] = prev_line + current_line
                        del content_lines[current_line_idx]
                        current_line_idx -= 1
                        cursor_col = len(prev_line)
                        redraw_content()
                elif char == curses.KEY_DC:  # Delete
                    line = content_lines[current_line_idx]
                    if cursor_col < len(line):
                        content_lines[current_line_idx] = line[:cursor_col] + line[cursor_col+1:]
                        redraw_content()
                    elif current_line_idx < len(content_lines) - 1:
                        # At end of line, merge with next line
                        content_lines[current_line_idx] = line + content_lines[current_line_idx + 1]
                        del content_lines[current_line_idx + 1]
                        redraw_content()
                elif char == curses.KEY_UP:
                    if current_line_idx > 0:
                        current_line_idx -= 1
                        cursor_col = min(cursor_col, len(content_lines[current_line_idx]))
                        redraw_content()
                elif char == curses.KEY_DOWN:
                    if current_line_idx < len(content_lines) - 1:
                        current_line_idx += 1
                        cursor_col = min(cursor_col, len(content_lines[current_line_idx]))
                        redraw_content()
                elif char == curses.KEY_LEFT:
                    if cursor_col > 0:
                        cursor_col -= 1
                        redraw_content()
                elif char == curses.KEY_RIGHT:
                    if cursor_col < len(content_lines[current_line_idx]):
                        cursor_col += 1
                        redraw_content()
                else:
                    if 32 <= char <= 126:
                        line = content_lines[current_line_idx]
                        content_lines[current_line_idx] = line[:cursor_col] + chr(char) + line[cursor_col:]
                        cursor_col += 1
                        redraw_content()
                        
            except KeyboardInterrupt:
                break
        
        curses.curs_set(0)
        return "\n".join(content_lines)
    
    def _show_help(self) -> None:
        """Show editor help"""
        help_text = [
            "Editor Help:",
            "",
            "Navigation:",
            "  Arrow keys - Move cursor",
            "  Enter - New line",
            "  Backspace - Delete character",
            "  Delete - Delete character forward",
            "",
            "Commands:",
            "  Ctrl+D - Finish editing",
            "  Ctrl+H - Show this help",
            "",
            "Press any key to continue..."
        ]
        
        self.stdscr.clear()
        for i, line in enumerate(help_text):
            if i < self.height - 1:
                self.stdscr.addstr(i, 0, line)
        
        self.stdscr.refresh()
        self.stdscr.getch()


class UIManager:
    """Main UI manager for the application"""
    
    def __init__(self, journal: Journal, settings: Settings):
        self.journal = journal
        self.settings = settings
        self.dialog: Optional[Dialog] = None
        self.editor: Optional[Editor] = None
        self.menu: Optional[Menu] = None
        self.stdscr = None
    
    def initialize(self, stdscr) -> None:
        """Initialize the UI manager"""
        self.stdscr = stdscr
        self.dialog = Dialog(stdscr)
        self.editor = Editor(stdscr)
        
        # Set up curses
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.clear()
    
    def _ensure_initialized(self) -> None:
        """Ensure dialog and editor are initialized"""
        if self.dialog is None or self.editor is None:
            raise RuntimeError("UIManager not initialized. Call initialize() first.")
    
    def _get_dialog(self) -> Dialog:
        """Get the dialog instance, ensuring it's initialized"""
        self._ensure_initialized()
        assert self.dialog is not None
        return self.dialog
    
    def _get_editor(self) -> Editor:
        """Get the editor instance, ensuring it's initialized"""
        self._ensure_initialized()
        assert self.editor is not None
        return self.editor
    
    def show_main_menu(self, stdscr) -> Optional[MenuItem]:
        """Show the main menu"""
        items = [
            MenuItem(MenuOptions.NEW_BLANK_ENTRY.value, self._new_blank_entry, Shortcuts.NEW_ENTRY.value),
            MenuItem(MenuOptions.NEW_TEMPLATE_ENTRY.value, self._new_template_entry, Shortcuts.TEMPLATE_ENTRY.value),
            MenuItem(MenuOptions.EDIT_TODAY.value, self._edit_today, Shortcuts.EDIT_TODAY.value),
            MenuItem(MenuOptions.VIEW_ENTRIES.value, self._view_entries),
            MenuItem(MenuOptions.SEARCH_ENTRIES.value, self._search_entries, Shortcuts.SEARCH.value),
            MenuItem(MenuOptions.EXPORT_ENTRIES.value, self._export_entries),
            MenuItem(MenuOptions.IMPORT_ENTRIES.value, self._import_entries),
            MenuItem(MenuOptions.BACKUP.value, self._backup, Shortcuts.BACKUP.value),
            MenuItem(MenuOptions.SETTINGS.value, self._settings, Shortcuts.SETTINGS.value),
            MenuItem(MenuOptions.HELP.value, self._help, Shortcuts.HELP.value),
            MenuItem(MenuOptions.QUIT.value, self._quit, Shortcuts.QUIT.value),
        ]
        
        self.menu = Menu(stdscr, "Daily Journal", items)
        return self.menu.display()
    
    def _new_blank_entry(self) -> None:
        """Create a new blank entry"""
        dialog = self._get_dialog()
        editor = self._get_editor()
        
        # Get entry details from user
        title = dialog.input_text("Title: ")
        if title is None:  # User cancelled
            return
        
        tags = dialog.input_text("Tags (space separated): ")
        if tags is None:  # User cancelled
            return
        
        # Get content from editor
        content = editor.edit_text("New Entry")
        if content is None:  # User cancelled
            return
        
        # Create the entry
        success = self.journal.create_entry(title, content, tags)
        
        if success:
            dialog.show_message("Success", "Entry created successfully!", "success")
        else:
            dialog.show_message("Error", "Failed to create entry", "error")
    
    def _new_template_entry(self) -> None:
        """Create a new entry with template"""
        dialog = self._get_dialog()
        # For now, just call the blank entry method
        # TODO: Implement template selection
        dialog.show_message("Info", "Template entry not implemented yet. Using blank entry.", "info")
        self._new_blank_entry()
    
    def _edit_today(self) -> None:
        """Edit today's journal"""
        dialog = self._get_dialog()
        editor = self._get_editor()
        
        today_file = self.journal.get_today_filename()
        content = self.journal.read_file(today_file)
        
        if not content:
            dialog.show_message("Info", "Today's journal is empty. Creating new entry.", "info")
            self._new_blank_entry()
            return
        
        # Edit the content
        new_content = editor.edit_text(f"Edit: {today_file}", content)
        if new_content is not None:
            success = self.journal.write_file(today_file, new_content)
            if success:
                dialog.show_message("Success", "Journal updated successfully!", "success")
            else:
                dialog.show_message("Error", "Failed to update journal", "error")
    
    def _view_entries(self) -> None:
        """View journal entries"""
        dialog = self._get_dialog()
        files = self.journal.get_journal_files()
        
        if not files:
            dialog.show_message("Info", "No journal files found.", "info")
            return
        
        # Create menu items for each file
        items = []
        for filename in files:
            display_name = filename.replace('.md', '')
            items.append(MenuItem(display_name, lambda f=filename: self._view_file(f)))
        
        # Show file selection menu
        menu = Menu(self.stdscr, "Select File to View", items)
        selected_item = menu.display()
        
        if selected_item:
            selected_item.action()
    
    def _view_file(self, filename: str) -> None:
        """View a specific file"""
        dialog = self._get_dialog()
        content = self.journal.read_file(filename)
        
        if not content:
            dialog.show_message("Info", f"File {filename} is empty.", "info")
            return
        
        # Show content in a dialog
        lines = content.split('\n')
        display_content = '\n'.join(lines[:20])  # Show first 20 lines
        if len(lines) > 20:
            display_content += f"\n\n... and {len(lines) - 20} more lines"
        
        dialog.show_message(f"Viewing: {filename}", display_content, "info")
    
    def _search_entries(self) -> None:
        """Search journal entries"""
        dialog = self._get_dialog()
        query = dialog.input_text("Search query: ")
        if not query:
            return
        
        # Perform search
        results = self.journal.search_entries(query)
        
        if not results:
            dialog.show_message("Search Results", "No entries found matching your query.", "info")
            return
        
        # Show results
        result_text = f"Found {len(results)} entries:\n\n"
        for i, entry in enumerate(results[:10]):  # Show first 10 results
            result_text += f"{i+1}. {entry.title} ({entry.date})\n"
            result_text += f"   {entry.content[:50]}...\n\n"
        
        if len(results) > 10:
            result_text += f"... and {len(results) - 10} more results"
        
        dialog.show_message("Search Results", result_text, "info")
    
    def _export_entries(self) -> None:
        """Export journal entries"""
        dialog = self._get_dialog()
        dialog.show_message("Info", "Export functionality not implemented yet.", "info")
    
    def _import_entries(self) -> None:
        """Import journal entries"""
        dialog = self._get_dialog()
        dialog.show_message("Info", "Import functionality not implemented yet.", "info")
    
    def _backup(self) -> None:
        """Create backup"""
        dialog = self._get_dialog()
        success = self.journal.create_backup()
        
        if success:
            dialog.show_message("Success", "Backup created successfully!", "success")
        else:
            dialog.show_message("Error", "Failed to create backup", "error")
    
    def _settings(self) -> None:
        """Show settings"""
        dialog = self._get_dialog()
        # Get current settings
        settings_dict = self.settings.to_dict()
        
        # Display settings
        settings_text = "Current Settings:\n\n"
        for key, value in settings_dict.items():
            settings_text += f"{key}: {value}\n"
        
        dialog.show_message("Settings", settings_text, "info")
    
    def _help(self) -> None:
        """Show help"""
        dialog = self._get_dialog()
        help_text = """
Daily Journal - Help

Navigation:
- Arrow keys: Navigate menus
- Enter: Select item
- ESC: Cancel/go back
- Ctrl+C: Quit application

Features:
- New Entry: Create a new journal entry
- Edit Today: Edit today's journal file
- View Entries: Browse and view journal files
- Search: Search through all entries
- Backup: Create backup of journal files
- Settings: View current settings

For more information, see the README file.
        """
        
        dialog.show_message("Help", help_text, "info")
    
    def _quit(self) -> None:
        """Quit application"""
        dialog = self._get_dialog()
        if dialog.confirm("Quit", "Are you sure you want to quit?"):
            # This will be handled by the main application loop
            raise KeyboardInterrupt 
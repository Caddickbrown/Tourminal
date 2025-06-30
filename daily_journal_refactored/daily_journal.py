#!/usr/bin/env python3
"""
Daily Journal - Refactored Version
Main application entry point.
"""

import sys
import curses
from typing import Optional

from journal_data import Journal, Settings
from journal_ui import UIManager, MenuItem


class JournalApp:
    """Main application class"""
    
    def __init__(self):
        self.settings = Settings()
        self.journal = Journal(self.settings)
        self.ui_manager = UIManager(self.journal, self.settings)
        self.running = True
    
    def run(self, stdscr) -> None:
        """Run the main application loop"""
        try:
            # Initialize UI
            self.ui_manager.initialize(stdscr)
            
            # Main application loop
            while self.running:
                # Show main menu
                selected_item = self.ui_manager.show_main_menu(stdscr)
                
                if selected_item is None:
                    # User cancelled (ESC pressed)
                    continue
                
                # Execute selected action
                try:
                    selected_item.action()
                except Exception as e:
                    # Show error message
                    self.ui_manager.dialog.show_message(
                        "Error",
                        f"An error occurred: {str(e)}",
                        "error"
                    )
        
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        finally:
            # Cleanup
            curses.endwin()
    
    def quit(self) -> None:
        """Quit the application"""
        self.running = False


def main():
    """Main entry point"""
    try:
        # Create and run application
        app = JournalApp()
        curses.wrapper(app.run)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
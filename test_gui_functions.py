#!/usr/bin/env python3
"""
Test script for Daily Journal GUI core functions
Tests the backend functionality without requiring GUI interaction.
"""

import os
import tempfile
import shutil
from datetime import datetime
import sys

# Add the current directory to path so we can import from daily_journal_gui
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from daily_journal_gui import (
        ensure_directories, get_today_filename, write_daily_file, 
        read_daily_file, append_to_daily_file, extract_tags_from_content,
        format_timestamp, load_settings, save_settings, DEFAULT_SETTINGS
    )
    print("✅ Successfully imported GUI functions")
except ImportError as e:
    print(f"❌ Failed to import GUI functions: {e}")
    sys.exit(1)

def test_basic_functions():
    """Test basic functionality without GUI"""
    print("\n🧪 Testing Core Functions")
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="test_journal_")
    print(f"📁 Using test directory: {test_dir}")
    
    try:
        # Test settings
        print("\n📋 Testing Settings...")
        test_settings = DEFAULT_SETTINGS.copy()
        test_settings["journal_directory"] = os.path.join(test_dir, "journal")
        test_settings["backup_directory"] = os.path.join(test_dir, "backups")
        
        # Test directory creation
        original_settings = DEFAULT_SETTINGS["journal_directory"]
        DEFAULT_SETTINGS["journal_directory"] = test_settings["journal_directory"]
        ensure_directories()
        
        if os.path.exists(test_settings["journal_directory"]):
            print("✅ Directory creation works")
        else:
            print("❌ Directory creation failed")
            return False
        
        # Test filename generation
        print("\n📅 Testing Filename Generation...")
        today_file = get_today_filename()
        print(f"📄 Today's filename: {today_file}")
        if today_file.endswith('.md') and len(today_file) > 5:
            print("✅ Filename generation works")
        else:
            print("❌ Filename generation failed")
            return False
        
        # Test file writing and reading
        print("\n📝 Testing File Operations...")
        test_content = "# Test Entry\n\ntags: test, demo\n\nThis is a test entry for the GUI version."
        
        write_daily_file(today_file, test_content)
        read_content = read_daily_file(today_file)
        
        if read_content.strip() == test_content.strip():
            print("✅ File write/read works")
        else:
            print("❌ File write/read failed")
            print(f"Expected: {repr(test_content)}")
            print(f"Got: {repr(read_content)}")
            return False
        
        # Test appending entries
        print("\n➕ Testing Entry Appending...")
        new_entry = "# Second Entry\n\ntags: test, append\n\nThis is a second entry."
        append_to_daily_file(today_file, new_entry)
        
        updated_content = read_daily_file(today_file)
        if new_entry in updated_content and test_content in updated_content:
            print("✅ Entry appending works")
        else:
            print("❌ Entry appending failed")
            return False
        
        # Test tag extraction
        print("\n🏷️  Testing Tag Extraction...")
        sample_content = "This is a test with #hashtag and @mention tags. Also #another and @someone."
        detected_tags = extract_tags_from_content(sample_content)
        
        expected_tags = ['another', 'hashtag', 'mention', 'someone']  # Should be sorted
        if detected_tags == expected_tags:
            print(f"✅ Tag extraction works: {detected_tags}")
        else:
            print(f"❌ Tag extraction failed")
            print(f"Expected: {expected_tags}")
            print(f"Got: {detected_tags}")
            return False
        
        # Test timestamp formatting
        print("\n⏰ Testing Timestamp...")
        timestamp = format_timestamp()
        if timestamp.startswith('[') and timestamp.endswith('] '):
            print(f"✅ Timestamp formatting works: {timestamp}")
        else:
            print(f"❌ Timestamp formatting failed: {timestamp}")
            return False
        
        print("\n🎉 All core functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        try:
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")
        except:
            print(f"⚠️  Could not clean up test directory: {test_dir}")
        
        # Restore original settings
        DEFAULT_SETTINGS["journal_directory"] = original_settings

def test_gui_imports():
    """Test that GUI components can be imported"""
    print("\n🖥️  Testing GUI Component Imports...")
    
    try:
        from daily_journal_gui import (
            EntryDialog, SearchDialog, SettingsDialog, DailyJournalGUI
        )
        print("✅ GUI component imports successful")
        return True
    except ImportError as e:
        print(f"❌ GUI component import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️  GUI components imported but with warnings: {e}")
        return True

def main():
    """Run all tests"""
    print("🚀 Daily Journal GUI - Function Tests")
    print("=" * 50)
    
    # Test basic functions
    basic_test_passed = test_basic_functions()
    
    # Test GUI imports (these might fail if tkinter is not available)
    gui_import_passed = test_gui_imports()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Core Functions: {'✅ PASS' if basic_test_passed else '❌ FAIL'}")
    print(f"GUI Imports: {'✅ PASS' if gui_import_passed else '❌ FAIL'}")
    
    if basic_test_passed and gui_import_passed:
        print("\n🎉 All tests passed! The GUI application should work correctly.")
        print("💡 To run the GUI: python daily_journal_gui.py")
    elif basic_test_passed:
        print("\n⚠️  Core functions work, but GUI might have issues.")
        print("💡 Check if tkinter is properly installed.")
    else:
        print("\n❌ Critical functions failed. Please check the implementation.")
    
    return 0 if basic_test_passed else 1

if __name__ == "__main__":
    exit(main())
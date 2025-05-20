#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
from pathlib import Path


class FileOrganizer:
    """A utility to organize files based on patterns in their names."""
    
    def __init__(self, source_dir, dest_dir=None, dry_run=False):
        """Initialize the organizer with source and destination directories.
        
        Args:
            source_dir (str): Directory containing files to organize
            dest_dir (str, optional): Base directory for organized files. If None, uses source_dir
            dry_run (bool): If True, only shows what would be done without moving files
        """
        self.source_dir = os.path.abspath(source_dir)
        self.dest_dir = os.path.abspath(dest_dir) if dest_dir else self.source_dir
        self.dry_run = dry_run
        
    def find_files_with_pattern(self, pattern, recursive=True):
        """Find all files containing the specified pattern.
        
        Args:
            pattern (str): String pattern to search for in filenames
            recursive (bool): Whether to search recursively through subdirectories
            
        Returns:
            list: List of file paths matching the pattern
        """
        matching_files = []
        
        # Define the search directory
        search_path = Path(self.source_dir)
        
        # Use glob for recursive searching if requested
        if recursive:
            all_files = search_path.glob('**/*') # **=search through all subdirectories at any depth 
        else: # * = match any file or folder name
            all_files = search_path.glob('*') #use .glob for - finding files that match a pattern. 
        # Filter files (not directories) containing the pattern
        
            
        # searching for files with the aiming key word in file names
        for file_path in all_files:
            if file_path.is_file() and pattern.lower() in file_path.name.lower():
                matching_files.append(str(file_path))
                
        return matching_files # returns matched files' name in list
    
    def organize_files(self, pattern, target_folder_name=None):
        """Move files matching a pattern to a target folder.
        
        Args:
            pattern (str): Pattern to search for in filenames
            target_folder_name (str, optional): Name of folder to move files to.
                                               If None, uses the pattern as folder name
                                               
        Returns:
            int: Number of files moved
        """
        if target_folder_name is None:
            target_folder_name = pattern
            
        # Create the target directory if it doesn't exist
        target_dir = os.path.join(self.dest_dir, target_folder_name)
        if not self.dry_run and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created directory: {target_dir}")
            
        # Find matching files
        matching_files = self.find_files_with_pattern(pattern)
        
        # Move each file to the target directory
        moved_count = 0
        for file_path in matching_files:
            file_name = os.path.basename(file_path)
            destination = os.path.join(target_dir, file_name)
            
            # Skip if source and destination are the same
            if os.path.abspath(file_path) == os.path.abspath(destination):
                continue
                
            if self.dry_run:
                print(f"Would move: {file_path} -> {destination}")
            else:
                try:
                    shutil.move(file_path, destination)
                    print(f"Moved: {file_path} -> {destination}")
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")
                    
        return moved_count
    
    def organize_multiple_patterns(self, patterns_dict):
        """Organize files based on multiple patterns.
        
        Args:
            patterns_dict (dict): Dictionary mapping patterns to folder names
                                 {pattern: folder_name}
                                 
        Returns:
            dict: Summary of files moved for each pattern
        """
        results = {}
        
        for pattern, folder_name in patterns_dict.items():
            num_moved = self.organize_files(pattern, folder_name)
            results[pattern] = num_moved
            
        return results


def interactive_mode():
    """Run the program in interactive mode with user prompts."""
    print("\n" + "=" * 60)
    print("📁 WELCOME TO FILE ORGANIZER 📁")
    print("This program helps you organize files based on keywords in their names.")
    print("=" * 60)
    print("\nUSAGE GUIDE:")
    print("1. Enter a directory path to search in (or just press Enter for default)")
    print("   Examples: '/Users/yourname/Desktop' or '~/Downloads'")
    print("2. Navigate to subfolders by simply typing the subfolder name")
    print("3. Use '...' to go up one level or 'search' to start searching for files")
    print("4. Enter keywords to search for in filenames (like 'lecture' or 'report')")
    print("5. Choose whether to search in subfolders (recommended for nested files)")
    print("6. Choose a name for the folder where matching files will be moved")
    print("7. Confirm the move operation")
    print("\nTIP: You can organize multiple sets of files in one session!")
    print("=" * 60 + "\n")
    
    # Get valid source directory
    valid_dir = False
    while not valid_dir:
        default_dir = os.path.expanduser("~/Documents")
        source_dir = input(f"Enter the directory path to search in (default: {default_dir}): ")
        if not source_dir:
            source_dir = default_dir
        
        # Expand user directory if needed (convert ~ to actual path)
        source_dir = os.path.expanduser(source_dir)
        
        # Validate source directory
        if not os.path.isdir(source_dir):
            print(f"Error: '{source_dir}' is not a valid directory.")
            print("Please enter a complete path to an existing directory on your computer.\n")
        else:
            valid_dir = True
    
    print(f"\nNow in: {source_dir}")
    
    # Store visited directories to make navigation easier
    visited_dirs = [source_dir]
    current_dir_idx = 0
    
    # Navigation loop
    while True:
        # Show subdirectories to help user navigate
        subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
        
        print("\nAvailable subfolders:")
        if subdirs:
            for subdir in sorted(subdirs[:15]):  # Show up to 15 subdirectories, sorted alphabetically
                print(f"  • {subdir}")
            if len(subdirs) > 15:
                print(f"  • ... and {len(subdirs)-15} more")
        else:
            print("  • (No subfolders found)")
        
        # Navigation options
        print("\nNavigation options:")
        print("  • Type a subfolder name to navigate into it")
        print("  • Type '...' to go up to parent directory")
        print("  • Type 'search' to start searching for files in current directory")
        print("  • Type 'quit' to exit the program")
        
        nav_choice = input("\nEnter navigation choice: ")
        
        if nav_choice.lower() == 'quit':
            print("\nExiting File Organizer. Goodbye!")
            sys.exit(0)
        elif nav_choice.lower() == '...':
            # Go up one level
            parent_dir = os.path.dirname(source_dir)
            if parent_dir and os.path.exists(parent_dir):
                source_dir = parent_dir
                print(f"\nNow in: {source_dir}")
                # Add to visited dirs if not already there
                if source_dir not in visited_dirs:
                    visited_dirs.append(source_dir)
                current_dir_idx = visited_dirs.index(source_dir)
            else:
                print("Already at the root directory.")
        elif nav_choice.lower() == 'search':
            # Break out of navigation loop to start searching
            break
        else:
            # Check if user entered a valid subfolder name
            potential_dir = os.path.join(source_dir, nav_choice)
            if os.path.isdir(potential_dir):
                source_dir = potential_dir
                print(f"\nNow in: {source_dir}")
                # Add to visited dirs if not already there
                if source_dir not in visited_dirs:
                    visited_dirs.append(source_dir)
                current_dir_idx = visited_dirs.index(source_dir)
            else:
                print(f"'{nav_choice}' is not a valid subfolder in the current directory.")
    
    # Create organizer
    organizer = FileOrganizer(source_dir)
    
    while True:
        print("\n" + "-" * 50)
        # Step 1: Get search keyword
        pattern = input("Enter keyword to search for in filenames (or 'navigate' to change directory, 'quit' to exit): ")
        if pattern.lower() == 'quit':
            break
        elif pattern.lower() == 'navigate':
            # Return to directory navigation
            while True:
                # Show current directory and subdirectories
                print(f"\nCurrent directory: {source_dir}")
                
                subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
                
                print("\nAvailable subfolders:")
                if subdirs:
                    for subdir in sorted(subdirs[:15]):
                        print(f"  • {subdir}")
                    if len(subdirs) > 15:
                        print(f"  • ... and {len(subdirs)-15} more")
                else:
                    print("  • (No subfolders found)")
                
                print("\nNavigation options:")
                print("  • Type a subfolder name to navigate into it")
                print("  • Type '...' to go up to parent directory")
                print("  • Type 'search' to start searching for files in current directory")
                print("  • Type 'quit' to exit the program")
                
                nav_choice = input("\nEnter navigation choice: ")
                
                if nav_choice.lower() == 'quit':
                    print("\nExiting File Organizer. Goodbye!")
                    sys.exit(0)
                elif nav_choice.lower() == '...':
                    # Go up one level
                    parent_dir = os.path.dirname(source_dir)
                    if parent_dir and os.path.exists(parent_dir):
                        source_dir = parent_dir
                        print(f"\nNow in: {source_dir}")
                        # Update organizer with new source directory
                        organizer = FileOrganizer(source_dir)
                    else:
                        print("Already at the root directory.")
                elif nav_choice.lower() == 'search':
                    # Break out of navigation loop to start searching
                    break
                else:
                    # Check if user entered a valid subfolder name
                    potential_dir = os.path.join(source_dir, nav_choice)
                    if os.path.isdir(potential_dir):
                        source_dir = potential_dir
                        print(f"\nNow in: {source_dir}")
                        # Update organizer with new source directory
                        organizer = FileOrganizer(source_dir)
                    else:
                        print(f"'{nav_choice}' is not a valid subfolder in the current directory.")
            
            # Continue the main loop to search files
            continue
            
        # Ask about recursive search
        recursive = input("Search in all subfolders too? (y/n, recommended 'y' for nested files): ")
        use_recursive = recursive.lower() != 'n'  # Default to True unless explicitly 'n'
            
        # Show matching files first
        matching_files = organizer.find_files_with_pattern(pattern, recursive=use_recursive)
        
        if not matching_files:
            print(f"No files found containing '{pattern}'.")
            print(f"Tips: Try a shorter keyword or check if you're searching in the right directory.")
            if not use_recursive:
                print("Consider enabling subfolder search with 'y' for nested files.")
            continue
            
        print(f"\nFound {len(matching_files)} files containing '{pattern}':")
        for i, file_path in enumerate(matching_files, 1):
            # Show relative path for clarity when using recursive search
            if use_recursive:
                rel_path = os.path.relpath(file_path, source_dir)
                print(f"  {i}. {rel_path}")
            else:
                print(f"  {i}. {os.path.basename(file_path)}")
            
        # Step 2: Get target folder name
        target_folder = input(f"\nEnter name for the destination folder (default: '{pattern}'): ")
        if not target_folder:
            target_folder = pattern
            
        # Confirm before moving
        confirm = input(f"\nReady to move {len(matching_files)} files to '{target_folder}' folder. Proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            continue
            
        # Move the files
        moved = organizer.organize_files(pattern, target_folder)
        print(f"\nSuccessfully moved {moved} files to '{target_folder}' folder.")
        print(f"Full path: {os.path.join(organizer.dest_dir, target_folder)}")
        
        # Ask if user wants to navigate to another directory before continuing
        dir_option = input("\nWould you like to navigate to a different directory? (y/n): ")
        if dir_option.lower() == 'y':
            print("\nEntering directory navigation mode...")
            # Return to directory navigation
            while True:
                # Show current directory and subdirectories
                print(f"\nCurrent directory: {source_dir}")
                
                subdirs = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
                
                print("\nAvailable subfolders:")
                if subdirs:
                    for subdir in sorted(subdirs[:15]):
                        print(f"  • {subdir}")
                    if len(subdirs) > 15:
                        print(f"  • ... and {len(subdirs)-15} more")
                else:
                    print("  • (No subfolders found)")
                
                print("\nNavigation options:")
                print("  • Type a subfolder name to navigate into it")
                print("  • Type '...' to go up to parent directory")
                print("  • Type 'search' to start searching for files in current directory")
                print("  • Type 'quit' to exit the program")
                
                nav_choice = input("\nEnter navigation choice: ")
                
                if nav_choice.lower() == 'quit':
                    print("\nExiting File Organizer. Goodbye!")
                    sys.exit(0)
                elif nav_choice.lower() == '...':
                    # Go up one level
                    parent_dir = os.path.dirname(source_dir)
                    if parent_dir and os.path.exists(parent_dir):
                        source_dir = parent_dir
                        print(f"\nNow in: {source_dir}")
                        # Update organizer with new source directory
                        organizer = FileOrganizer(source_dir)
                    else:
                        print("Already at the root directory.")
                elif nav_choice.lower() == 'search':
                    # Break out of navigation loop to start searching
                    break
                else:
                    # Check if user entered a valid subfolder name
                    potential_dir = os.path.join(source_dir, nav_choice)
                    if os.path.isdir(potential_dir):
                        source_dir = potential_dir
                        print(f"\nNow in: {source_dir}")
                        # Update organizer with new source directory
                        organizer = FileOrganizer(source_dir)
                    else:
                        print(f"'{nav_choice}' is not a valid subfolder in the current directory.")
    
    print("\nThank you for using File Organizer! Have a great day!")


def main():
    """Main function to handle command-line or interactive usage."""
    
    # Check if any command line arguments were provided
    if len(sys.argv) > 1:
        # Command line mode
        parser = argparse.ArgumentParser(description='Organize files based on filename patterns')
        parser.add_argument('source_dir', nargs='?', help='Directory containing files to organize')
        parser.add_argument('--dest-dir', help='Destination directory for organized files')
        parser.add_argument('--pattern', action='append', help='Pattern to search for (can be used multiple times)')
        parser.add_argument('--map', action='append', help='Map pattern to folder name (format: pattern:folder_name)')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without moving files')
        parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
        
        args = parser.parse_args()
        
        # If interactive flag is set, run interactive mode
        if args.interactive:
            interactive_mode()
            return
            
        # Validate source directory
        if not args.source_dir:
            print("Error: Source directory is required.")
            parser.print_help()
            return
            
        # Create file organizer
        organizer = FileOrganizer(args.source_dir, args.dest_dir, args.dry_run)
        
        # Handle basic patterns (each pattern gets its own folder named after the pattern)
        if args.pattern:
            for pattern in args.pattern:
                organizer.organize_files(pattern)
                
        # Handle mapped patterns (each pattern maps to a specified folder name)
        if args.map:
            patterns_dict = {}
            for mapping in args.map:
                try:
                    pattern, folder_name = mapping.split(':', 1)
                    patterns_dict[pattern] = folder_name
                except ValueError:
                    print(f"Invalid mapping format: {mapping}. Use 'pattern:folder_name'")
                    
            organizer.organize_multiple_patterns(patterns_dict)
        
        # If no patterns specified, show usage example
        if not args.pattern and not args.map:
            print("No patterns specified. Example usage:")
            print("python file_organizer.py ~/Documents --pattern lcsw --pattern lec")
            print("python file_organizer.py ~/Documents --map lcsw:LCSW_Files --map lec:Lecture_Notes")
            print("\nOr run in interactive mode:")
            print("python file_organizer.py -i")
    else:
        # No arguments, run interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import winreg
import ctypes
from pathlib import Path
import csv
from datetime import datetime

class ProjectScoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Scout - Find Your Projects")
        self.root.geometry("1200x600")

        self.projects = []
        self.scanning = False
        self.stop_requested = False

        self.found_paths = set()
        self.status_update_counter = 0  # Counter for throttling status updates
        self.projects_added_count = 0  # Counter for GUI refresh
        self.setup_ui()
        self.current_theme = self.get_system_theme()
        self.apply_theme(self.current_theme)

    def setup_ui(self):
        # Top Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(control_frame, text="Click 'Start Scan' to begin searching...")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.scan_btn = ttk.Button(control_frame, text="Start Scan", command=self.toggle_scan)
        self.scan_btn.pack(side=tk.RIGHT, padx=5)

        self.theme_btn = ttk.Button(control_frame, text="☾", width=3, command=self.toggle_theme)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        # Treeview for Projects
        columns = ("name", "path", "type", "git", "status", "created", "modified")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("name", text="Project Name", command=lambda: self.sort_by_column("name"))
        self.tree.heading("path", text="Directory Path", command=lambda: self.sort_by_column("path"))
        self.tree.heading("type", text="Type", command=lambda: self.sort_by_column("type"))
        self.tree.heading("git", text="Git", command=lambda: self.sort_by_column("git"))
        self.tree.heading("status", text="Git Status", command=lambda: self.sort_by_column("status"))
        self.tree.heading("created", text="Created", command=lambda: self.sort_by_column("created"))
        self.tree.heading("modified", text="Modified", command=lambda: self.sort_by_column("modified"))

        self.tree.column("name", width=120)
        self.tree.column("path", width=350)
        self.tree.column("type", width=100)
        self.tree.column("git", width=50)
        self.tree.column("status", width=80)
        self.tree.column("created", width=120)
        self.tree.column("modified", width=120)
        
        self.sort_reverse = {}  # Track sort direction for each column

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom Buttons
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        ttk.Button(bottom_frame, text="Open in Explorer", command=self.open_in_explorer).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Open with Antigravity", command=self.open_with_antigravity).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5)
        
        # Color tags
        self.tree.tag_configure("git_yes", background="#e1f5fe") # Light blue for git projects
        self.tree.tag_configure("dirty", foreground="#d32f2f")   # Red text for uncommitted changes

    def get_system_theme(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "Light" if value == 1 else "Dark"
        except Exception:
            return "Light"

    def toggle_theme(self):
        new_theme = "Dark" if self.current_theme == "Light" else "Light"
        self.apply_theme(new_theme)

    def apply_theme(self, theme):
        self.current_theme = theme
        style = ttk.Style(self.root)
        style.theme_use("clam")
        
        if theme == "Dark":
            bg = "#2b2b2b"
            fg = "#ffffff"
            field_bg = "#383838"
            
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg, fieldbackground=field_bg)
            style.configure("Treeview", background="#383838", foreground=fg, fieldbackground="#383838")
            style.configure("Treeview.Heading", background="#404040", foreground=fg, relief="flat")
            style.map("Treeview", background=[("selected", "#005a9e")])
            
            style.configure("TButton", background="#404040", foreground=fg, bordercolor="#505050")
            style.map("TButton", background=[("active", "#505050")])
            
            # Update tags for Dark Mode
            self.tree.tag_configure("git_yes", background="#1e3a50")
            self.tree.tag_configure("dirty", foreground="#ff6b6b")
            
            if hasattr(self, 'theme_btn'):
                self.theme_btn.config(text="☀")
                
            # Windows Title Bar Dark
            try:
                # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass
                
        else:
            bg = "#f0f0f0"
            fg = "#000000"
            
            self.root.configure(bg=bg)
            style.configure(".", background=bg, foreground=fg)
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
            style.configure("Treeview.Heading", background="#f0f0f0", foreground="black")
            style.map("Treeview", background=[("selected", "#0078d7")])
            
            style.configure("TButton", background="#e1e1e1", foreground="black")
            style.map("TButton", background=[("active", "#e5f1fb")])
            
            # Update tags for Light Mode
            self.tree.tag_configure("git_yes", background="#e1f5fe")
            self.tree.tag_configure("dirty", foreground="#d32f2f")
            
            if hasattr(self, 'theme_btn'):
                self.theme_btn.config(text="☾")
                
            # Windows Title Bar Light
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                value = ctypes.c_int(0)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            except:
                pass

    def toggle_scan(self):
        if self.scanning:
            self.stop_requested = True
            self.status_label.config(text="Stopping scan...")
        else:
            self.start_scan()

    def start_scan(self):
        self.projects = []
        self.found_paths = set()
        self.status_update_counter = 0  # Reset counter
        self.projects_added_count = 0  # Reset projects counter
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.scanning = True
        self.stop_requested = False
        self.scan_btn.config(text="Stop Scan")
        
        # Start scanning in a background thread
        thread = threading.Thread(target=self.run_scanner, daemon=True)
        thread.start()

    def is_network_drive(self, path):
        """Check if path is on a network drive"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(path)
                # DRIVE_REMOTE = 4
                return drive_type == 4
        except:
            pass
        return False

    def run_scanner(self):
        # Search priorities: Home first, then D:, then others (skip network drives and C: initially)
        # get_available_drives() already filters out network drives, so we can use them directly
        home = str(Path.home())
        drives = sorted(self.get_available_drives())
        
        # Start with home folder and D: drive
        search_paths = [home]
        
        # Add D: drive second if it exists
        if "D:\\" in drives:
            search_paths.append("D:\\")
        
        # Add other local drives (skip C: for now)
        for d in drives:
            if d not in search_paths and d != "C:\\":
                search_paths.append(d)
        
        # Add C: drive last (to avoid system folders that slow things down)
        if "C:\\" in drives:
            search_paths.append("C:\\")

        excluded_folders = {
            "windows", "program files", "program files (x86)", 
            "programdata", "recovery", "system volume information",
            "node_modules", "venv", ".venv", "__pycache__", ".git",
            "appdata", "local", "roaming", "microsoft", "cache"
            , "pictures", "music", "videos", "desktop", "links", ".cursor",
            "favorites", "contacts", "searches", "saved games", "objects",
            "$recycle.bin", "recycle.bin", "exception", "user data",
            # WordPress/CMS folders that generate false positives
            "uploads", "plugins", "themes", "wp-content", "wp-includes", "wp-admin",
            "vendor", "assets", "libs", "lib", "libraries", "documentation",
            # Build folders
            "dist", "build", "target", "out", "bin", "obj"
        }
        
        # Portable browser name patterns (case insensitive check will be done)
        self.portable_browser_patterns = {
            "firefox", "chrome", "opera", "edge", "brave", "vivaldi",
            "tor browser", "waterfox", "pale moon", "librewolf"
        }
        
        system_excludes = {
            "c:\\windows", "c:\\program files", "c:\\program files (x86)",
            "c:\\programdata", "c:\\recovery", "c:\\system volume information",
            "c:\\$recycle.bin", "d:\\$recycle.bin"
        }

        for base_path in search_paths:
            if self.stop_requested: break
            if base_path.lower() in system_excludes: continue
            self.update_status(f"Scanning {base_path}...")
            self.scan_directory(base_path, excluded_folders, depth=0)

        self.scanning = False
        self.root.after(0, lambda: self.scan_btn.config(text="Start Scan"))
        self.update_status("Scan complete.")

    def get_available_drives(self):
        """Get available local drives, skipping network drives"""
        import string
        from ctypes import windll
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        kernel32 = windll.kernel32
        
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                path = f"{letter}:\\"
                # Check drive type before checking if it exists
                # This avoids hanging on network drives
                try:
                    drive_type = kernel32.GetDriveTypeW(path)
                    # DRIVE_UNKNOWN = 0, DRIVE_NO_ROOT_DIR = 1, DRIVE_REMOVEABLE = 2
                    # DRIVE_FIXED = 3, DRIVE_REMOTE = 4, DRIVE_CDROM = 5, DRIVE_RAMDISK = 6
                    # Only include fixed (local) drives (3), skip network (4) and others
                    if drive_type == 3:  # DRIVE_FIXED - local hard drive
                        # Quick check if path exists (should be fast for local drives)
                        try:
                            if os.path.exists(path):
                                drives.append(path)
                        except (OSError, PermissionError):
                            pass  # Skip if can't access
                    # Skip all other drive types (network, CD-ROM, removable, etc.)
                except Exception:
                    pass  # Skip if GetDriveTypeW fails
            bitmask >>= 1
        return drives

    def get_directory_dates(self, path):
        """Get creation and modification dates of directory"""
        try:
            stat = os.stat(path)
            created = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M")
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            return created, modified
        except Exception:
            return "Unknown", "Unknown"

    def check_git_status(self, path):
        try:
            # git status --porcelain returns empty if clean, and lists files if dirty
            # Use timeout and faster flags to prevent hanging
            result = subprocess.run(
                ["git", "status", "--porcelain", "--ignore-submodules=dirty"],
                cwd=path,
                capture_output=True,
                text=True,
                check=False,
                timeout=2,  # 2 second timeout to prevent hanging
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode != 0:
                return "Unknown"
            
            return "Dirty" if result.stdout.strip() else "Clean"
        except subprocess.TimeoutExpired:
            return "Timeout"
        except Exception:
            return "Error"

    def is_portable_browser_folder(self, folder_name):
        """Check if folder name indicates a portable browser"""
        folder_lower = folder_name.lower()
        # Check if folder contains "portable" and any browser name
        if "portable" in folder_lower:
            for browser in self.portable_browser_patterns:
                if browser in folder_lower:
                    return True
        return False

    def is_subfolder_of_project(self, path):
        """Recursively check parent directories to see if this is part of a larger project"""
        # Max levels to check up
        max_levels = 8
        current = path
        
        # Don't check the path itself, start with parent
        parent = os.path.dirname(path)
        
        for _ in range(max_levels):
            if parent == current: # Reached root drive
                break
                
            # Check for project markers in this parent directory
            try:
                # Indicators that suggest the parent is the REAL project root
                indicators = [
                    ".git", "package.json", "composer.json", "pubspec.yaml",
                    "go.mod", "Cargo.toml", "pom.xml", "manage.py", "requirements.txt",
                    "mix.exs", "build.sbt", ".gitignore", "Makefile",
                    "webpack.config.js", "rollup.config.js"
                ]
                
                # Check for WordPress Theme (style.css + functions.php)
                if os.path.exists(os.path.join(parent, "style.css")) and \
                   os.path.exists(os.path.join(parent, "functions.php")):
                    return True
                
                # Check for standard indicators
                for indicator in indicators:
                    if os.path.exists(os.path.join(parent, indicator)):
                        return True
                        
                # Check if parent has a "src" directory (strong indicator of project root)
                if os.path.exists(os.path.join(parent, "src")) and os.path.isdir(os.path.join(parent, "src")):
                    return True

                # Check for Visual Studio Solution in parent
                if any(f.endswith(".sln") for f in os.listdir(parent)):
                    return True

                # Check if parent matches "folder/folder.php" (WP Plugin) pattern
                parent_name = os.path.basename(parent).lower()
                clean_name = parent_name.replace("-master", "").replace("-main", "")
                
                # Check for exact match or cleaned match
                if os.path.exists(os.path.join(parent, f"{parent_name}.php")) or \
                   os.path.exists(os.path.join(parent, f"{clean_name}.php")):
                    return True
                        
            except (PermissionError, OSError):
                pass
            
            # Move up
            current = parent
            parent = os.path.dirname(current)
            
        return False

    def format_path_for_display(self, path, max_depth=3):
        """Format path for display showing only first max_depth levels"""
        parts = Path(path).parts
        if len(parts) <= max_depth + 1:
            return path
        # Show first max_depth parts, then last part if not too long
        first_parts = list(parts[:max_depth])
        last_part = parts[-1]
        if len(last_part) > 30:
            last_part = last_part[:27] + "..."
        return os.path.join(*first_parts, "...", last_part)

    def is_vendor_or_library_folder(self, path, folder_name):
        """Check if folder is likely a vendor/library folder, not a real project"""
        folder_lower = folder_name.lower()
        path_lower = path.lower()
        
        # Common vendor/library folder patterns
        vendor_patterns = [
            "vendor", "vendors", "third-party", "thirdparty", "external",
            "packages", "libs", "libraries", "dependencies",
            "bower_components", "jspm_packages",
            "mode", "modes",  # CodeMirror modes
            "addons", "add-ons", "plugins", "extensions", "modules"
        ]
        
        # Check if folder name matches vendor patterns
        if any(pattern in folder_lower for pattern in vendor_patterns):
            return True
        
        # Check if path contains WordPress/CMS indicators
        cms_indicators = [
            "wp-content", "wordpress", "joomla", "drupal", "elementor",
            "essential-addons", "epic-news", "eventful", "astra"
        ]
        if any(indicator in path_lower for indicator in cms_indicators):
            return True
        
        # Check if it's a documentation folder with only index.html
        if "documentation" in folder_lower or "docs" == folder_lower:
            return True
            
        return False

    def has_substantial_project_files(self, path, files_in_dir, project_type):
        """Check if folder has substantial project files, not just one index.html"""
        
        # For HTML projects, require more than just index.html
        if project_type == "Web/HTML":
            # Check if there are other meaningful files
            html_files = [f for f in files_in_dir if f.endswith(".html")]
            js_files = [f for f in files_in_dir if f.endswith(".js")]
            css_files = [f for f in files_in_dir if f.endswith(".css")]
            
            # If only index.html exists with no other meaningful files, skip it
            if len(html_files) == 1 and len(js_files) == 0 and len(css_files) == 0:
                return False
                
            # Check for common non-project patterns
            folder_name = os.path.basename(path).lower()
            non_project_names = [
                "mode", "modes", "theme", "addon", "plugin", "extension",
                "help", "about", "documentation", "demo", "example", "sample"
            ]
            if any(name in folder_name for name in non_project_names):
                return False
        
        return True

    def scan_directory(self, path, excluded_folders, depth=0):
        # Update status more frequently - every folder at depth 0-2, every 5th at depth 3-5, etc.
        self.status_update_counter += 1
        should_update = False
        
        if depth <= 2:
            should_update = True  # Always update for top 3 levels
        elif depth == 3 and self.status_update_counter % 5 == 0:
            should_update = True  # Every 5th folder at depth 3
        elif depth == 4 and self.status_update_counter % 10 == 0:
            should_update = True  # Every 10th folder at depth 4
        elif depth <= 5 and self.status_update_counter % 20 == 0:
            should_update = True  # Every 20th folder at depth 5
        
        if should_update:
            display_path = self.format_path_for_display(path, max_depth=3)
            self.update_status(f"Scanning: {display_path}... (Found: {self.projects_added_count})")
            # Force GUI update to process the queue
            try:
                self.root.update_idletasks()
            except:
                pass
        
        try:
            entries = list(os.scandir(path))
        except PermissionError:
            return
        except Exception:
            return

        is_project = False
        project_type = ""
        has_git = False

        files_in_dir = []
        dirs_in_dir = []
        
        for entry in entries:
            try:
                name_lower = entry.name.lower()
                if entry.is_file():
                    files_in_dir.append(name_lower)
                elif entry.is_dir():
                    if name_lower == ".git":
                        has_git = True
                    elif entry.name.startswith("."):
                        continue
                    elif name_lower in excluded_folders:
                        continue
                    elif self.is_portable_browser_folder(entry.name):
                        continue
                    else:
                        dirs_in_dir.append(entry)
            except (PermissionError, OSError):
                continue

        # Identification Logic
        if "package.json" in files_in_dir:
            is_project = True
            # Check for specific frameworks
            if any(f in ["vite.config.js", "vite.config.ts"] for f in files_in_dir):
                project_type = "Vite"
            elif any(f in ["vue.config.js", "nuxt.config.js"] for f in files_in_dir):
                project_type = "Vue.js"
            elif any(f in ["angular.json"] for f in files_in_dir):
                project_type = "Angular"
            elif any(f in ["next.config.js", "next.config.ts"] for f in files_in_dir):
                project_type = "Next.js"
            elif any(f in ["svelte.config.js"] for f in files_in_dir):
                project_type = "Svelte"
            elif any(d.name in ["src", "public"] for d in dirs_in_dir) or any(f in ["tsconfig.json", "jsconfig.json"] for f in files_in_dir):
                # Check if it's React by looking for common React indicators
                package_json_path = os.path.join(path, "package.json")
                if os.path.exists(package_json_path):
                    try:
                        with open(package_json_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            if "react" in content or "react-scripts" in content:
                                project_type = "React"
                            else:
                                project_type = "Node.js"
                    except:
                        project_type = "React"  # Default to React if we can't read
                else:
                    project_type = "React"
            else:
                project_type = "Node.js"
        elif "pubspec.yaml" in files_in_dir:
            is_project = True
            project_type = "Flutter"
        elif any(f.endswith(".sln") or f.endswith(".csproj") or f.endswith(".vbproj") for f in files_in_dir):
            if self.is_subfolder_of_project(path):
                # If we are in a subfolder (e.g. csproj inside a sln folder), skip it
                # UNLESS it is the SLN folder itself (which won't be a subfolder of another sln typically)
                is_project = False
            else:
                is_project = True
                project_type = "C# / .NET"
        elif any(f in ["requirements.txt", "pyproject.toml", "setup.py", "pipfile", "poetry.lock"] for f in files_in_dir):
            is_project = True
            project_type = "Python"
        elif any(f.endswith(".py") for f in files_in_dir) and len([f for f in files_in_dir if f.endswith(".py")]) > 1:
            is_project = True
            project_type = "Python Script"
        elif "build.gradle" in files_in_dir or "build.gradle.kts" in files_in_dir:
            # Check if this is part of a Flutter project
            if self.is_subfolder_of_project(path):
                is_project = False  # Skip as it's part of Flutter project
            else:
                is_project = True
                project_type = "Android/Java/Kotlin"
        elif "pom.xml" in files_in_dir:
            is_project = True
            project_type = "Java/Maven"
        elif any(f.endswith(".xcodeproj") or f.endswith(".xcworkspace") for f in files_in_dir) or any(d.name.endswith(".xcodeproj") for d in dirs_in_dir):
            # Check if this is part of a Flutter project
            if self.is_subfolder_of_project(path):
                is_project = False  # Skip as it's part of Flutter project
            else:
                is_project = True
                project_type = "iOS"
        elif any(f in ["go.mod", "go.sum"] for f in files_in_dir):
            is_project = True
            project_type = "Go"
        elif any(f in ["Cargo.toml"] for f in files_in_dir):
            is_project = True
            project_type = "Rust"
        elif any(f in ["Gemfile"] for f in files_in_dir):
            is_project = True
            project_type = "Ruby"
        elif any(f in ["composer.json"] for f in files_in_dir) or any(f.endswith(".php") for f in files_in_dir):
            if self.is_subfolder_of_project(path):
                is_project = False
            else:
                is_php = False
                if "composer.json" in files_in_dir:
                    is_php = True
                else:
                    # Check for substantial PHP files to avoid false positives
                    php_files = [f for f in files_in_dir if f.endswith(".php")]
                    folder_name = os.path.basename(path).lower()
                    
                    # WordPress Plugin pattern: folder/folder.php or folder/folder-plugin.php
                    # Also check for cleaned names (removing -master suffix)
                    clean_name = folder_name.replace("-master", "").replace("-main", "")
                    
                    if f"{folder_name}.php" in php_files or f"{clean_name}.php" in php_files:
                        is_php = True
                    # Standard web entry point
                    elif "index.php" in php_files:
                         is_php = True
                    # Project likely has a src folder and some php files
                    elif os.path.exists(os.path.join(path, "src")) and os.path.isdir(os.path.join(path, "src")):
                         is_php = True
                    # Multiple PHP files likely mean a project (but careful with this if it's a subfolder)
                    elif len(php_files) > 1:
                         is_php = True
                
                if is_php:
                    is_project = True
                    project_type = "PHP"
        elif any(f in ["CMakeLists.txt"] for f in files_in_dir):
            is_project = True
            project_type = "C/C++"
        elif any(f.endswith(".vcxproj") for f in files_in_dir):
            is_project = True
            project_type = "C++"
        elif "index.html" in files_in_dir:
            # Check if this is web folder in Flutter project
            if self.is_subfolder_of_project(path):
                is_project = False  # Skip as it's part of Flutter project
            # Check if it's a vendor/library folder or lacks substantial files
            elif self.is_vendor_or_library_folder(path, os.path.basename(path)):
                is_project = False
            elif not self.has_substantial_project_files(path, files_in_dir, "Web/HTML"):
                is_project = False
            else:
                is_project = True
                project_type = "Web/HTML"
        elif "manage.py" in files_in_dir:
            is_project = True
            project_type = "Django"
        elif any(f in ["mix.exs"] for f in files_in_dir):
            is_project = True
            project_type = "Elixir"
        elif any(f in ["build.sbt"] for f in files_in_dir):
            is_project = True
            project_type = "Scala"
        elif any(f in ["dub.json", "dub.sdl"] for f in files_in_dir):
            is_project = True
            project_type = "D"
        elif has_git: # If none of above but has git, it's a project
            is_project = True
            project_type = "Git Repo"

        if is_project:
            git_status = ""
            if has_git:
                git_status = self.check_git_status(path)
            
            created_date, modified_date = self.get_directory_dates(path)
            self.add_project(os.path.basename(path) or path, path, project_type, "Yes" if has_git else "No", git_status, created_date, modified_date)
            # Exclude subfolders ONLY if project has active git AND no subfolder has git
            if has_git:
                has_subfolder_with_git = any(os.path.isdir(os.path.join(d.path, ".git")) for d in dirs_in_dir)
                if not has_subfolder_with_git:
                    # Exclude all subfolders - don't scan them
                    dirs_in_dir = []

        for d in dirs_in_dir:
            if self.stop_requested: break
            self.scan_directory(d.path, excluded_folders, depth=depth+1)

    def add_project(self, name, path, p_type, git, status, created, modified):
        if path in self.found_paths:
            return
        self.found_paths.add(path)
        self.projects_added_count += 1
        
        tags = []
        if git == "Yes":
            tags.append("git_yes")
        if status == "Dirty":
            tags.append("dirty")
        
        # Capture values in closure to avoid late binding
        values_tuple = (name, path, p_type, git, status, created, modified)
        tags_tuple = tuple(tags)
        
        # Inserting at index 0 if it's git, otherwise at the end
        def insert_item():
            try:
                if git == "Yes":
                    self.tree.insert("", 0, values=values_tuple, tags=tags_tuple)
                else:
                    self.tree.insert("", tk.END, values=values_tuple, tags=tags_tuple)
            except:
                pass
        
        self.root.after_idle(insert_item)
        
        # Force GUI update every 5 projects to show progress
        if self.projects_added_count % 5 == 0:
            try:
                self.root.update_idletasks()
            except:
                pass

    def sort_by_column(self, col):
        """Sort treeview by column when header is clicked"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        
        # Toggle sort direction
        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse
        
        # Special handling for date columns and numeric columns
        if col in ["created", "modified"]:
            # Parse dates for proper sorting
            def parse_date(item_tuple):
                date_str, item = item_tuple
                try:
                    if date_str == "Unknown":
                        return (datetime.min, item)
                    return (datetime.strptime(date_str, "%Y-%m-%d %H:%M"), item)
                except:
                    return (datetime.min, item)
            items.sort(key=parse_date, reverse=reverse)
        else:
            # Normal string sorting
            items.sort(key=lambda x: x[0].lower() if x[0] else "", reverse=reverse)
        
        # Rearrange items in treeview
        for index, (val, item) in enumerate(items):
            self.tree.move(item, "", index)
        
        # Update column heading to show sort direction
        if reverse:
            self.tree.heading(col, text=self.tree.heading(col, "text").rstrip(" ▲▼") + " ▼")
        else:
            self.tree.heading(col, text=self.tree.heading(col, "text").rstrip(" ▲▼") + " ▲")

    def update_status(self, text):
        # Use after_idle to ensure GUI updates happen when idle, preventing queue buildup
        # Capture text in lambda closure to avoid late binding issues
        def update_label():
            try:
                self.status_label.config(text=text)
                self.root.update_idletasks()
            except:
                pass
        self.root.after_idle(update_label)

    def open_in_explorer(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a project first.")
            return
        
        project_path = self.tree.item(selected_item[0])['values'][1]
        if os.path.exists(project_path):
            os.startfile(project_path)
        else:
            messagebox.showerror("Error", f"Path not found: {project_path}")

    def open_with_antigravity(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a project first.")
            return
            
        project_path = self.tree.item(selected_item[0])['values'][1]
        
        # Don't check for existence strictly, the tool might handle it or it might be remote/container based
        # But safest is to check exists locally first for this use case
        if not os.path.exists(project_path):
             messagebox.showerror("Error", f"Path not found: {project_path}")
             return

        try:
            # Use Popen to launch and not block
            # Only support Windows per user OS
            subprocess.Popen(f'antigravity "{project_path}"', shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Antigravity:\n{str(e)}")

    def export_to_csv(self):
        """Export all projects from treeview to CSV file"""
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Warning", "No projects to export. Please run a scan first.")
            return
        
        # Ask user for file location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )
        
        if not filename:
            return  # User cancelled
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(["Project Name", "Directory Path", "Type", "Git", "Git Status", "Created", "Modified"])
                
                # Write all items from treeview
                for item_id in items:
                    values = self.tree.item(item_id)['values']
                    writer.writerow(values)
            
            messagebox.showinfo("Success", f"Projects exported successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV file:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectScoutApp(root)
    root.mainloop()

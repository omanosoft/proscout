import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
from pathlib import Path

class ProjectScoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Scout - Find Your Projects")
        self.root.geometry("1000x600")

        self.projects = []
        self.scanning = False
        self.stop_requested = False

        self.found_paths = set()
        self.setup_ui()

    def setup_ui(self):
        # Top Controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(control_frame, text="Click 'Start Scan' to begin searching...")
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.scan_btn = ttk.Button(control_frame, text="Start Scan", command=self.toggle_scan)
        self.scan_btn.pack(side=tk.RIGHT, padx=5)

        # Treeview for Projects
        columns = ("name", "path", "type", "git", "status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("name", text="Project Name")
        self.tree.heading("path", text="Directory Path")
        self.tree.heading("type", text="Type")
        self.tree.heading("git", text="Git")
        self.tree.heading("status", text="Git Status")

        self.tree.column("name", width=120)
        self.tree.column("path", width=400)
        self.tree.column("type", width=100)
        self.tree.column("git", width=50)
        self.tree.column("status", width=80)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom Buttons
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)

        ttk.Button(bottom_frame, text="Open in Explorer", command=self.open_in_explorer).pack(side=tk.LEFT, padx=5)
        
        # Color tags
        self.tree.tag_configure("git_yes", background="#e1f5fe") # Light blue for git projects
        self.tree.tag_configure("dirty", foreground="#d32f2f")   # Red text for uncommitted changes

    def toggle_scan(self):
        if self.scanning:
            self.stop_requested = True
            self.status_label.config(text="Stopping scan...")
        else:
            self.start_scan()

    def start_scan(self):
        self.projects = []
        self.found_paths = set()
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.scanning = True
        self.stop_requested = False
        self.scan_btn.config(text="Stop Scan")
        
        # Start scanning in a background thread
        thread = threading.Thread(target=self.run_scanner, daemon=True)
        thread.start()

    def run_scanner(self):
        # Search priorities: Home, then C:, then D:, then others
        home = str(Path.home())
        drives = sorted(self.get_available_drives())
        
        search_paths = [home]
        # Add C: if it's not already covered by home (unlikely but for completeness)
        # Usually we want to scan the whole C: excluding home if home was already scanned?
        # Actually, simpler: just scan C: and D: after Home, and skip home-subfolders in C: scan.
        
        for d in drives:
            if d not in search_paths:
                search_paths.append(d)

        # Move C: to second position if it's there
        if "C:\\" in search_paths:
            search_paths.remove("C:\\")
            search_paths.insert(1, "C:\\")
        
        # Move D: to third position if it's there
        if "D:\\" in search_paths:
            search_paths.remove("D:\\")
            if len(search_paths) > 2:
                search_paths.insert(2, "D:\\")
            else:
                search_paths.append("D:\\")

        excluded_folders = {
            "windows", "program files", "program files (x86)", 
            "programdata", "recovery", "system volume information",
            "node_modules", "venv", ".venv", "__pycache__", ".git",
            "appdata", "local", "roaming", "microsoft", "cache"
            , "pictures", "music", "videos", "desktop", "links", ".cursor",
            "favorites", "contacts", "searches", "saved games", "objects"
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
            self.scan_directory(base_path, excluded_folders)

        self.scanning = False
        self.root.after(0, lambda: self.scan_btn.config(text="Start Scan"))
        self.update_status("Scan complete.")

    def get_available_drives(self):
        import string
        from ctypes import windll
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                path = f"{letter}:\\"
                if os.path.exists(path):
                    drives.append(path)
            bitmask >>= 1
        return drives

    def check_git_status(self, path):
        try:
            # git status --porcelain returns empty if clean, and lists files if dirty
            # We use --ignore-submodules=dirty to be faster
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path,
                capture_output=True,
                text=True,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode != 0:
                return "Unknown"
            
            return "Dirty" if result.stdout.strip() else "Clean"
        except Exception:
            return "Error"

    def scan_directory(self, path, excluded_folders):
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
                    else:
                        dirs_in_dir.append(entry)
            except (PermissionError, OSError):
                continue

        # Identification Logic
        if "package.json" in files_in_dir:
            is_project = True
            project_type = "Node.js"
        elif "pubspec.yaml" in files_in_dir:
            is_project = True
            project_type = "Flutter"
        elif any(f.endswith(".sln") or f.endswith(".csproj") for f in files_in_dir):
            is_project = True
            project_type = "C# / .NET"
        elif any(f in ["requirements.txt", "pyproject.toml", "setup.py", "pipfile"] for f in files_in_dir):
            is_project = True
            project_type = "Python"
        elif any(f.endswith(".py") for f in files_in_dir) and len([f for f in files_in_dir if f.endswith(".py")]) > 1:
            is_project = True
            project_type = "Python Script"
        elif "build.gradle" in files_in_dir:
            is_project = True
            project_type = "Android/Java"
        elif any(f.endswith(".xcodeproj") or f.endswith(".xcworkspace") for f in files_in_dir) or any(d.name.endswith(".xcodeproj") for d in dirs_in_dir):
            is_project = True
            project_type = "iOS"
        elif "index.html" in files_in_dir:
            is_project = True
            project_type = "Web/HTML"
        elif "manage.py" in files_in_dir:
            is_project = True
            project_type = "Django"
        elif has_git: # If none of above but has git, it's a project
            is_project = True
            project_type = "Git Repo"

        if is_project:
            git_status = ""
            if has_git:
                git_status = self.check_git_status(path)
            
            self.add_project(os.path.basename(path) or path, path, project_type, "Yes" if has_git else "No", git_status)
            # If we found a project, only scan subdirectories if they contain their own .git folder
            # (as requested: skip subfolders of a project unless they have their own git)
            dirs_in_dir = [d for d in dirs_in_dir if os.path.isdir(os.path.join(d.path, ".git"))]

        for d in dirs_in_dir:
            if self.stop_requested: break
            self.scan_directory(d.path, excluded_folders)

    def add_project(self, name, path, p_type, git, status):
        if path in self.found_paths:
            return
        self.found_paths.add(path)
        
        tags = []
        if git == "Yes":
            tags.append("git_yes")
        if status == "Dirty":
            tags.append("dirty")
            
        # Inserting at index 0 if it's git, otherwise at the end
        if git == "Yes":
            self.root.after(0, lambda: self.tree.insert("", 0, values=(name, path, p_type, git, status), tags=tuple(tags)))
        else:
            self.root.after(0, lambda: self.tree.insert("", tk.END, values=(name, path, p_type, git, status), tags=tuple(tags)))

    def update_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectScoutApp(root)
    root.mainloop()

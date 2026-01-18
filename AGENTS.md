# AGENTS.md - Development Guidelines for Project Scout

This document describes the architecture, code structure, and best practices for developing and maintaining the Project Scout application.

## 📁 Project Structure

```
proscout/
├── project_scout.py    # Main application (GUI + scanning)
├── README.md           # User documentation
└── AGENTS.md           # This file - development guidelines
```

## 🏗️ Architecture

### Main Class: `ProjectScoutApp`

The application is built around a single main class that uses:

- **tkinter** for GUI interface
- **threading** for asynchronous scanning (doesn't block GUI)
- **subprocess** for git status checks
- **pathlib** for path handling
- **ctypes** for Windows API calls (GetDriveType, GetLogicalDrives)

### Key Components

1. **GUI Setup** (`setup_ui`)
   - Treeview for displaying projects
   - Status label for progress
   - Control buttons

2. **Scanner Thread** (`run_scanner`)
   - Runs in a background thread
   - Scans drives in priority order
   - Uses `scan_directory` for recursive scanning

3. **Project Detection** (`scan_directory`)
   - Identifies project type based on files
   - Checks git status
   - Filters subfolders of larger projects

4. **GUI Updates** (`update_status`, `add_project`)
   - Thread-safe GUI updates using `root.after_idle()`
   - Batch refresh every 5 projects

## 🔧 Key Functions

### `get_available_drives()`
- Returns list of local drives
- **IMPORTANT**: Checks `GetDriveTypeW` BEFORE `os.path.exists()` to avoid timeout on network drives
- Returns only `DRIVE_FIXED` (3) - local drives

### `scan_directory(path, excluded_folders, depth=0)`
- Recursive function for scanning folders
- Detects projects based on characteristic files
- `depth` parameter is used for throttling status updates
- Skips excluded folders and project subfolders (Flutter, React Native)

### `is_subfolder_of_project(path)`
- Checks if folder is part of a larger project (e.g., android/ in Flutter project)
- Prevents project duplication (doesn't show android/ as a separate project)

### `check_git_status(path)`
- Checks project git status
- **IMPORTANT**: Has 2 second timeout to not block scanning
- Returns: Clean, Dirty, Unknown, Timeout, Error

### `add_project(name, path, type, git, status, created, modified)`
- Adds project to treeview
- Uses `after_idle()` for thread-safe GUI update
- Refreshes GUI every 5 projects (`update_idletasks()`)

## 🎯 Project Identification

### Check Priority

Projects are identified in a specific order:

1. **package.json** projects:
   - Vite, Vue, Angular, Next.js, Svelte, React, Node.js

2. **pubspec.yaml** - Flutter

3. **.sln / .csproj** - C# / .NET

4. **Python** projects:
   - requirements.txt, pyproject.toml, setup.py, pipfile, poetry.lock
   - Or multiple .py files

5. **Android/Java/Kotlin** - build.gradle / build.gradle.kts

6. **Maven** - pom.xml

7. **iOS** - .xcodeproj / .xcworkspace

8. **Go** - go.mod / go.sum

9. **Rust** - Cargo.toml

10. **Others** - Ruby, PHP, C/C++, Elixir, Scala, D

11. **Git Repo** - If it has .git folder

### React Detection

React projects are detected by reading `package.json` and checking content for "react" or "react-scripts". Also checks for existence of `src/`, `public/`, `tsconfig.json`, or `jsconfig.json` folders.

## 🚫 Excluded Folders

### Automatically excluded:

```python
excluded_folders = {
    "windows", "program files", "program files (x86)", 
    "programdata", "recovery", "system volume information",
    "node_modules", "venv", ".venv", "__pycache__", ".git",
    "appdata", "local", "roaming", "microsoft", "cache",
    "pictures", "music", "videos", "desktop", "links", ".cursor",
    "favorites", "contacts", "searches", "saved games", "objects",
    "$recycle.bin", "recycle.bin", "exception", "user data"
}
```

### Portable browsers:

Detected by name containing "portable" + browser name (firefox, chrome, opera, edge, brave, vivaldi, etc.)

## ⚡ Optimizations

### Performance

1. **Drive Type Check First**
   - Checks `GetDriveTypeW` BEFORE `os.path.exists()`
   - Prevents timeout on network drives

2. **Git Status Timeout**
   - 2 seconds timeout for git status check
   - Doesn't block scanning

3. **Status Update Throttling**
   - Depth 0-2: every folder
   - Depth 3: every 5th folder
   - Depth 4: every 10th folder
   - Depth 5+: every 20th folder

4. **GUI Refresh Throttling**
   - Refreshes GUI every 5 projects
   - Uses `update_idletasks()` instead of `update()`

5. **Subfolder Exclusion**
   - If project has git and no git projects in subfolders, skips subfolders
   - Flutter subfolders are automatically filtered

### Thread Safety

- All GUI updates use `root.after_idle()` or `root.after(0, ...)`
- `update_idletasks()` is called periodically during scanning
- Background thread uses `self.stop_requested` flag for graceful shutdown

## 🐛 Debugging Tips

### Logging

Currently no logging system. For debugging you can add:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Status Update Issues

If status doesn't display:
- Check if `update_status()` calls `update_idletasks()`
- Check throttling logic in `scan_directory()`

### Slow Scanning

If scanning is slow:
- Check if `os.path.exists()` is called on network drives
- Check git timeout (should be 2 seconds)
- Check excluded folders list

### Missing Projects

If projects are not found:
- Check identification logic in `scan_directory()`
- Check `is_subfolder_of_project()` - might filter too much
- Check excluded folders

## 🔄 Adding New Project Types

To add a new project type:

1. Find a characteristic file/folder
2. Add check in `scan_directory()` in `# Identification Logic` section
3. Add before general checks (package.json, pubspec.yaml, etc.)
4. Add to `AGENTS.md` documentation

Example:

```python
elif "newproject.json" in files_in_dir:
    is_project = True
    project_type = "New Project Type"
```

## 📊 CSV Export Format

CSV file contains columns:
- Project Name
- Directory Path
- Type
- Git (Yes/No)
- Git Status (Clean/Dirty/Unknown/Timeout/Error)
- Created (YYYY-MM-DD HH:MM)
- Modified (YYYY-MM-DD HH:MM)

## 🎨 GUI Customization

### Colors

- `git_yes`: `#e1f5fe` (light blue background)
- `dirty`: `#d32f2f` (red text)

Changing colors in `setup_ui()`:

```python
self.tree.tag_configure("git_yes", background="#e1f5fe")
self.tree.tag_configure("dirty", foreground="#d32f2f")
```

### Columns

Columns are defined in `setup_ui()`:

```python
columns = ("name", "path", "type", "git", "status", "created", "modified")
```

## 🧪 Testing

Currently no unit tests. For testing:

1. Run the application
2. Test with a small folder first
3. Check sorting
4. Check CSV export
5. Check git status check

## 📝 TODO / Future Improvements

- [ ] Add logging system
- [ ] Add unit tests
- [ ] Add configuration file (config.json) for excluded folders
- [ ] Add filter/search functionality
- [ ] Add favorites/bookmarks
- [ ] Add dark mode
- [ ] Add JSON format export
- [ ] Add option for custom scan paths

## 🔐 Security

- Application doesn't send data outside local system
- Uses only local drives (skips network drives)
- Doesn't read file contents except package.json for React detection
- Git status checks are read-only

## 📚 References

- [tkinter documentation](https://docs.python.org/3/library/tkinter.html)
- [Windows API - GetDriveType](https://docs.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdrivetypew)
- [pathlib documentation](https://docs.python.org/3/library/pathlib.html)

---

**Note**: This document should be updated when new features are added or existing ones are changed.

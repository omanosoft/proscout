# Project Scout

**Project Scout** is a Windows desktop application that automatically scans your system and finds all your development projects. The application recognizes different project types and displays them in a unified interface with detailed information about git status, creation date, and modification date.

## ✨ Features

- 🔍 **Automatic Scanning** - Finds all projects on your drives
- 🎯 **Project Type Recognition** - Detects over 20 different project types
- 📊 **Git Integration** - Shows git status (Clean/Dirty) for each project
- 📅 **Date Sorting** - Sort by creation or modification date
- 💾 **CSV Export** - Export project list to CSV format
- 🚀 **Optimized Scanning** - Fast and efficient, skips network drives and system folders
- 🎨 **Intuitive GUI** - Simple and modern user interface

## 🎯 Supported Project Types

The application recognizes the following project types:

- **Node.js / JavaScript** - package.json
- **React** - React projects
- **Vue.js** - Vue.js projects
- **Angular** - Angular projects
- **Next.js** - Next.js projects
- **Vite** - Vite projects
- **Svelte** - Svelte projects
- **Flutter** - Flutter projects (pubspec.yaml)
- **Python** - Python projects (requirements.txt, pyproject.toml, setup.py, pipfile, poetry.lock)
- **Django** - Django projects
- **C# / .NET** - Visual Studio projects (.sln, .csproj, .vbproj)
- **Android/Java/Kotlin** - Android projects (build.gradle, build.gradle.kts)
- **Java/Maven** - Maven projects (pom.xml)
- **iOS** - iOS projects (.xcodeproj, .xcworkspace)
- **Go** - Go projects (go.mod, go.sum)
- **Rust** - Rust projects (Cargo.toml)
- **Ruby** - Ruby projects (Gemfile)
- **PHP** - PHP projects (composer.json)
- **C/C++** - C/C++ projects (CMakeLists.txt, .vcxproj)
- **Elixir** - Elixir projects (mix.exs)
- **Scala** - Scala projects (build.sbt)
- **D** - D projects (dub.json, dub.sdl)
- **Git Repo** - Projects with .git folder

## 📋 Requirements

- **OS**: Windows 10/11
- **Python**: 3.7 or newer
- **Libraries**: 
  - tkinter (usually comes with Python)
  - ctypes (built-in)
  - pathlib (built-in)
  - csv (built-in)
  - datetime (built-in)
  - subprocess (built-in)
  - threading (built-in)

## 🚀 Installation

1. Clone or download this repository
2. Make sure you have Python 3.7+ installed
3. Run the application:

```bash
python project_scout.py
```

## 📖 Usage

### Starting a Scan

1. Run the application
2. Click the **"Start Scan"** button
3. The application will automatically scan:
   - First the current user's folder
   - Then the D: drive
   - Then other local drives
   - Finally the C: drive

### Viewing Results

The project list displays the following information:
- **Project Name** - Project name
- **Directory Path** - Full path to the project
- **Type** - Project type
- **Git** - Whether the project uses git (Yes/No)
- **Git Status** - Git repository status (Clean/Dirty/Unknown)
- **Created** - Folder creation date
- **Modified** - Last modification date

### Sorting

Click on any column header to sort the list. Click again to change sort direction (ascending/descending).

### Opening a Project

1. Select a project from the list
2. Click the **"Open in Explorer"** button
3. The project will open in Windows Explorer

### Export to CSV

1. After scanning is complete
2. Click the **"Export to CSV"** button
3. Choose the location where you want to save the CSV file
4. The CSV file will contain all columns from the display

### Stopping a Scan

Click the **"Stop Scan"** button during scanning to abort.

## 🎨 Colors and Tags

- **Light blue background** - Projects with git repository
- **Red text** - Projects with uncommitted changes (Dirty)

## ⚙️ Optimizations

The application is optimized for fast scanning:

- **Skips network drives** - Automatically detects and skips network drives
- **Skips system folders** - Windows, Program Files, etc.
- **Skips build folders** - node_modules, venv, .git, etc.
- **Skips portable browsers** - Firefox Portable, Chrome Portable, etc.
- **Flutter subfolder filtering** - Doesn't display android/, ios/, web/ folders as separate projects
- **Git timeout** - Git status check has 2 seconds timeout to not block scanning

## 🛠️ Technical Details

### Scanning Order

1. Home folder (current user)
2. D: drive
3. Other local drives (E:, F:, etc.)
4. C: drive (last to avoid system folders)

### Excluded Folders

The application automatically skips the following folders:
- System folders: `windows`, `program files`, `programdata`, `recovery`
- Build folders: `node_modules`, `venv`, `.venv`, `__pycache__`, `.git`
- User folders: `appdata`, `cache`, `pictures`, `music`, `videos`, `desktop`
- Other: `$recycle.bin`, `recycle.bin`, `exception`, `user data`

### Git Status Check

- Projects with git repository automatically have git status check
- 2 seconds timeout to avoid blocking
- Displays: Clean, Dirty, Unknown, Timeout, or Error

## 📝 Notes

- The application scans only **local drives** - network drives are automatically skipped
- Projects with git repository are displayed at the top of the list
- Flutter subfolders (android/, ios/, web/, etc.) are not displayed as separate projects
- If a project has git and no git projects in subfolders, subfolders are not scanned (optimization)

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

## 📄 License

This project is available under the MIT license.

## 👨‍💻 Author

The project was developed for quickly finding and managing development projects.

---

**Made with ❤️ for developers**

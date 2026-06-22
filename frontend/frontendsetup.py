import os
from pathlib import Path

def create_project_structure():
    # Define the root src directory relative to where the script runs
    src_dir = Path("src")

    # 1. Define the subdirectories to create
    subdirectories = [
        src_dir / "components",
        src_dir / "services"
    ]

    # 2. Define all the files to create
    files_to_create = [
        # Files inside src/components/
        src_dir / "components/ExportButton.tsx",      src_dir / "components/ExportButton.css",
        src_dir / "components/InfoModal.tsx",         src_dir / "components/InfoModal.css",
        src_dir / "components/InstabilityPanel.tsx",   src_dir / "components/InstabilityPanel.css",
        src_dir / "components/LearnPage.tsx",          src_dir / "components/LearnPage.css",
        src_dir / "components/LocationSelector.tsx",   src_dir / "components/LocationSelector.css",
        src_dir / "components/RefreshTimer.tsx",       src_dir / "components/RefreshTimer.css",
        src_dir / "components/RemoteWeatherCard.tsx",  src_dir / "components/RemoteWeatherCard.css",
        src_dir / "components/StatisticsPanel.tsx",    src_dir / "components/StatisticsPanel.css",
        src_dir / "components/StatusBadge.tsx",        src_dir / "components/StatusBadge.css",
        src_dir / "components/ThemeToggle.tsx",        src_dir / "components/ThemeToggle.css",
        
        # Files inside src/services/
        src_dir / "services/api.ts",
        
        # Files directly in src/
        src_dir / "App.tsx",
        src_dir / "Dashboard.tsx",
        src_dir / "Header.tsx",
        src_dir / "Header.css",
        src_dir / "index.css"
    ]

    print("📁 Creating folders...")
    for folder in subdirectories:
        # mkdir(parents=True, exist_ok=True) safely handles existing folders
        folder.mkdir(parents=True, exist_ok=True)
        print(skinny_log := f"  Created/Verified: {folder}")

    print("\n📄 Creating files...")
    for file_path in files_to_create:
        # touch(exist_ok=True) creates the file if it doesn't exist, without wiping content if it does
        file_path.touch(exist_ok=True)
        print(f"  Created/Verified: {file_path}")

    print("\n✅ Structure generation complete!")

if __name__ == "__main__":
    create_project_structure()
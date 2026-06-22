import os
from pathlib import Path

# Define the folder and file structure
# Keys are directory paths, values are lists of files within them
structure = {
    "backend": [
        "main.py",
        "requirements.txt",
        "config.py"
    ],
    "backend/models": ["atmospheric.py"],
    "backend/routes": ["__init__.py", "sensor_data.py", "dashboard.py"],
    "backend/services": ["__init__.py", "data_processor.py", "data_store.py"],
    "backend/utils": ["__init__.py", "validators.py"],
    "backend/data": ["readings.json"]
}

def create_structure(base_path, structure_map):
    for folder, files in structure_map.items():
        # Create the directory (and any necessary parent directories)
        folder_path = Path(base_path) / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        for file_name in files:
            # Create an empty file
            file_path = folder_path / file_name
            file_path.touch(exist_ok=True)
            print(f"Created: {file_path}")

if __name__ == "__main__":
    # '.' represents the current working directory
    create_structure(".", structure)
    print("\nProject structure created successfully!")

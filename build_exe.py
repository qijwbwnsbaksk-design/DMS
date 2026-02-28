"""
Build script for creating the Windows executable.

Run this script from the dental_app directory:
    python build_exe.py

Or use PyInstaller directly:
    pyinstaller --name "DentalClinic" --windowed --onefile --add-data "password.txt;." main.py

The executable will be created in the 'dist' folder.
"""

import subprocess
import sys
import os

def build():
    # Ensure we're in the dental_app directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "DentalClinic",
        "--windowed",  # No console window
        "--onefile",   # Single EXE file
        "--add-data", f"password.txt{os.pathsep}.",  # Include password.txt
        "main.py"
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("="*50)
        print(f"\nThe executable is located at:")
        print(f"  {os.path.join(script_dir, 'dist', 'DentalClinic.exe')}")
        print("\nIMPORTANT NOTES:")
        print("1. Copy DentalClinic.exe to any folder on your Windows PC")
        print("2. Double-click to run - no installation needed")
        print("3. The SQLite database (dental_clinic.db) will be created")
        print("   automatically in the same folder as the EXE")
        print("4. A password.txt file with default password 'admin' is bundled")
        print("   but a new one will be created next to the EXE if needed")
    else:
        print("\nBuild failed. Check the errors above.")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(build())

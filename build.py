import os
import sys
import shutil
import subprocess

def install_pyinstaller():
    print("Checking for PyInstaller...")
    try:
        # Check if PyInstaller can be run
        subprocess.run(["pyinstaller", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        print("PyInstaller is already installed and accessible.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Installing via pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing PyInstaller: {e}")
            sys.exit(1)

def build_exe(script_name):
    print(f"\nBuilding {script_name} to standalone EXE...")
    if not os.path.exists(script_name):
        print(f"Error: {script_name} does not exist in the current directory.")
        return False
        
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        script_name
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully compiled {script_name} to EXE.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {script_name}: {e}")
        return False
    except FileNotFoundError:
        print("Error: PyInstaller command not found in system PATH.")
        return False

def clean_temp_files(script_name):
    base_name = os.path.splitext(script_name)[0]
    spec_file = f"{base_name}.spec"
    
    # Remove spec file
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"Removed temporary file: {spec_file}")
        except Exception as e:
            print(f"Warning: Could not remove spec file {spec_file}: {e}")
            
    # Remove build folder
    build_dir = os.path.join(os.getcwd(), "build")
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            print("Removed temporary folder: build/")
        except Exception as e:
            print(f"Warning: Could not remove build folder: {e}")

if __name__ == "__main__":
    # Ensure working directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    install_pyinstaller()
    
    targets = ["chrome_profiles.py", "windows_management.py"]
    success_count = 0
    
    for target in targets:
        if build_exe(target):
            success_count += 1
            clean_temp_files(target)
            
    print("\n" + "="*45)
    if success_count == len(targets):
        print(f"Build complete. All {success_count} executables are in the dist/ folder.")
    else:
        print(f"Build finished. {success_count}/{len(targets)} targets built successfully.")
    print("="*45)

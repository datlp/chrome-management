import os
import sys
import re
import subprocess

VERSION_FILE = "version.txt"
FILES_TO_UPDATE = ["chrome_profiles.py", "windows_management.py"]
README_FILE = "Readme.md"

def get_current_version():
    if not os.path.exists(VERSION_FILE):
        print(f"Error: {VERSION_FILE} not found. Creating default '1.2.0'.")
        with open(VERSION_FILE, "w") as f:
            f.write("1.2.0")
        return "1.2.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def bump_version(current, bump_type):
    parts = current.split(".")
    # Ensure version follows semantic versioning X.Y.Z
    if len(parts) < 3:
        parts = [parts[0], "0", "0"]
    
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        print("Non-semantic version detected. Defaulting to patch bump.")
        return current + ".1"

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        # Assume custom version string
        return bump_type

def update_code_files(old_ver, new_ver):
    for filename in FILES_TO_UPDATE:
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found, skipping.")
            continue
            
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Match pattern __version__ = "X.Y.Z"
        pattern = rf'__version__\s*=\s*"{re.escape(old_ver)}"'
        replacement = f'__version__ = "{new_ver}"'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated __version__ in {filename} to {new_ver}")
        else:
            # Fallback check if __version__ is defined differently
            pattern_any = r'__version__\s*=\s*"[^"]+"'
            if re.search(pattern_any, content):
                new_content = re.sub(pattern_any, replacement, content)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated existing __version__ in {filename} to {new_ver}")
            else:
                print(f"Warning: Could not find __version__ variable in {filename}")

def update_readme(old_ver, new_ver):
    if not os.path.exists(README_FILE):
        return
        
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Replace version strings in headers and commands
    replacements = [
        (f"Phiên bản v{old_ver}", f"Phiên bản v{new_ver}"),
        (f"Release v{old_ver}", f"Release v{new_ver}"),
        (f"create v{old_ver}", f"create v{new_ver}"),
        (f"upload v{old_ver}", f"upload v{new_ver}"),
        (f"tag v{old_ver}", f"tag v{new_ver}")
    ]
    
    updated = False
    for old_str, new_str in replacements:
        if old_str in content:
            content = content.replace(old_str, new_str)
            updated = True
            
    if updated:
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated version references in {README_FILE} to {new_ver}")
    else:
        # Fallback to general replace if needed
        pass

def git_commit_and_tag(new_ver):
    print("\nRunning Git commands...")
    try:
        # Git Add
        subprocess.run(["git", "add", VERSION_FILE, README_FILE] + FILES_TO_UPDATE, check=True)
        # Git Commit
        subprocess.run(["git", "commit", "-m", f"Bump version to v{new_ver}"], check=True)
        # Git Tag
        subprocess.run(["git", "tag", f"v{new_ver}"], check=True)
        print(f"Git commit and tag v{new_ver} created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
        return False

if __name__ == "__main__":
    # Ensure working directory is the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    current_version = get_current_version()
    print(f"Current Version: {current_version}")
    
    bump_type = "patch"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["major", "minor", "patch"]:
            bump_type = arg
        else:
            bump_type = sys.argv[1] # Custom version string
    else:
        print("\nChoose bump type:")
        print("1. Patch (x.y.z+1)")
        print("2. Minor (x.y+1.0)")
        print("3. Major (x+1.0.0)")
        print("4. Custom version string")
        choice = input("Enter selection (1-4, default 1): ").strip()
        if choice == "2":
            bump_type = "minor"
        elif choice == "3":
            bump_type = "major"
        elif choice == "4":
            bump_type = input("Enter custom version string: ").strip()
            
    new_version = bump_version(current_version, bump_type)
    print(f"Bumping version from {current_version} to {new_version}...")
    
    # 1. Update version.txt
    with open(VERSION_FILE, "w") as f:
        f.write(new_version)
        
    # 2. Update source code files
    update_code_files(current_version, new_version)
    
    # 3. Update Readme.md
    update_readme(current_version, new_version)
    
    # 4. Git Automation
    git_success = git_commit_and_tag(new_version)
    
    print("\n" + "="*50)
    print(f"Version bump to v{new_version} completed successfully.")
    print("="*50)
    print("To push to GitHub:")
    print(f"  git push origin main --tags")
    print("\nTo build compiled binaries:")
    print("  python build.py")
    print("="*50)

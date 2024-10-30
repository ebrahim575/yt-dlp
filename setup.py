import os
import subprocess
import sys
import venv
import platform

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e}")
        sys.exit(1)

def main():
    print("Setting up YouTube Downloader...")

    # Detect OS
    is_windows = platform.system() == "Windows"
    is_mac = platform.system() == "Darwin"

    if not (is_windows or is_mac):
        print("This application only supports Windows and macOS")
        sys.exit(1)

    # Create virtual environment
    venv.create("venv", with_pip=True)

    # Determine the path to the virtual environment's Python executable
    if is_windows:
        venv_python = os.path.join("venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join("venv", "bin", "python")

    # Upgrade pip
    run_command(f"{venv_python} -m pip install --upgrade pip")

    # Install required packages
    run_command(f"{venv_python} -m pip install yt-dlp ffmpeg-python")
    
    # Install OS-specific packages
    if is_windows:
        run_command(f"{venv_python} -m pip install pywin32")
    else:
        run_command(f"{venv_python} -m pip install pyobjc-framework-Cocoa")

    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    if is_windows:
        print("1. Activate the virtual environment: venv\\Scripts\\activate")
        print("2. Run the application: python yt-dlp-gui-windows.py")
    else:
        print("1. Activate the virtual environment: source venv/bin/activate")
        print("2. Run the application: python yt-dlp-gui-mac.py")

if __name__ == "__main__":
    main()
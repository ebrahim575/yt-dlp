import subprocess
import sys
import platform

def update_dependencies():
    try:
        # Determine OS and pip command
        is_windows = platform.system() == 'Windows'
        pip_cmd = 'pip' if is_windows else 'pip3'
        
        # Update yt-dlp
        print("Updating yt-dlp...")
        subprocess.check_call([pip_cmd, "install", "--upgrade", "yt-dlp"])
        
        # Update ffmpeg if needed
        print("Updating ffmpeg-python...")
        subprocess.check_call([pip_cmd, "install", "--upgrade", "ffmpeg-python"])
        
        # Install OS-specific dependencies
        if is_windows:
            print("Installing Windows-specific dependencies...")
            subprocess.check_call([pip_cmd, "install", "--upgrade", "pywin32"])
        else:
            print("Installing macOS-specific dependencies...")
            subprocess.check_call([pip_cmd, "install", "--upgrade", "pyobjc-framework-Cocoa"])
                
        print("Update completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during update: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
        
    return True

if __name__ == "__main__":
    update_dependencies()
import os
import subprocess
import sys


def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def get_username():
    username = os.environ.get('USER')
    print(f"Current user: {username}")
    return username

def main():
    # Check if Homebrew is installed
    if subprocess.call(["which", "brew"]) != 0:
        print("Homebrew is not installed. Please install Homebrew first.")
        print("Use the following script to install homebrew : '/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\'")
        print('Then run this file again.')
        return

    # Update Homebrew
    print("Updating Homebrew...")
    subprocess.check_call(["brew", "update"])

    # Install Python and pip if not already installed
    print("Installing Python and pip...")
    subprocess.check_call(["brew", "install", "python"])

    # Install ffmpeg
    print("Installing ffmpeg...")
    subprocess.check_call(["brew", "install", "ffmpeg"])

    # Install Python libraries from requirements.txt
    print("Installing Python libraries...")
    install_requirements()

    print("Setup complete!")

if __name__ == "__main__":
    main()

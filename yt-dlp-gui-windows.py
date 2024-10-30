import tkinter as tk
from yt_dlp import YoutubeDL
import re
import os
import subprocess
import platform

# Check if running on Windows
if platform.system() != 'Windows':
    print("This app is only supported on Windows")
    exit(1)

# Global variables
MAX_FILENAME_LENGTH = 200  # Maximum length for filenames

def get_username():
    try:
        # Windows specific username retrieval
        username = os.environ.get('USERNAME')
        if not username:
            home = os.path.expanduser('~')
            username = home.split('\\')[-1]
        return username
    except:
        return None

def sanitize_filename(filename):
    # Windows specific filename sanitization
    return re.sub(r'[<>:"/\\|?*]', "", filename)

def download_video(url, download_options):
    with YoutubeDL(download_options) as ydl:
        ydl.download([url])

def exit_app():
    window.destroy()

def download_done(d):
    if d['status'] == 'finished':
        download_label.config(text="Download complete!")
        # Refresh Windows Explorer
        os.startfile(get_downloads_folder())

def get_downloads_folder():
    username = get_username()
    if not username:
        raise Exception("Could not determine username")
    
    # Windows specific downloads path
    folder_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'youtube-dl')
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_mp3():
    url = url_entry.get()
    download_options = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(get_downloads_folder(), f'%(title).{MAX_FILENAME_LENGTH}s.%(ext)s'),
        'writethumbnail': True,
        'embedthumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        },
        {
            'key': 'EmbedThumbnail',
        }],
        'progress_hooks': [download_done],
        'ignoreerrors': True
    }
    if "x.com" in url:
        url = url.replace('x.com', 'twitter.com')
        download_options['cookiefile'] = 'cookies.txt'

    download_video(url, download_options)

def download_mp4():
    url = url_entry.get()
    download_options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(get_downloads_folder(), f'%(title).{MAX_FILENAME_LENGTH}s.%(ext)s'),
        'progress_hooks': [download_done],
        'embed_thumbnail': True,
    }
    if "x.com" in url:
        url = url.replace('x.com', 'twitter.com')
        download_options['cookiefile'] = 'cookies.txt'

    download_video(url, download_options)

def open_file():
    folder_path = get_downloads_folder()
    if os.path.exists(folder_path):
        # Windows specific file opening
        os.startfile(folder_path)
    else:
        download_label.config(text="Folder not found!")

# Create the main window with Windows styling
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("500x150")

# Windows specific UI adjustments
window.configure(bg='SystemButtonFace')  # Windows default background

# Create the URL label and entry widget
url_label = tk.Label(window, text="Enter the URL:", bg='SystemButtonFace')
url_label.grid(row=0, column=0, padx=5, pady=5)
url_entry = tk.Entry(window, width=40)  # Wider entry field
url_entry.grid(row=0, column=1, padx=5, pady=5)

# Create the download buttons with Windows styling
mp3_button = tk.Button(window, text="YouTube to MP3", command=download_mp3)
mp3_button.grid(row=1, column=0, padx=5, pady=5)

mp4_button = tk.Button(window, text="YouTube to MP4", command=download_mp4)
mp4_button.grid(row=1, column=1, padx=5, pady=5)

# Create the open file button
open_file_button = tk.Button(window, text="Open File", command=open_file)
open_file_button.grid(row=2, column=0, columnspan=2, pady=5)

# Create the exit button
exit_button = tk.Button(window, text="Exit", command=exit_app)
exit_button.grid(row=3, column=0, pady=5)

# Create the download label
download_label = tk.Label(window, text="", bg='SystemButtonFace')
download_label.grid(row=3, column=1, pady=5)

# Center the window on screen
window.update_idletasks()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width - 500) // 2
y = (screen_height - 150) // 2
window.geometry(f"500x150+{x}+{y}")

# Start the GUI
window.mainloop()
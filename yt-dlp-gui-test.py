import tkinter as tk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
import re
import os
import subprocess
import ffmpeg
import sys

# Global variables
MAX_FILENAME_LENGTH = 100  # Maximum length for filenames
download_path = None

def get_icloud_folder():
    username = os.getlogin()
    return f'/Users/{username}/Library/Mobile Documents/com~apple~CloudDocs/youtube-dl'

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename):
    # Remove invalid characters and limit length
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    return sanitized[:MAX_FILENAME_LENGTH].strip()

def download_video(url, download_options):
    try:
        ensure_directory_exists(os.path.dirname(download_options['outtmpl']))
        with YoutubeDL(download_options) as ydl:
            ydl.download([url])
        return True, "Download completed successfully."
    except Exception as e:
        return False, f"Error during download: {str(e)}"

def exit_app():
    window.destroy()

def download_done(d):
    if d['status'] == 'finished':
        download_label.config(text="Download complete!")

def get_filename():
    return '%(title).30s'  # Limit title to 30 characters

def check_and_fix_format(file_path):
    try:
        # Get video and audio codec information
        probe = ffmpeg.probe(file_path)
        video_codec = None
        audio_codec = None

        for stream in probe['streams']:
            if stream['codec_type'] == 'video':
                video_codec = stream['codec_name']
            elif stream['codec_type'] == 'audio':
                audio_codec = stream['codec_name']

        # Check if video is H.264 and audio is AAC
        if video_codec != 'h264' or audio_codec != 'aac':
            output_path = file_path  # Save in the same location
            # Convert the file to H.264 video and AAC audio
            ffmpeg.input(file_path).output(output_path, vcodec='libx264', acodec='aac', movflags='faststart').run(overwrite_output=True)
            return True, "File was re-encoded to H.264 and AAC."
        else:
            return True, "File is already in the correct format."
    except Exception as e:
        return False, f"Error during format check/fix: {str(e)}"

def download_mp4():
    url = url_entry.get()
    filename = get_filename()
    global download_path
    download_path = os.path.join(get_icloud_folder(), f"{filename}.%(ext)s")
    download_options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': download_path,
        'progress_hooks': [download_done],
        'embed_thumbnail': True,
    }

    if "x.com" in url:
        url = url.replace('x.com', 'twitter.com')
        download_options['cookiefile'] = 'cookies.txt'

    success, message = download_video(url, download_options)
    download_label.config(text=message)

    # Check and fix the format of the downloaded video
    final_path = download_path.replace('%(ext)s', 'mp4')  # This is where yt-dlp saves the file
    success, format_message = check_and_fix_format(final_path)
    download_label.config(text=f"{message}\n{format_message}")

def open_file():
    global download_path
    if download_path:
        folder_path = os.path.dirname(download_path)
        if os.path.exists(folder_path):
            subprocess.Popen(f'open "{folder_path}"', shell=True)
        else:
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
    else:
        download_label.config(text="No file downloaded yet.")

# Custom class to redirect console output to Text widget
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)  # Scrolls to the end of the text widget
        self.widget.config(state=tk.DISABLED)

    def flush(self):
        pass

# Create the main window
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("500x320")

# Create the URL label and entry widget
url_label = tk.Label(window, text="Enter the URL:")
url_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
url_entry = tk.Entry(window, width=30)
url_entry.grid(row=0, column=1, sticky='w', padx=5, pady=5)

# Create the download mp4 button
mp4_button = tk.Button(window, text="YouTube to MP4", command=download_mp4)
mp4_button.grid(row=1, column=1, sticky='w', padx=5, pady=5)

# Create the open file button
open_file_button = tk.Button(window, text="Open File", command=open_file)
open_file_button.grid(row=2, column=0, sticky='w', padx=5, pady=5)

# Create the exit button
exit_button = tk.Button(window, text="Exit", command=exit_app)
exit_button.grid(row=3, column=0, sticky='w', padx=5, pady=5)

# Create the download label
download_label = tk.Label(window, text="")
download_label.grid(row=3, column=1, sticky='e', padx=5, pady=5)

# Create a text widget for console output
console_output = tk.Text(window, height=8, width=60, state=tk.DISABLED)
console_output.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

# Redirect console output to the text widget
sys.stdout = TextRedirector(console_output)
sys.stderr = TextRedirector(console_output)

# Start the GUI
window.mainloop()
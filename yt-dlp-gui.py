import tkinter as tk
from yt_dlp import YoutubeDL
from setup import get_username
def download_video(url, download_options):
    with YoutubeDL(download_options) as ydl:
        ydl.download([url])

def exit_app():
    window.destroy()

def download_done(d):
    if d['status'] == 'finished':
        download_label.config(text="Download complete!")

def download_mp3():
    url = url_entry.get()
    download_options = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': '/Users/ezulq/Library/Mobile Documents/com~apple~CloudDocs/youtube-dl/%(title)s.%(ext)s', # Go here to change where your output directory is
        'writethumbnail': True,
        'embedthumbnail': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        },
        {
            'key': 'EmbedThumbnail',
        }
        ],
        'progress_hooks': [download_done],
        'ignoreerrors': True

    }
    download_video(url, download_options)

def download_mp4():
    username = get_username()
    url = url_entry.get()
    download_options = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'/Users/{username}/Library/Mobile Documents/com~apple~CloudDocs/youtube-dl/%(title)s.%(ext)s',
        'progress_hooks': [download_done],
        'embed_thumbnail': True,
    }

    # if "x.com" in url:
    #     download_options['cookiesfrombrowser'] = 'chrome'

    download_video(url, download_options)

# Create the main window
window = tk.Tk()
window.title("YouTube Downloader")
window.geometry("500x120")

# Create the URL label and entry widget
url_label = tk.Label(window, text="Enter the URL:")
url_label.grid(row=0, column=0)
url_entry = tk.Entry(window, width=30)
url_entry.grid(row=0, column=1, sticky='')

# Create the download mp3 button
mp3_button = tk.Button(window, text="YouTube to MP3", command=download_mp3, padx=0, pady=0)
mp3_button.grid(row=1, column=0, sticky='')

# Create the download mp4 button
mp4_button = tk.Button(window, text="YouTube to MP4", command=download_mp4, padx=0, pady=0)
mp4_button.grid(row=1, column=1, sticky='w')

# Create the exit button
exit_button = tk.Button(window, text="Exit", command=exit_app)
exit_button.grid(row=2, column=0, sticky='')

# Create the download label
download_label = tk.Label(window, text="")
download_label.grid(row=2, column=1, sticky='')

# Start the GUI
window.mainloop()

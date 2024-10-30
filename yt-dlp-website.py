from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory
from yt_dlp import YoutubeDL
import os
import re
import platform
import io
import sys
from threading import Lock
from queue import Queue
import datetime
import logging
from creds import PASSWORD

# Feature flags
SHOW_CONSOLE_OUTPUT = True  # Toggle this to enable/disable console output in UI

# Initialize Flask and logging
app = Flask(__name__)
output_buffer = []
output_lock = Lock()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixed console capture
class ConsoleCapture:
    def write(self, message):
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        if message.strip():
            with output_lock:
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                output_buffer.append(f"[{timestamp}] {message.strip()}")
                if len(output_buffer) > 100:
                    output_buffer.pop(0)
            sys.__stdout__.write(message)
    
    def flush(self):
        sys.__stdout__.flush()

if SHOW_CONSOLE_OUTPUT:
    sys.stdout = ConsoleCapture()

# Add this at the top with other global variables
last_output_index = 0  # Track the last output index we've sent

@app.route('/console-output')
def get_console_output():
    global last_output_index
    if not SHOW_CONSOLE_OUTPUT:
        return jsonify({'output': ''})
    
    with output_lock:
        # Only get new output since last request
        new_output = output_buffer[last_output_index:]
        last_output_index = len(output_buffer)
        output = '\n'.join(new_output) if new_output else ''
    return jsonify({'output': output})

# Check if running on macOS
if platform.system() != 'Darwin':
    print("This app is only supported on macOS")
    exit(1)

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Downloader</title>
    <style>
        /* SF Pro Font Import */
        @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap');

        /* Reset & Base Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background-color: #000000;
            color: #f5f5f7;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -.022em;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* Main Container */
        .container {
            width: 90%;
            max-width: 600px;
            padding: 2.5rem;
            background: #1d1d1f;
            border-radius: 18px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }

        /* Typography */
        h1 {
            font-size: 40px;
            line-height: 1.1;
            font-weight: 600;
            letter-spacing: 0;
            margin-bottom: 2rem;
            text-align: center;
            color: #f5f5f7;
        }

        /* Form Elements */
        .input-group {
            margin-bottom: 1.5rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px 16px;
            font-size: 17px;
            border: 1px solid #424245;
            border-radius: 12px;
            outline: none;
            transition: all 0.3s ease;
            background-color: #2d2d2d;
            color: #f5f5f7;
        }

        input[type="text"]::placeholder {
            color: #86868b;
        }

        input[type="text"]:focus {
            border-color: #0071e3;
            box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.3);
        }

        /* Buttons */
        .button-group {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        button {
            background-color: #0071e3;
            color: #ffffff;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 17px;
            font-weight: 400;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: 140px;
        }

        button:hover {
            background-color: #0077ed;
            transform: scale(1.02);
        }

        button:active {
            transform: scale(0.98);
        }

        /* Status Message */
        #status {
            margin-top: 2rem;
            text-align: center;
            font-size: 17px;
            color: #f5f5f7;
            min-height: 24px;
            transition: all 0.3s ease;
        }

        /* Loading Animation */
        .loading {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 13px;
        }

        .loading div {
            position: absolute;
            width: 13px;
            height: 13px;
            border-radius: 50%;
            background: #0071e3;
            animation-timing-function: cubic-bezier(0, 1, 1, 0);
        }

        .loading div:nth-child(1) {
            left: 8px;
            animation: loading1 0.6s infinite;
        }

        .loading div:nth-child(2) {
            left: 8px;
            animation: loading2 0.6s infinite;
        }

        .loading div:nth-child(3) {
            left: 32px;
            animation: loading2 0.6s infinite;
        }

        .loading div:nth-child(4) {
            left: 56px;
            animation: loading3 0.6s infinite;
        }

        @keyframes loading1 {
            0% { transform: scale(0); }
            100% { transform: scale(1); }
        }

        @keyframes loading2 {
            0% { transform: translate(0, 0); }
            100% { transform: translate(24px, 0); }
        }

        @keyframes loading3 {
            0% { transform: scale(1); }
            100% { transform: scale(0); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .container {
                width: 95%;
                padding: 1.5rem;
            }

            h1 {
                font-size: 32px;
            }

            .button-group {
                flex-direction: column;
                gap: 0.8rem;
            }

            button {
                width: 100%;
            }
        }

        /* Console Output Styles */
        .console-toggle {
            margin: 0;
            width: auto;
            opacity: 1;
        }

        .console-output {
            width: 100%;
            height: 150px;
            background: #000000;
            border: 1px solid #424245;
            border-radius: 12px;
            padding: 12px;
            font-family: monospace; 
            font-size: 13px;
            color: #00ff00;
            overflow-y: auto;
            margin-top: 1rem;
        }

        .console-output.show {
            display: block;
        }

        .console-output pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        @media (max-width: 768px) {
            .console-output {
                width: 95%;
                right: 2.5%;
                bottom: 60px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Yt-dlp</h1>
        <div class="input-group">
            <input type="text" id="url" placeholder="Paste your video URL here" autocomplete="off">
        </div>
        <div class="button-group">
            <button onclick="download('mp3')">Download MP3</button>
            <button onclick="download('mp4')">Download MP4</button>
            <button class="console-toggle" onclick="toggleConsole()">Toggle Console</button>
        </div>
        <div id="status"></div>
        <div id="console" class="console-output show">
            <pre id="console-text"></pre>
        </div>
    </div>

    <script>
        let isDownloading = false;
        let pollInterval;

        function download(format) {
            const url = document.getElementById('url').value;
            const status = document.getElementById('status');
            
            if (!url) {
                status.textContent = 'Please enter a URL';
                return;
            }

            // Show loading animation
            status.innerHTML = '<div class="loading"><div></div><div></div><div></div><div></div></div>';
            
            // Start polling when download begins
            isDownloading = true;
            startPolling();

            fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}&format=${format}`
            })
            .then(response => response.json())
            .then(data => {
                status.textContent = data.message;
                if (data.success) {
                    document.getElementById('url').value = '';
                }
                // Stop polling when download is complete
                isDownloading = false;
                stopPolling();
            })
            .catch(error => {
                status.textContent = 'Error occurred during download';
                console.error('Error:', error);
                isDownloading = false;
                stopPolling();
            });
        }

        function startPolling() {
            // Clear any existing interval
            stopPolling();
            // Start new polling interval
            pollInterval = setInterval(pollConsoleOutput, 1000);
        }

        function stopPolling() {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        }

        function toggleConsole() {
            const console = document.getElementById('console');
            console.classList.toggle('show');
        }

        function pollConsoleOutput() {
            if (!isDownloading) return;

            fetch('/console-output')
                .then(response => response.json())
                .then(data => {
                    const consoleText = document.getElementById('console-text');
                    if (data.output) {
                        consoleText.innerHTML += data.output;
                        consoleText.scrollTop = consoleText.scrollHeight;
                    }
                });
        }
    </script>
</body>
</html>
'''

# Global variables
MAX_FILENAME_LENGTH = 200

def get_username():
    try:
        # macOS specific username retrieval
        username = os.environ.get('USER')
        if not username:
            home = os.path.expanduser('~')
            username = home.split('/')[-1]
        return username
    except:
        return None

def get_icloud_folder():
    username = get_username()
    if not username:
        raise Exception("Could not determine username")
    
    folder_path = f'/Users/{username}/Library/Mobile Documents/com~apple~CloudDocs/youtube-dl'
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def download_video(url, format_type):
    output_folder = get_icloud_folder()
    if format_type == 'mp3':
        download_options = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{output_folder}/%(title).{MAX_FILENAME_LENGTH}s.%(ext)s',
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
            'ignoreerrors': True
        }
    else:  # mp4
        download_options = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'{output_folder}/%(title).{MAX_FILENAME_LENGTH}s.%(ext)s',
            'embed_thumbnail': True,
        }

    if "x.com" in url:
        url = url.replace('x.com', 'twitter.com')
        download_options['cookiefile'] = 'cookies.txt'

    try:
        with YoutubeDL(download_options) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    # Simple login page HTML
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login</title>
            <style>
                /* SF Pro Font Import */
                @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap');

                /* Reset & Base Styles */
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
                    background-color: #000000;
                    color: #f5f5f7;
                    line-height: 1.47059;
                    font-weight: 400;
                    letter-spacing: -.022em;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                /* Main Container */
                .container {
                    width: 90%;
                    max-width: 600px;
                    padding: 2.5rem;
                    background: #1d1d1f;
                    border-radius: 18px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }

                /* Typography */
                h1 {
                    font-size: 40px;
                    line-height: 1.1;
                    font-weight: 600;
                    letter-spacing: 0;
                    margin-bottom: 2rem;
                    text-align: center;
                    color: #f5f5f7;
                }

                /* Form Elements */
                .input-group {
                    margin-bottom: 1.5rem;
                }

                input[type="password"] {
                    width: 100%;
                    padding: 12px 16px;
                    font-size: 17px;
                    border: 1px solid #424245;
                    border-radius: 12px;
                    outline: none;
                    transition: all 0.3s ease;
                    background-color: #2d2d2d;
                    color: #f5f5f7;
                }

                input[type="password"]::placeholder {
                    color: #86868b;
                }

                input[type="password"]:focus {
                    border-color: #0071e3;
                    box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.3);
                }

                /* Buttons */
                .button-group {
                    display: flex;
                    gap: 1rem;
                    justify-content: center;
                    margin-top: 2rem;
                }

                button {
                    background-color: #0071e3;
                    color: #ffffff;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 12px;
                    font-size: 17px;
                    font-weight: 400;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    min-width: 140px;
                }

                button:hover {
                    background-color: #0077ed;
                    transform: scale(1.02);
                }

                button:active {
                    transform: scale(0.98);
                }

                /* Status Message */
                #status {
                    margin-top: 2rem;
                    text-align: center;
                    font-size: 17px;
                    color: #f5f5f7;
                    min-height: 24px;
                }

                /* Responsive Design */
                @media (max-width: 768px) {
                    .container {
                        width: 95%;
                        padding: 1.5rem;
                    }

                    h1 {
                        font-size: 32px;
                    }

                    button {
                        width: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Yt-dlp</h1>
                <div class="input-group">
                    <input type="password" id="password" placeholder="Enter password" autocomplete="off">
                </div>
                <div class="button-group">
                    <button onclick="login()">Login</button>
                </div>
                <div id="status"></div>
            </div>
            <script>
                function login() {
                    const password = document.getElementById('password').value;
                    const status = document.getElementById('status');
                    
                    fetch('/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `password=${encodeURIComponent(password)}`
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.href = '/app';
                        } else {
                            status.textContent = 'Invalid password';
                        }
                    });
                }

                // Add enter key support
                document.getElementById('password').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        login();
                    }
                });
            </script>
        </body>
        </html>
    ''')

@app.route('/')
def index():
    return render_template_string('''
        <script>
            window.location.href = '/login';
        </script>
    ''')

@app.route('/app')
def app_route():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_type = request.form.get('format')
    
    if not url:
        return jsonify({'success': False, 'message': 'No URL provided'})
    
    success = download_video(url, format_type)
    return jsonify({
        'success': success,
        'message': 'Download complete!' if success else 'Download failed'
    })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                             'apple-touch-icon.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
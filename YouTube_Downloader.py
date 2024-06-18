import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from pytube import YouTube

# Global variables
download_path = os.path.join(os.path.expanduser("~"), "Downloads")
total_bytes = 0


def download_video():
    url = url_entry.get()
    thread = threading.Thread(target=download_worker, args=(url,))
    thread.start()


def download_worker(url):
    global total_bytes
    try:
        yt = YouTube(url, on_progress_callback=update_progress)
        stream = yt.streams.get_highest_resolution()
        total_bytes = stream.filesize

        # Check if the file exists in the download directory
        base_filename = stream.default_filename
        download_filename = os.path.join(download_path, base_filename)

        if os.path.exists(download_filename):
            # File exists, generate a unique filename
            i = 1
            while True:
                unique_filename = f"{os.path.splitext(base_filename)[0]}_{i}{os.path.splitext(base_filename)[1]}"
                download_filename = os.path.join(download_path, unique_filename)
                if not os.path.exists(download_filename):
                    break
                i += 1

        append_to_status(f"Downloading: {yt.title}\n\n")

        # Start downloading in a separate thread
        download_thread = threading.Thread(target=download_stream, args=(stream, download_filename))
        download_thread.start()

    except Exception as e:
        append_to_status(f"Error: {str(e)}\n")


def download_stream(stream, download_filename):
    try:
        stream.download(output_path=download_path, filename=os.path.basename(download_filename))

        # When download is complete, update status
        append_to_status(f"Download completed! Saved to: {download_filename}\n")
    except Exception as e:
        append_to_status(f"Error downloading: {str(e)}\n")


def update_progress(stream, chunk, bytes_remaining):
    global total_bytes
    bytes_downloaded = total_bytes - bytes_remaining
    percentage = (bytes_downloaded / total_bytes) * 100
    progress['value'] = percentage
    progress_label.config(text=f"Download Progress: {int(percentage)}%")
    root.update_idletasks()


def append_to_status(message):
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, message)
    status_text.config(state=tk.DISABLED)
    status_text.see(tk.END)  # Scroll to the end of the text widget


# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Create a custom style for ttk widgets
style = ttk.Style()
style.theme_use('clam')  # Choose a modern theme, 'clam' is one option
style.configure('TButton', padding=6, relief='raised')

# Create and place the widgets
url_label = ttk.Label(root, text="Enter YouTube URL:")
url_label.pack(pady=10)

url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=10)

download_button = ttk.Button(root, text="Download", command=download_video)
download_button.pack(pady=10)

progress_label = ttk.Label(root, text="Download Progress: 0%")
progress_label.pack(pady=5)

progress = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress.pack(pady=10)

status_text = scrolledtext.ScrolledText(root, height=6, width=50, wrap=tk.WORD)
status_text.pack(pady=10)
status_text.configure(font=("Helvetica", 10))

# Center the window on the screen
window_width = 600
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Run the application
root.mainloop()

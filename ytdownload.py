import tkinter as tk
from tkinter import ttk, messagebox
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os, threading, time

# AZ

print("( ͡° ͜ʖ ͡°)\ngrabby grabby")

def download_video(video, lower_resolution=False, base_file_name=None, output_name=None):
    try:
        if lower_resolution:
            stream = video.streams.filter(file_extension='mp4', res='360p').first()
        else:
            stream = video.streams.filter(file_extension='mp4').first()

        if os.path.exists(base_file_name):
            messagebox.showinfo("Info", "File already exists. Download skipped.")
            progress_label.config(text=f"{output_name} already exists")
        else:
            stream.download(output_path=os.getcwd(), filename=base_file_name)
            progress_label.config(text=f"{output_name} downloaded")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {str(e)}")

def process_to_wav(mp4_file):
    try:
        wav_file = mp4_file.replace('.mp4', '.wav')
        video_clip = VideoFileClip(mp4_file)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(wav_file, codec='pcm_s16le', bitrate='192k')
        video_clip.close()
        audio_clip.close()
        os.remove(mp4_file)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while converting to WAV: {str(e)}")

def cut_video(input_file, output_file, start_time, end_time):
    try:
        video_clip = VideoFileClip(input_file)
        cut_video_clip = video_clip.subclip(start_time, end_time)
        cut_video_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, logger=None)
        video_clip.close()
        cut_video_clip.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while cutting the video: {str(e)}")

def process_video(video, convert_to_wav=False, lower_resolution=False, start_time=None, end_time=None, output_name=None):
    try:
        if output_name in (None, ''):
            output_name = video.title
            
        base_file_name = os.path.join(os.getcwd(), f"{output_name}.mp4")

        progress_label.config(text="downloading video...")
        app.switch_gif()
        download_video(video, lower_resolution, base_file_name, output_name)

        if convert_to_wav:
            process_to_wav(base_file_name)

        elif start_time is not None and end_time is not None:
            output_file = os.path.join(os.getcwd(), f"{output_name}_cut.mp4")
            cut_video(base_file_name, output_file, start_time, end_time)
            
        app.switch_gif()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def process_input():
    input_id = url_entry.get()
    if not input_id:
        messagebox.showerror("Error", "Please enter a URL or ID.")
        return

    try:
        video = YouTube(input_id)
        convert_to_wav = convert_var.get()
        lower_resolution = resolution_var.get()

        start_time_str = start_time_entry.get()
        end_time_str = end_time_entry.get()
        output_name = output_name_entry.get()

        if start_time_str and end_time_str:
            start_time = int(start_time_str.split(":")[0]) * 60 + int(start_time_str.split(":")[1])
            end_time = int(end_time_str.split(":")[0]) * 60 + int(end_time_str.split(":")[1])
        else:
            start_time = None
            end_time = None
        
        threading.Thread(target=process_video, args=(video, convert_to_wav, lower_resolution, start_time, end_time, output_name)).start()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")    
        progress_label.config(text="an error occurred")

def convert_checkbox_callback(*args):
    if convert_var.get():
        start_time_entry.config(state=tk.DISABLED)
        end_time_entry.config(state=tk.DISABLED)
    else:
        start_time_entry.config(state=tk.NORMAL)
        end_time_entry.config(state=tk.NORMAL)
        

def set_default_style():
    default_font = ("Comic Sans MS", 10, "bold")
    style = ttk.Style()
    style.configure('.', font=default_font)

root = tk.Tk()
root.title("youtube snatcher")
root.geometry("650x230")

set_default_style()

from urllib import request
from io import BytesIO
from PIL import Image, ImageTk

try:
    class GifSwitcherApp:
        def __init__(self, root):
            self.root = root

            # GIF URLs
            self.gif_urls = [
                "https://64.media.tumblr.com/77fe2713e463f0b6bafc5555eda92a28/c37a8340022fc418-fa/s250x400/26fd3c62c039887ec4218447640f30706adf37a6.gifv",
                "https://64.media.tumblr.com/465ee7bbdc4b79258ab8f5fd0ca4d674/a2436daad0a4c6f1-65/s540x810/1dd4a359f882dcf459f97bf52ec12d29c674c57d.gifv"
            ]

            # Initialize variables
            self.current_gif_index = 0
            self.gif_data = self.download_gif(self.gif_urls[0])

            # Display initial GIF
            self.frame = tk.Label(root, width=80, height=80)
            self.frame.grid(row=0, column=1, rowspan=4, padx=5, pady=5)

            # Start updating the GIF
            self.update_gif()

        def download_gif(self, url):
            response = request.urlopen(url)
            gif_data = response.read()
            img = Image.open(BytesIO(gif_data))
            return img

        def switch_gif(self):
            # Switch to the other gif
            self.current_gif_index = 1 - self.current_gif_index
            self.gif_data = self.download_gif(self.gif_urls[self.current_gif_index])

        def resize_gif(self, width, height):
            return self.gif_data.resize((width, height), Image.Resampling.LANCZOS)

        def update_gif(self):
            try:
                self.gif_data.seek(self.gif_data.tell() + 1)
                resized_frame = ImageTk.PhotoImage(self.resize_gif(80, 80).convert("RGBA"))
                self.frame.configure(image=resized_frame)
                self.frame.image = resized_frame
                self.root.after(int(self.gif_data.info["duration"]), self.update_gif)
            except EOFError:
                self.gif_data.seek(0)
                self.root.after(0, self.update_gif)
    app = GifSwitcherApp(root)
except Exception as e:
    print(e)
    print("Get better internet bozo")


url_label = ttk.Label(root, text="video url or id:")
url_label.grid(row=0, column=0, padx=2, pady=2, sticky="w")

url_entry = ttk.Entry(root, width=50)
url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

convert_var = tk.BooleanVar()
convert_var.trace_add("write", convert_checkbox_callback)
convert_check = ttk.Checkbutton(root, text="convert to wav", variable=convert_var)
convert_check.grid(row=1, column=0, padx=10, pady=5, sticky="w")

resolution_var = tk.BooleanVar()
resolution_check = ttk.Checkbutton(root, text="360p", variable=resolution_var)
resolution_check.grid(row=2, column=0, padx=10, pady=5, sticky="w")

start_time_label = ttk.Label(root, text="start time (format: mm:ss):")
start_time_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
start_time_entry = ttk.Entry(root, width=10)
start_time_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

end_time_label = ttk.Label(root, text="end time (format: mm:ss):")
end_time_label.grid(row=3, column=2, padx=10, pady=5, sticky="w")
end_time_entry = ttk.Entry(root, width=10)
end_time_entry.grid(row=3, column=3, padx=10, pady=5, sticky="w")

output_name_label = ttk.Label(root, text="output name:")
output_name_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
output_name_entry = ttk.Entry(root, width=20)
output_name_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

process_button = ttk.Button(root, text="go", command=process_input)
process_button.grid(row=5, column=0, columnspan=4, pady=10)

progress_label = ttk.Label(root, text="")
progress_label.grid(row=5, column=2, columnspan=4, pady=10)

def dancing_guy_loop():
    while True:
        dancing_guy_label.config(text="\(._.\) ← look@himgo")
        time.sleep(0.5)
        dancing_guy_label.config(text="(/._.)/ ← look@himgo")
        time.sleep(0.5)

dancing_guy_label = tk.Label(root, text="( ͡° ͜ʖ ͡°)")
dancing_guy_label.grid(row=5, column=0, padx=10, pady=0, sticky="sw")

dancing_guy_thread = threading.Thread(target=dancing_guy_loop)
dancing_guy_thread.start()

def on_closing():
    print("lol")

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedStyle
import threading
import time
import queue
import os
import speech_recognition as sr
import pyttsx3

class SpeechRecognitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech Recognition System")
        self.current_frame = None
        self.style = ThemedStyle(self)
        self.style.set_theme("plastik")  # Change theme if desired
        self.configure_gui_styles()
        self.center_window()
        self.switch_frame(HomePage)

    def switch_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()

        self.current_frame = frame_class(self, self)
        self.current_frame.pack(expand=True, fill="both")

    def center_window(self):
        window_width = 600
        window_height = 400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

    def configure_gui_styles(self):
        # Set background color to light pink for all frames
        self.style.configure('.', background='#FFB6C1')

        # Set button colors to dark blue
        self.style.configure('Custom.TButton', foreground='white', font=('Helvetica', 18, 'bold'))
        self.style.map('Custom.TButton', background=[('active', '#00008B')])

        self.style.configure('Custom.TEntry', background='#FFFF00', borderwidth=2, relief='solid', padding=5, font=('Mynamar MN', 22))

        self.style.configure('Custom.TLabel', foreground='#555', font=('Helvetica', 10))

        self.style.configure('Custom.TText', background='#FFFF00', bd=2, relief='solid', padx=5, pady=5, font=('Mynamar MN', 22), fg='#555')

        self.style.configure('Custom.TCombobox', background='#FFFF00', borderwidth=2, relief='solid', padding=5, font=('Mynamar MN', 22))


class LoadingAnimation(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.attributes('-fullscreen', True)
        self.label = ttk.Label(self, text="Loading...", font=('Helvetica', 16))
        self.label.pack(padx=20, pady=10)
        self.progress = ttk.Progressbar(self, mode='indeterminate', length=200)
        self.progress.pack(pady=10)

    def start_animation(self):
        self.label.after(2000, self.destroy)  # Destroy after 2 seconds
        self.progress.start()

    def stop_animation(self):
        if self.progress.winfo_exists():  # Check if progress bar widget exists
            self.progress.stop()


class AnimatedFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

    def slide_in(self):
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

    def slide_out(self):
        self.place_forget()


class HomePage(AnimatedFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        title_label = ttk.Label(self, text="Speech Recognition System", style='Custom.TLabel', font=("Helvetica", 20))
        title_label.pack(pady=20)

        text_to_speech_btn = ttk.Button(self, text="Text to Speech", style='Custom.TButton', command=self.show_loading_animation_text_to_speech)
        text_to_speech_btn.pack(pady=10)

        speech_to_text_btn = ttk.Button(self, text="Speech to Text", style='Custom.TButton', command=self.show_loading_animation_speech_to_text)
        speech_to_text_btn.pack(pady=10)

        real_time_btn = ttk.Button(self, text="Real Time", style='Custom.TButton', command=self.show_loading_animation_real_time)
        real_time_btn.pack(pady=10)

    def show_loading_animation_text_to_speech(self):
        loading_animation = LoadingAnimation(self.controller)
        loading_animation.start_animation()
        self.controller.after(2000, lambda: self.show_frame(TextToSpeechPage))
        self.controller.after(2200, loading_animation.stop_animation)

    def show_loading_animation_speech_to_text(self):
        loading_animation = LoadingAnimation(self.controller)
        loading_animation.start_animation()
        self.controller.after(2000, lambda: self.show_frame(SpeechToTextPage))
        self.controller.after(2200, loading_animation.stop_animation)

    def show_loading_animation_real_time(self):
        loading_animation = LoadingAnimation(self.controller)
        loading_animation.start_animation()
        self.controller.after(2000, lambda: self.show_frame(RealTimePage))
        self.controller.after(2200, loading_animation.stop_animation)

    def show_frame(self, page):
        self.controller.switch_frame(page)


class TextToSpeechPage(AnimatedFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.text_entry = ttk.Entry(self, width=50, style='Custom.TEntry')
        self.text_entry.pack(pady=10)

        self.play_btn = ttk.Button(self, text="Play", style='Custom.TButton', command=self.convert_to_speech)
        self.play_btn.pack(pady=10)

        back_btn = ttk.Button(self, text="Back to Home", style='Custom.TButton', command=lambda: controller.switch_frame(HomePage))
        back_btn.pack(pady=10)

    def convert_to_speech(self):
        text = self.text_entry.get()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


class SpeechToTextPage(AnimatedFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.file_path_label = ttk.Label(self, text="Selected File: ", style='Custom.TLabel')
        self.file_path_label.pack(pady=10)

        self.select_file_btn = ttk.Button(self, text="Select Audio File", style='Custom.TButton', command=self.select_audio_file)
        self.select_file_btn.pack(pady=10)

        self.save_text_btn = ttk.Button(self, text="Save Text", style='Custom.TButton', command=self.save_text)
        self.save_text_btn.pack(pady=10)

        self.text_output = tk.Text(self, height=10, width=50, wrap="word")
        self.text_output.pack(pady=10)

        back_btn = ttk.Button(self, text="Back to Home", style='Custom.TButton', command=lambda: controller.switch_frame(HomePage))
        back_btn.pack(pady=10)

        self.configure_text_widget()

    def select_audio_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
        self.file_path_label.config(text="Selected File: " + self.file_path)

    def save_text(self):
        if hasattr(self, 'file_path'):
            threading.Thread(target=self.process_audio).start()

    def process_audio(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.file_path) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            self.text_output.delete('1.0', tk.END)  # Clear previous text
            self.text_output.insert(tk.END, text)
            self.save_text_to_file(text)
            messagebox.showinfo("Save Text", "Text saved successfully.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Unable to recognize speech.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from Google Speech Recognition service; {e}")

    def save_text_to_file(self, text):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(text)

    def configure_text_widget(self):
        self.text_output.config(bg='white', bd=2, relief='solid', padx=5, pady=5, font=('Mynamar MN', 22), fg='#555')


class RealTimePage(AnimatedFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.text_box = tk.Text(self, height=10, width=50, wrap="word")
        self.text_box.pack(pady=10)

        self.language_var = tk.StringVar(value="en")  # Default language is English

        language_label = ttk.Label(self, text="Select Language:", style='Custom.TLabel')
        language_label.pack(pady=5)

        self.language_menu = ttk.Combobox(self, textvariable=self.language_var, values=["en", "hi", "mr"], style='Custom.TCombobox')
        self.language_menu.pack(pady=5)

        self.start_btn = ttk.Button(self, text="Start", style='Custom.TButton', command=self.start_real_time_recognition)
        self.start_btn.pack(pady=10)

        self.stop_btn = ttk.Button(self, text="Stop", style='Custom.TButton', command=self.stop_real_time_recognition)
        self.stop_btn.pack(pady=10)
        self.stop_btn.config(state=tk.DISABLED)

        back_btn = ttk.Button(self, text="Back to Home", style='Custom.TButton', command=lambda: controller.switch_frame(HomePage))
        back_btn.pack(pady=10)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.stop_event = threading.Event()

    def start_real_time_recognition(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.text_box.delete('1.0', tk.END)  # Clear previous text

        language = self.language_var.get()

        threading.Thread(target=self.listen_microphone, args=(language,)).start()

    def stop_real_time_recognition(self):
        self.stop_event.set()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def listen_microphone(self, language):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            while not self.stop_event.is_set():
                try:
                    audio_data = self.recognizer.listen(source, timeout=5)
                    if language == "hi":
                        text = self.recognizer.recognize_google(audio_data, language="hi-IN")
                    elif language == "mr":
                        text = self.recognizer.recognize_google(audio_data, language="mr-IN")
                    else:
                        text = self.recognizer.recognize_google(audio_data)
                    self.text_box.insert(tk.END, text + "\n")
                    self.text_box.see(tk.END)  # Scroll to the end of the text box
                except sr.WaitTimeoutError:
                    break
                except sr.UnknownValueError:
                    pass


if __name__ == "__main__":
    app = SpeechRecognitionApp()
    app.mainloop()
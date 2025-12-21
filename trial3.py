import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedStyle
import threading
import speech_recognition as sr
import pyttsx3
import os

class SpeechRecognitionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech Recognition System")
        self.current_frame = None
        self.style = ThemedStyle(self)
        self.style.set_theme("plastik")
        
        # Global instances to prevent re-initialization lag
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        
        self.configure_gui_styles()
        self.center_window()
        self.switch_frame(HomePage)

    def switch_frame(self, frame_class):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, self)
        self.current_frame.pack(expand=True, fill="both")

    def center_window(self):
        window_width, window_height = 600, 400
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def configure_gui_styles(self):
        self.style.configure('.', background='#FFB6C1')
        self.style.configure('Custom.TButton', foreground='white', font=('Helvetica', 14, 'bold'))
        self.style.configure('Custom.TEntry', font=('Helvetica', 12))
        self.style.configure('Custom.TLabel', foreground='#555', font=('Helvetica', 12))

class HomePage(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        ttk.Label(self, text="Speech Recognition System", style='Custom.TLabel', font=("Helvetica", 20)).pack(pady=20)

        # Removed the 2-second artificial loading delay for instant transitions
        ttk.Button(self, text="Text to Speech", style='Custom.TButton', 
                   command=lambda: controller.switch_frame(TextToSpeechPage)).pack(pady=10)
        ttk.Button(self, text="Speech to Text", style='Custom.TButton', 
                   command=lambda: controller.switch_frame(SpeechToTextPage)).pack(pady=10)
        ttk.Button(self, text="Real Time", style='Custom.TButton', 
                   command=lambda: controller.switch_frame(RealTimePage)).pack(pady=10)

class TextToSpeechPage(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.text_entry = ttk.Entry(self, width=50)
        self.text_entry.pack(pady=20)
        
        ttk.Button(self, text="Play", style='Custom.TButton', command=self.convert_to_speech).pack(pady=10)
        ttk.Button(self, text="Back", style='Custom.TButton', command=lambda: controller.switch_frame(HomePage)).pack(pady=10)

    def convert_to_speech(self):
        text = self.text_entry.get()
        if text.strip():
            # Run in thread so the GUI doesn't freeze during speech
            threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text):
        self.controller.engine.say(text)
        self.controller.engine.runAndWait()

class SpeechToTextPage(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.file_path = ""
        
        self.label = ttk.Label(self, text="No file selected")
        self.label.pack(pady=10)
        
        ttk.Button(self, text="Select File", style='Custom.TButton', command=self.select_audio_file).pack(pady=5)
        ttk.Button(self, text="Process & Save", style='Custom.TButton', command=self.start_processing).pack(pady=5)
        
        self.text_output = tk.Text(self, height=8, width=50)
        self.text_output.pack(pady=10)
        ttk.Button(self, text="Back", style='Custom.TButton', command=lambda: controller.switch_frame(HomePage)).pack(pady=5)

    def select_audio_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav;*.mp3")])
        if self.file_path:
            self.label.config(text=f"Selected: {os.path.basename(self.file_path)}")

    def start_processing(self):
        if self.file_path:
            threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        recognizer = self.controller.recognizer
        try:
            with sr.AudioFile(self.file_path) as source:
                audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
            # Use .after to update GUI from thread safely
            self.controller.after(0, lambda: self.update_ui(text))
        except Exception as e:
            self.controller.after(0, lambda: messagebox.showerror("Error", str(e)))

    def update_ui(self, text):
        self.text_output.delete('1.0', tk.END)
        self.text_output.insert(tk.END, text)
        # Immediate prompt to save after processing
        save_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if save_path:
            with open(save_path, "w") as f: f.write(text)

class RealTimePage(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.text_box = tk.Text(self, height=10, width=50)
        self.text_box.pack(pady=10)

        self.lang_var = tk.StringVar(value="en-US")
        ttk.Label(self, text="Language:").pack()
        self.combo = ttk.Combobox(self, textvariable=self.lang_var, values=["en-US", "hi-IN", "mr-IN"])
        self.combo.pack(pady=5)

        self.start_btn = ttk.Button(self, text="Start", command=self.start_listening)
        self.start_btn.pack(pady=5)
        self.stop_btn = ttk.Button(self, text="Stop", command=self.stop_listening, state="disabled")
        self.stop_btn.pack(pady=5)
        
        ttk.Button(self, text="Back", command=lambda: [self.stop_listening(), controller.switch_frame(HomePage)]).pack()

        self.is_listening = False
        self.mic = sr.Microphone()

    def start_listening(self):
        self.is_listening = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.listen_loop, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def listen_loop(self):
        with self.mic as source:
            # Calibrate once per session, not once per phrase
            self.controller.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            while self.is_listening:
                try:
                    # listen() blocks until speech is detected
                    audio = self.controller.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    text = self.controller.recognizer.recognize_google(audio, language=self.lang_var.get())
                    self.controller.after(0, lambda t=text: self.text_box.insert(tk.END, t + " "))
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception:
                    break

if __name__ == "__main__":
    app = SpeechRecognitionApp()
    app.mainloop()
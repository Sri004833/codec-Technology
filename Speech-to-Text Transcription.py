import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import speech_recognition as sr
from pydub import AudioSegment
import pyttsx3
import threading

# Language map for Google Speech Recognition API
LANGUAGES = {
    "English (US)": "en-US",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT"
}

def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.replace(".mp3", ".wav")
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

def transcribe_audio_file(file_path, language_code):
    if file_path.endswith(".mp3"):
        file_path = convert_mp3_to_wav(file_path)

    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        log("Listening to the audio file...")
        audio = recognizer.record(source)

    try:
        log("Transcribing file...")
        return recognizer.recognize_google(audio, language=language_code)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"API error: {e}"

def transcribe_from_microphone(language_code):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        log("Adjusting for background noise... please wait.")
        recognizer.adjust_for_ambient_noise(source)
        log("Please speak into the microphone...")
        audio = recognizer.listen(source)

    try:
        log("Transcribing microphone input...")
        return recognizer.recognize_google(audio, language=language_code)
    except sr.UnknownValueError:
        return "Could not understand the speech."
    except sr.RequestError as e:
        return f"API error: {e}"

def choose_file():
    path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
    if path:
        language_code = LANGUAGES[lang_var.get()]
        run_in_thread(transcribe_and_show_file, path, language_code)

def start_microphone():
    language_code = LANGUAGES[lang_var.get()]
    run_in_thread(transcribe_and_show_mic, language_code)

def transcribe_and_show_file(path, language_code):
    set_progress("Processing file...")
    transcription = transcribe_audio_file(path, language_code)
    show_result(transcription)
    set_progress("Done")

def transcribe_and_show_mic(language_code):
    set_progress("Listening...")
    transcription = transcribe_from_microphone(language_code)
    show_result(transcription)
    set_progress("Done")

def show_result(text):
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, text)

def save_transcription():
    text = result_text.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Empty", "There is no transcription to save.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Transcription saved to:\n{filepath}")

def play_transcription():
    text = result_text.get(1.0, tk.END).strip()
    if not text:
        messagebox.showinfo("Empty", "There is no text to play.")
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def run_in_thread(func, *args):
    threading.Thread(target=func, args=args, daemon=True).start()

def set_progress(msg):
    progress_var.set(msg)
    app.update_idletasks()

def log(message):
    print(message)

# Build GUI
app = tk.Tk()
app.title("Speech-to-Text Transcription Tool")
app.geometry("650x500")

frame_top = tk.Frame(app)
frame_top.pack(pady=10)

btn_file = tk.Button(frame_top, text="Transcribe Audio File", command=choose_file, width=25)
btn_file.grid(row=0, column=0, padx=5)

btn_mic = tk.Button(frame_top, text="Transcribe from Microphone", command=start_microphone, width=25)
btn_mic.grid(row=0, column=1, padx=5)

frame_lang = tk.Frame(app)
frame_lang.pack(pady=5)

tk.Label(frame_lang, text="Language:").pack(side=tk.LEFT)
lang_var = tk.StringVar(value="English (US)")
lang_menu = ttk.Combobox(frame_lang, textvariable=lang_var, values=list(LANGUAGES.keys()), state="readonly", width=20)
lang_menu.pack(side=tk.LEFT, padx=5)

progress_var = tk.StringVar(value="Idle")
progress_label = tk.Label(app, textvariable=progress_var, fg="blue")
progress_label.pack()

result_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=75, height=18)
result_text.pack(padx=10, pady=10)

frame_bottom = tk.Frame(app)
frame_bottom.pack(pady=5)

btn_save = tk.Button(frame_bottom, text="Save Transcription", command=save_transcription)
btn_save.grid(row=0, column=0, padx=5)

btn_play = tk.Button(frame_bottom, text="Play Transcription", command=play_transcription)
btn_play.grid(row=0, column=1, padx=5)

app.mainloop()

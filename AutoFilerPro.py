"""
AI AutoFiler Pro is a tool that automates the process of creating files, sorting data, reading and viewing them,
and finding data using artificial intelligence and language processing capabilities. In addition to these core features,
it also includes a speech recognition tool to allow for hands-free operation.
Written by: @HeavenHM
Date: 2021-09-10
Version: 1.1
"""

# Importing the libraries.
import tkinter as tk
import tkinter.messagebox as messagebox
from io import StringIO
import sys
from langchain.agents import initialize_agent
from langchain.agents.tools import Tool
from langchain.llms import OpenAI
import speech_recognition as sr
import os
from gtts import gTTS
from playsound import playsound

# Setting up the OpenAI API key.
open_ai_key = os.environ.get("OPENAI_API_KEY")
output_temp = "output.mp3"

class PythonREPL:
    """Simulates a standalone Python REPL."""

    def __init__(self):
        pass

    def run(self, command: str) -> str:
        """Run command and returns anything printed."""
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(command, globals())
            sys.stdout = old_stdout
            output = mystdout.getvalue()
        except Exception as e:
            sys.stdout = old_stdout
            output = str(e)
        return output

# Method to run the query and display the output
def run_query(query, output_box,rate, enable_tts):
    model_kwargs = {"temperature": 0.0, "model": "text-davinci-003", "api_key":open_ai_key}
    llm = OpenAI(**model_kwargs)
    python_repl = Tool("Python REPL",PythonREPL().run,
        "A Python shell. Use this to execute python commands." +
        "Input should be a valid python command. If you expect output it should be printed out.",
    )
    tools = [python_repl]
    # Initialize the agent with parameters.
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", model_kwargs=model_kwargs, verbose=True,max_iterations=50)

    # Clear the output box
    output_box.delete('1.0', tk.END)

    # Run the query and write each response to the output box
    response = agent.run(query)
    output_box.insert(tk.END, response)

    # Speak the output if TTS is enabled
    if enable_tts:
        speak_text(response,'en', rate)

# Method to record voice and convert it to text
def record_voice(input_box, execute_button):
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        input_box.insert(0, text)
        execute_button.invoke()
    except sr.UnknownValueError:
       messagebox.showerror("INFO","Could not understand audio")
    except sr.RequestError as e:
        messagebox.showerror("INFO","Could not request results; {0}".format(e))

# Method to speak text using TTS
def speak_text(text,lang,rate):
    try:
        tts = gTTS(text, lang=lang, slow=(rate=="slow"))
        tts.save(output_temp)
        playsound(output_temp)
        os.remove(output_temp)
    except Exception as e:
        messagebox.showerror("ERROR","Exception occured: " + str(e))

# The main entry point for the app.
def app_main():
    root = tk.Tk()
    root.title("AI AutoFiler Pro")
    #root.geometry("600x400")
    root.resizable(False, False)
    
    # Initialize the TTS engine

    # Create the input frame and widgets
    input_frame = tk.Frame(root)
    input_frame.grid(row=0, column=0, padx=10, pady=10)

    input_label = tk.Label(input_frame, text="Enter query:")
    input_label.grid(row=0, column=0)

    input_box = tk.Entry(input_frame, width=50)
    input_box.grid(row=0, column=1, padx=10)

    # Create the output frame and widgets
    output_frame = tk.Frame(root)
    output_frame.grid(row=3, column=0, padx=10, pady=10)

    output_label = tk.Label(output_frame, text="Output:")
    output_label.grid(row=0, column=0)

    output_box = tk.Text(output_frame, width=80, height=18)
    output_box.grid(row=1, column=0)

    # Create the TTS frame and widgets
    tts_frame = tk.LabelFrame(root, text="Text-to-Speech")
    tts_frame.grid(row=0, column=1, padx=10, pady=10, rowspan=4)

    voice_label = tk.Label(tts_frame, text="Voice model:")
    voice_label.grid(row=0, column=0)

    voice_options = ["Default", "Secondary"]
    voice_var = tk.StringVar(value=voice_options[0])
    voice_menu = tk.OptionMenu(tts_frame, voice_var, *voice_options)
    voice_menu.grid(row=0, column=1)

    rate_label = tk.Label(tts_frame, text="Rate:")
    rate_label.grid(row=1, column=0)

    rate_options = ["slow", "medium", "fast"]
    rate_var = tk.StringVar(value=rate_options[1])
    rate_menu = tk.OptionMenu(tts_frame, rate_var, *rate_options)
    rate_menu.grid(row=1, column=1)

    enable_tts = tk.BooleanVar(value=True)
    enable_tts_checkbox = tk.Checkbutton(tts_frame, text="Enable TTS", variable=enable_tts)
    enable_tts_checkbox.grid(row=2, column=0, columnspan=2)

    record_button = tk.Button(root, text="Record",command=lambda: record_voice(input_box,execute_button))
    record_button.grid(row=1, column=0, sticky='s')

    execute_button = tk.Button(root,text="Execute",command=lambda: run_query(input_box.get(),output_box,rate_var.get(),enable_tts.get()))
    execute_button.grid(row=2, column=0, sticky='s')

    root.mainloop()

if __name__ == '__main__':
    try:
        app_main()
    except Exception as e:
        print("Exception occured: " + str(e))
        messagebox.showerror("ERROR", "Exception occured: " + str(e))



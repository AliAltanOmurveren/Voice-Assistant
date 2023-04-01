#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import os
import json
import subprocess
import re
import math
import pyautogui

if not os.path.exists("model"):
    print ("Please download the model from https://github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as 'model' in the current folder.")
    exit (1)

import pyaudio

# Open the file that contains words to be recognized
with open("words.txt", "r", encoding="UTF-8") as file:
    words = file.read().replace("\n", " ")

# Open the file that contains numbers to be recognized
with open("numbers.json", "r", encoding="UTF-8") as file:
    numbers = json.load(file)

model = Model("model")
# Set words
rec = KaldiRecognizer(model, 16000, words)

# Open commands file
with open("commands.json", "r", encoding="utf-8") as f:
    commands = json.load(f)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

commands_keys = commands.keys()

listen = True

subprocess.call("clear", shell=True)

while True:
    data = stream.read(2000, exception_on_overflow = False)

    number = 0

    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        # Convert results to json
        
        result = json.loads(rec.Result())
        # Get result text
        text = result["text"]
        print(text)

        # Get word count
        text_len = len(text.split())

        if text == "dinlemeyi durdur":
            print("Dinleme durduruldu!")
            listen = False
        
        if text == "dinlemeyi başlat":
            print("Dinleme başlatıldı!")
            listen = True

        if text == "dinlemeyi bitir":
            break
        
        # ADVANCED DEBUGGER 
        #print(text)

        # All commands are longer than 1 word
        if listen and text_len > 1 :
            # if there is a number in the text set the number
            n = 0
            nums = text.split()
            while n in range(len(nums)):
                if nums[n] in numbers:
                    if n < len(nums) - 1 and nums[n + 1] == "yüz":
                        number += numbers[nums[n]] * 100
                        n += 2
                    else:
                        number += numbers[nums[n]]
                        n += 1
                else:
                    n += 1

            # Check if recognized command is valid in commands.json
            
            for k in commands_keys:
                reg = str(re.findall(k + "|$", text)[0])
                if bool(reg):
                    print(reg)
                    
                    if re.search("sistem sesini.* yap", text):
                        subprocess.call(commands["sistem sesini.* yap"] + str(math.floor(number / 100 * 65535)), shell=True)
                    else:
                        # Execute the command in cmd
                        subprocess.call(commands[str(reg)], shell=True)
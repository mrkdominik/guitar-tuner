import sounddevice as sd
import numpy as np
import scipy
import scipy.fftpack
import os
import tkinter as tk

# Global variable general settings

sampling_rate = 44100  # sample frequency in hz
analysis_window_size = 44100  # window size of the DFT in seconds
window_step = 21050  # step size of windows
analysis_window_duration  = analysis_window_size / sampling_rate  # length of window in seconds
sample_duration = 1 / sampling_rate  # length between two samples in seconds
windowSamples = [0 for _ in range(analysis_window_size)]

# This function finds the closest note for a given pitch
# Returns: the note (eg: A4, G3, etc), pitch of the tone

standard_A_frequency = 440
note_names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/standard_A_frequency)*12))
    closest_note = note_names[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = standard_A_frequency * 2 ** (i / 12)
    return closest_note, closest_pitch

# The sounddevice callback function
# Provides us with new data once window_step samples have been finalized

def callback(indata, frames, time, status):
    global windowSamples
    if status:
        print(status)

    if any(indata):
        windowSamples = np.concatenate(
            (windowSamples, indata[:, 0])
        )  # append new samples
        windowSamples = windowSamples[len(indata[:, 0]) :]  # remove old samples
        magnitudeSpec = abs(scipy.fftpack.fft(windowSamples)[: len(windowSamples) // 2])

        for i in range(int(62 / (sampling_rate / analysis_window_size))):
            magnitudeSpec[i] = 0

        maxInd = np.argmax(magnitudeSpec)
        maxFreq = maxInd * (sampling_rate / analysis_window_size)
        closestNote, closestPitch = find_closest_note(maxFreq)

        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print(f"Closest note: {closestNote} {maxFreq:.1f}/{closestPitch:.1f}")

    else:
        print("no input")

try:
    with sd.InputStream(
        channels=1, callback=callback, blocksize=window_step, samplerate=sampling_rate
    ):

        while True:
            pass

except Exception as e:
    print(str(e))

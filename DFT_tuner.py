import sounddevice as sd 
import numpy as np 
import scipy
import scipy.fftpack
import os

# Global variable general settings

sample_freq = 44100 # sample frequency in hz
window_size = 44100 # window size of the DFT in seconds
window_step = 21050 # step size of windows
window_t_len = window_size / sample_freq # length of window in seconds
sample_t_length = 1/sample_freq #length between two samples in seconds
windowSamples = [0 for _ in range(window_size)]


# This function finds the closest note for a given pitch
# Returns: the note (eg: A4, G3, etc), pitch of the tone

concert_pitch = 440
all_notes = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]

def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/concert_pitch))*12)
    closest_note = all_notes[i%12] + str(4+ (i+9) // 12)
    closest_pitch = concert_pitch*2**(i/12)
    return closest_note, closest_pitch

# The sounddevice callback function
# Provides us with new data once window_step samples have been finalized

def callback(indata, frames, time, status):
    global windowSamples
    if status: 
        print(status)

    if any(indata):
        windowSamples = np.concatenate((windowSamples, indata[:,0])) # append new samples
        windowSamples = windowSamples[len(indata[:,0]):] # remove old samples
        magnitudeSpec = abs(scipy.fftpack.fft(windowSamples)[:len(windowSamples)//2])

        for i in range(int(62/(sample_freq/window_size))):
            magnitudeSpec[i] = 0

        maxInd = np.argmax(magnitudeSpec)
        maxFreq = maxInd * (sample_freq/window_size)
        closestNote, closestPitch = find_closest_note(maxFreq)

        if os.name == 'nt':
                os.system('cls')
        else:
            os.system('clear')

        print(f"Closest note: {closestNote} {maxFreq:.1f}/{closestPitch:.1f}")
    
    else: 
        print("no input")

try:
    with sd.InputStream(channels = 1, callback = callback, 
         blocksize = window_step, samplerate = sample_freq):
         
         while True: 
            pass

except Exception as e: 
    print(str(e))

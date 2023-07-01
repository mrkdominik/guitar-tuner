import copy
import os
import numpy as np
import scipy.fftpack
import sounddevice as sd
import time


# Calibrating Global Variables, can be changed by user

sample_freq = 48000
window_size = 48000
window_step = 12000
num_hps = 5
power_thres = 1e-6
concert_pitch = 440
white_noise_thres = 0.2

window_t_len = window_size / sample_freq
sample_t_length = 1 / sample_freq
delta_freq = sample_freq / window_size
octave_bands = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]


all_notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F","F#", "G", "G#"]

def find_closest_note(pitch):
    """
    Finds the closest note for a given pitch
    parameter: pitch ----> float ----> pitch measured in hertz

    returns: 
    closest_note ----> string ----> the closest note to the pitch
    closest_pitch ----> float ----> the pitch of the closest note in hertz
    """

    i = int(np.round(np.log2(pitch / concert_pitch)) * 12)
    closest_note = all_notes[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = concert_pitch * 2 ** (i / 12)
    return closest_note, closest_pitch


hann_window = np.hanning(window_size)
def callback(indata, frames, times, status):
    """
    calling input stream from sounddevice
    """
    if not hasattr(callback, "window_samples"):
        callback.window_samples = [0 for _ in range(window_size)]

    if not hasattr(callback, "noteBuffer"):
        callback.noteBuffer = ["1","2"]

    if status: 
        print(status)
        return

    if any(indata):
        callback.window_samples = np.concatenate(callback.window_samples, indata[:,0]:)

        #skip if singal is too small
        signal_power = (np.linalg.norm(callback.window_samples, ord = 2) ** 2) / len(callback.window_samples)
        if signal_power < power_thres:
            os.system("cls" if os.name = "nt" else "clear")
            print("Closest notes: ....")
            return


        # avoiding spectral leakage
        hann_samples = callback.window_samples * hann_window
        magnitudeSpec = abs(scipy.fftpack.fft(hann_samples)[:len(hann_samples)//2])

        # supress main humss
        for i in range(int(62/delta_freq)):
            magnitude_spec[i] = 0
        
        """ • calculating average power in octave bands, if the power is below the 
        average power, set the magnitude to zero
        • we do this to reduce the effect of white noise, which is essential to run a
        Harmonic Product Spectrum method"""

        for 
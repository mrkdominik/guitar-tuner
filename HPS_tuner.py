import copy
import os
import numpy as np
import scipy.fftpack
import sounddevice as sd
import time
import tkinter as tk

# Calibrating Global Variables, can be changed by user

sampling_rate = 48000
analysis_window_size = 48000
window_step = 12000
hps_iterations = 5
min_power_threshold = 1e-6
standard_A_frequency = 440
white_noise_thres = 0.2

analysis_window_duration  = analysis_window_size / sampling_rate
sample_duration = 1 / sampling_rate
frequency_resolution = sampling_rate / analysis_window_size
octave_bands = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]


note_names = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]


def find_closest_note(pitch):
    """
    Finds the closest note for a given pitch
    parameter: pitch ----> float ----> pitch measured in hertz

    returns:
    closest_note ----> string ----> the closest note to the pitch
    closest_pitch ----> float ----> the pitch of the closest note in hertz
    """

    i = int(np.round(np.log2(pitch / standard_A_frequency) * 12))
    closest_note = note_names[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = standard_A_frequency * 2 ** (i / 12)
    return closest_note, closest_pitch


hann_window = np.hanning(analysis_window_size)

def callback(indata, frames, time, status):
    """
    calling input stream from sounddevice
    """
    if not hasattr(callback, "window_samples"):
        callback.window_samples = [0 for _ in range(analysis_window_size)]

    if not hasattr(callback, "noteBuffer"):
        callback.noteBuffer = ["1", "2"]

    if status:
        print(status)
        return

    if any(indata):
        callback.window_samples = np.concatenate(
            (callback.window_samples, indata[:, 0])
        )
        callback.window_samples = callback.window_samples[len(indata[:, 0]) :]

        # skip if singal is too small
        signal_power = (np.linalg.norm(callback.window_samples, ord=2) ** 2) / len(
            callback.window_samples
        )
        if signal_power < min_power_threshold:
            os.system("cls" if os.name == "nt" else "clear")
            print("Closest note: ....")
            return

        # avoiding spectral leakage
        hann_samples = callback.window_samples * hann_window
        magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[: len(hann_samples) // 2])

        # supress main humss
        for i in range(int(62 / frequency_resolution)):
            magnitude_spec[i] = 0

        """ • calculating average power in octave bands, if the power is below the 
        average power, set the magnitude to zero
        • we do this to reduce the effect of white noise, which is essential to run a
        Harmonic Product Spectrum method"""

        for j in range(len(octave_bands) - 1):
            ind_start = int(octave_bands[j] / frequency_resolution)
            ind_end = int(octave_bands[j + 1] / frequency_resolution)
            ind_end = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
            avg_energy_per_freq = (
                np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2
            ) / (ind_end - ind_start)
            avg_energy_per_freq = avg_energy_per_freq**0.5

            for i in range(ind_start, ind_end):
                magnitude_spec[i] = (
                    magnitude_spec[i]
                    if magnitude_spec[i] > avg_energy_per_freq * white_noise_thres
                    else 0
                )

        # interpolate the magnitude spectrum
        mag_spec_ipol = np.interp(
            np.arange(0, len(magnitude_spec), 1 / hps_iterations),
            np.arange(0, len(magnitude_spec)),
            magnitude_spec,
        )
        mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)

        hps_spec = copy.deepcopy(mag_spec_ipol)

        # calculate the HPS
        for i in range(hps_iterations):
            tmp_hps_spec = np.multiply(
                hps_spec[: int(np.ceil(len(mag_spec_ipol) / (i + 1)))],
                mag_spec_ipol[:: (i + 1)],
            )
            if not any(tmp_hps_spec):
                break
            hps_spec = tmp_hps_spec

        max_ind = np.argmax(hps_spec)
        max_freq = max_ind * (sampling_rate / analysis_window_size) / hps_iterations

        closest_note, closest_pitch = find_closest_note(max_freq)
        max_freq = round(max_freq, 1)
        closest_pitch = round(closest_pitch, 1)

        callback.noteBuffer.insert(0, closest_note)
        callback.noteBuffer.pop()

        os.system("cls" if os.name == "nt" else "clear")
        if callback.noteBuffer.count(callback.noteBuffer[0]) == len(
            callback.noteBuffer
        ):
            print(f"Closest note: {closest_note} {max_freq}/{closest_pitch}")

        else:
            print("Closest notes: ....")

    else:
        print("no input")


try:
    print("Starting Harmonic Product Spectrum Tuner :guitar: 🎸...")
    with sd.InputStream(
        channels=1, callback=callback, blocksize=window_step, samplerate=sampling_rate
    ):
        while True:
            time.sleep(0.5)

except Exception as e:
    print(str(e))
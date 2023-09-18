import copy
import os
import numpy as np
import scipy.fftpack
import sounddevice as sd
import time

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
    i = int(np.round(np.log2(pitch / standard_A_frequency) * 12))
    closest_note = note_names[i % 12]
    closest_pitch = standard_A_frequency * 2 ** (i / 12)
    return closest_note, closest_pitch, i

hann_window = np.hanning(analysis_window_size)

def generate_random_note():
    global random_note, random_note_index
    random_note_index = np.random.randint(0, 12)
    random_note = note_names[random_note_index]
    print(f"Try playing the note: {random_note}")

generate_random_note()

def callback(indata, frames, time, status):
    if not hasattr(callback, "last_printed_note"):
        callback.last_printed_note = None

    if status:
        print(status)
        return

    if any(indata):
        window_samples = np.concatenate(
            (callback.window_samples, indata[:, 0]) if hasattr(callback, "window_samples") else (np.zeros(analysis_window_size), indata[:, 0])
        )
        window_samples = window_samples[len(indata[:, 0]):]

        signal_power = (np.linalg.norm(window_samples, ord=2) ** 2) / len(window_samples)
        if signal_power < min_power_threshold:
            return

        hann_samples = window_samples * hann_window
        magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[: len(hann_samples) // 2])

        for i in range(int(62 / frequency_resolution)):
            magnitude_spec[i] = 0

        for j in range(len(octave_bands) - 1):
            ind_start = int(octave_bands[j] / frequency_resolution)
            ind_end = int(octave_bands[j + 1] / frequency_resolution)
            ind_end = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
            avg_energy_per_freq = (np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2) / (ind_end - ind_start)
            avg_energy_per_freq = avg_energy_per_freq**0.5

            for i in range(ind_start, ind_end):
                magnitude_spec[i] = magnitude_spec[i] if magnitude_spec[i] > avg_energy_per_freq * white_noise_thres else 0

        mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1 / hps_iterations), np.arange(0, len(magnitude_spec)), magnitude_spec)
        mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)

        hps_spec = copy.deepcopy(mag_spec_ipol)

        for i in range(hps_iterations):
            tmp_hps_spec = np.multiply(hps_spec[: int(np.ceil(len(mag_spec_ipol) / (i + 1)))], mag_spec_ipol[:: (i + 1)])
            if not any(tmp_hps_spec):
                break
            hps_spec = tmp_hps_spec

        max_ind = np.argmax(hps_spec)
        max_freq = max_ind * (sampling_rate / analysis_window_size) / hps_iterations

        closest_note, closest_pitch, index = find_closest_note(max_freq)

        if closest_note == random_note:
            if callback.last_printed_note != closest_note:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"Great job! You played {closest_note}.")
                callback.last_printed_note = closest_note
                generate_random_note()
        elif callback.last_printed_note != closest_note:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"You played {closest_note}, but we're expecting {random_note}. Try again!")
            callback.last_printed_note = closest_note

    else:
        print("no input")    if not hasattr(callback, "last_printed_note"):
        callback.last_printed_note = None

    if status:
        print(status)
        return

    if any(indata):
        window_samples = np.concatenate(
            (callback.window_samples, indata[:, 0]) if hasattr(callback, "window_samples") else (np.zeros(analysis_window_size), indata[:, 0])
        )
        window_samples = window_samples[len(indata[:, 0]):]

        signal_power = (np.linalg.norm(window_samples, ord=2) ** 2) / len(window_samples)
        if signal_power < min_power_threshold:
            return

        hann_samples = window_samples * hann_window
        magnitude_spec = abs(scipy.fftpack.fft(hann_samples)[: len(hann_samples) // 2])

        for i in range(int(62 / frequency_resolution)):
            magnitude_spec[i] = 0

        for j in range(len(octave_bands) - 1):
            ind_start = int(octave_bands[j] / frequency_resolution)
            ind_end = int(octave_bands[j + 1] / frequency_resolution)
            ind_end = ind_end if len(magnitude_spec) > ind_end else len(magnitude_spec)
            avg_energy_per_freq = (np.linalg.norm(magnitude_spec[ind_start:ind_end], ord=2) ** 2) / (ind_end - ind_start)
            avg_energy_per_freq = avg_energy_per_freq**0.5

            for i in range(ind_start, ind_end):
                magnitude_spec[i] = magnitude_spec[i] if magnitude_spec[i] > avg_energy_per_freq * white_noise_thres else 0

        mag_spec_ipol = np.interp(np.arange(0, len(magnitude_spec), 1 / hps_iterations), np.arange(0, len(magnitude_spec)), magnitude_spec)
        mag_spec_ipol = mag_spec_ipol / np.linalg.norm(mag_spec_ipol, ord=2)

        hps_spec = copy.deepcopy(mag_spec_ipol)

        for i in range(hps_iterations):
            tmp_hps_spec = np.multiply(hps_spec[: int(np.ceil(len(mag_spec_ipol) / (i + 1)))], mag_spec_ipol[:: (i + 1)])
            if not any(tmp_hps_spec):
                break
            hps_spec = tmp_hps_spec

        max_ind = np.argmax(hps_spec)
        max_freq = max_ind * (sampling_rate / analysis_window_size) / hps_iterations

        closest_note, closest_pitch, index = find_closest_note(max_freq)

        if closest_note == random_note:
            if callback.last_printed_note != closest_note:
                os.system("cls" if os.name == "nt" else "clear")
                print(f"Great job! You played {closest_note}.")
                callback.last_printed_note = closest_note
                generate_random_note()
        elif callback.last_printed_note != closest_note:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"You played {closest_note}, but we're expecting {random_note}. Try again!")
            callback.last_printed_note = closest_note

    else:
        print("no input")

try:
    print("Starting Harmonic Product Spectrum Tuner ...")
    with sd.InputStream(channels=1, callback=callback, blocksize=window_step, samplerate=sampling_rate):
        while True:
            time.sleep(0.1)
except Exception as e:
    print(str(e))
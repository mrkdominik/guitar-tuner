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



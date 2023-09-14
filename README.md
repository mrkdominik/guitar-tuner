# Guitar Tuner 🎸♯
This program provides a real-time audio pitch detection capabilities using both the Discrete Fourier transform and the Harmonic Product Spectrum method. It analyzes audio input from your microphone and displays the closest musical note along with the corresponding pitch.

## Prerequisites 🥁
Before you start, ensure you have the following libraries installed:

* sounddevice
* numpy
* scipy
* tkinter (optional for a graphical user interface)

You can install these libraries using:
```
pip install sounddevice numpy scipy
```
## Usage 🎹
1. Clone the repository or download the files DFT_tuner.py and HPS_tuner.py.
2. Run the script:
```
python3 DFT_tuner.py
```
or 
```
python3 HPS_tuner.py
```

1. Play a musical note or sound into your microphone.
2. The application will display the closest musical note and your note pitch vs the closest standard note pitch in the terminal.

## How it works? 🎺
* [Discrete Fourier Transform](https://en.wikipedia.org/wiki/Discrete_Fourier_transform)
  1. The application captures audio input and processes the data in chunks.
  2. A DFT is applied to extract the magnitude spectrum and determine the peak frequency.
  3. The closest musical note is calculated based on the detected pitch.
* [Harmonic Product Spectrum](http://musicweb.ucsd.edu/~trsmyth/analysis/Harmonic_Product_Spectrum.html)
  1. Similar to the DFT-based method, but with additional steps:
  2. The magnitude spectrum undergoes multiple interpolations to increase its resolution. 
  3. HPS is applied to the interpolated spectrum to identify the fundamental frequency even in noisy signals.
  4. The closest musical note is calculated based on the detected pitch.
 

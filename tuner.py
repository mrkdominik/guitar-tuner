import numpy as np 

concert_pitch = 440
all_notes = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]


def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch/concert_pitch))*12)
    closest_note = all_notes[i%12] + str(4+ (i+9) // 12)
    closest_pitch = concert_pitch*2**(i/12)
    return closest_note, closest_pitch
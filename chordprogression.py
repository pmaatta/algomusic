import random
import warnings
from patterns import Scale


# TODO: class vs function?
# TODO: mutate progression
    # easier with class
# TODO: return chord names
# TODO: same vs different voicing / chord type for all chords
# TODO: scale degree not in scale
# TODO: chord type not in scale
# TODO: handle locrian / phrygian scale degrees
# TODO: other scales
# TODO: comments


def generate_chord_progression(scale, length=8, voicing=None):
    """
    Generate a chord progression based on a given scale. 
    
    All the chords have the same structure/voicing and contain only notes in the scale. 
    Intervals other than the first and fifth are filtered out of low notes.

    Args:
        scale: Scale              Scale of the progression.
        length: int               Length of the progression (number of chords).
        voicing: str/list(int)    Structure of all chords in the progression in zero-based 
                                  scale degrees. Randomly chosen from basic_voicings (*) if not 
                                  given. If given must be a key or value in basic_voicings or
                                  a list of ints in range(scale_length).
    Returns:
        chord_progression_notes: list(list(int))  A list containing a list of notes for each chord.
    """

    if scale.scale_type_name != 'major':
        warnings.warn('voicings do not correspond to scale degrees properly with non-diatonic scales')

    basic_voicings = {
        'triad':    [0, 2, 4],
        'seventh':  [0, 2, 4, 6],
        'ninth':    [0, 2, 4, 6, 8],
        'sixth':    [0, 2, 4, 5],
        'sus4':     [0, 3, 4],
        'sus2':     [0, 1, 4],
        '7sus4':    [0, 3, 4, 6],
        'add9':     [0, 2, 4, 8],
        'fifth':    [0, 4]
    }

    scale_length = len(scale.scale_type)
    scale_degrees = random.choices(range(scale_length), k=length)

    if voicing is None: # (*)
        voicing = basic_voicings['seventh']
        # voicing = random.choice(list(basic_voicings.values()))
    else:
        if voicing in basic_voicings:
            voicing = basic_voicings[voicing]
        elif voicing in list(basic_voicings.values()):
            pass
        else:
            assert all([isinstance(note, int) for note in voicing]), 'bad value for voicing'
            assert all([(note in range(scale_length)) for note in voicing]), 'bad value for voicing'

    chord_progression_notes = []

    for scale_degree in scale_degrees:

        voicings = voicing * 8
        all_chord_idxs = []
        for octave in range(8):
            all_chord_idxs.extend([note + scale_length*octave for note in voicing])

        scale_idxs = range(len(scale.all_scale_notes))
        scale_degree_note = (scale.key + scale.mode[scale_degree]) % 12
        scale_degree_first_idx = [x % 12 for x in scale.all_scale_notes].index(scale_degree_note)
        offset_idxs = [i - scale_degree_first_idx for i in scale_idxs]
        offset_chord_idxs = [offset_idxs.index(note) for note in all_chord_idxs if note in offset_idxs]

        all_chord_notes = []
        for i, idx in enumerate(offset_chord_idxs):
            note = scale.all_scale_notes[idx]
            if note < 40:
                if voicings[i] == 0:
                    all_chord_notes.append(note)
            elif note < 50:
                if voicings[i] in [0, 4]:
                    all_chord_notes.append(note)
            else:
                all_chord_notes.append(note)

        chord_progression_notes.append(all_chord_notes)

    return chord_progression_notes


if __name__ == "__main__":
    
    some_scale = Scale(scale_type_name='major', mode_idx=0)
    chord_progression_notes = generate_chord_progression(some_scale)

    print(some_scale.key_name)
    for notes in chord_progression_notes:
        notes_mod12 = [note % 12 for note in notes]
        note_names = [Scale.note_names[note] for note in notes_mod12]
        print(note_names)




# class ChordProgression:

#     basic_voicings = {
#         'triad':    [0, 2, 4],
#         'seventh':  [0, 2, 4, 6],
#         'ninth':    [0, 2, 4, 6, 8],
#         'sixth':    [0, 2, 4, 5],
#         'sus4':     [0, 3, 4],
#         'sus2':     [0, 1, 4],
#         '7sus4':    [0, 3, 4, 6],
#         'add9':     [0, 2, 4, 8],
#         'fifth':    [0, 4]
#     }

#     def __init__(self, scale, progression_length=4):
#         self.scale = scale
#         self.progression_length = progression_length
#         self.chord_progression_notes = self.generate_progression()

#     def generate_progression(self):
#         if self.scale.scale_type_name != 'major':
#             raise NotImplementedError

#         scale_length = len(self.scale.scale_type)
#         scale_degrees = random.choices(range(scale_length), k=self.progression_length)
#         # voicing = random.choice(list(self.basic_voicings.values()))
#         voicing = self.basic_voicings['seventh']

#         chord_progression_notes = []

#         for scale_degree in scale_degrees:

#             voicings = voicing * 8
#             all_chord_idxs = []
#             for octave in range(8):
#                 all_chord_idxs.extend([note + scale_length*octave for note in voicing])

#             scale_idxs = range(len(self.scale.all_scale_notes))
#             scale_degree_note = (self.scale.key + self.scale.mode[scale_degree]) % 12
#             scale_degree_first_idx = [x % 12 for x in self.scale.all_scale_notes].index(scale_degree_note)
#             # all_scale_note_names = [Scale.note_names[(note % 12)] for note in self.scale.all_scale_notes]

#             offset_idxs = [i - scale_degree_first_idx for i in scale_idxs]
#             offset_chord_idxs = [offset_idxs.index(note) for note in all_chord_idxs if note in offset_idxs]

#             all_chord_notes = []
#             for i, idx in enumerate(offset_chord_idxs):
#                 note = self.scale.all_scale_notes[idx]
#                 # following works for 7-note scale only (with perfect 5th)
#                 if note < 40:
#                     if voicings[i] == 0:
#                         all_chord_notes.append(note)
#                 elif note < 50:
#                     if voicings[i] in [0, 4]:
#                         all_chord_notes.append(note)
#                 else:
#                     all_chord_notes.append(note)

#             chord_progression_notes.append(all_chord_notes)

#         return chord_progression_notes



# some_scale = Scale(scale_type_name='major', mode_idx=0)
# cp = ChordProgression(some_scale)

# print(some_scale.key_name)
# for notes in cp.chord_progression_notes:
#     notes_mod12 = [note % 12 for note in notes]
#     note_names = [Scale.note_names[note] for note in notes_mod12]
#     print(note_names)








# some_scale = Scale(scale_type_name='major', mode_idx=0)
# scale_length = len(some_scale.scale_type)
# scale_degree = 3
# voicing = [0, 2, 4, 6] 
# voicings = voicing * 8
# # chord = [note + scale_degree for note in voicing]
# all_chord_idxs = []
# for octave in range(8):
#     all_chord_idxs.extend([note + scale_length*octave for note in voicing])
#     # all_chord_idxs.extend([note + scale_length*octave for note in chord])

# scale_idxs = range(len(some_scale.all_scale_notes))
# # key_first_idx = [x % 12 for x in some_scale.all_scale_notes].index(some_scale.key)
# scale_degree_note = (some_scale.key + some_scale.mode[scale_degree]) % 12
# scale_degree_first_idx = [x % 12 for x in some_scale.all_scale_notes].index(scale_degree_note)
# all_scale_note_names = [Scale.note_names[(note % 12)] for note in some_scale.all_scale_notes]

# # print(some_scale.mode[scale_degree])
# print()
# print('Key:', some_scale.key_name)
# print(some_scale.mode_name, some_scale.names) 
# print('(zero-based) scale degree: ', scale_degree)
# print('Scale degree note:', scale_degree_note, Scale.note_names[scale_degree_note % 12])
# print('First index of scale degree note in all notes:', scale_degree_first_idx)
# print(some_scale.all_scale_notes)
# print(all_scale_note_names)
# # print(list(scale_idxs))
# # print(key_first_idx)
# # print(some_scale.mode)
# # print([x % 12 for x in some_scale.all_scale_notes])
# # print([x - some_scale.key for x in some_scale.all_scale_notes])


# print('Offset indices (zero at first occurrence of scale degree)')
# offset_idxs = [i - scale_degree_first_idx for i in scale_idxs]
# # offset_idxs = [i - key_first_idx for i in scale_idxs]
# print(offset_idxs)

# print('Chord voicing indices')
# print(all_chord_idxs)

# print('Offset chord voicing indices')
# offset_chord_idxs = [offset_idxs.index(note) for note in all_chord_idxs if note in offset_idxs]
# print(offset_chord_idxs)

# print('Voicings')
# print(voicings)

# print('All chord notes')
# # all_chord_notes = sorted([some_scale.all_scale_notes[i] for i in offset_chord_idxs])
# all_chord_notes = []
# for i, idx in enumerate(offset_chord_idxs):
#     note = some_scale.all_scale_notes[idx]
#     # following works for 7-note scale only (with perfect 5th)
#     if note < 40:
#         if voicings[i] == 0:
#             all_chord_notes.append(note)
#     elif note < 50:
#         if voicings[i] in [0, 4]:
#             all_chord_notes.append(note)
#     else:
#         all_chord_notes.append(note)


# print(all_chord_notes)

# print('Chord note names')
# all_chord_notes_mod12 = [note % 12 for note in all_chord_notes]
# chord_note_names = [Scale.note_names[note] for note in all_chord_notes_mod12]
# print(chord_note_names)

# print()

# # parameters:
# # limit high notes to upper structure (no 1 or 3)
# # limit low notes to 1 and 5 (+3)


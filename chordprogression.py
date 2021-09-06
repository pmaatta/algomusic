import random
import warnings
from music.patterns import Scale


class ChordProgression:
    """
    Generate a chord progression based on a given scale. 
    
    All the chords contain only notes in the scale. If the parameter 'voicing' is 
    given, all the chords have that particular voicing. Intervals other than the 
    first and fifth are filtered out of low notes.

    scale: Scale              Scale of the progression.

    length: int               Length of the progression (number of chords).

    scale_length: int         Number of notes in the scale.

    scale_degrees: list(int)  List of the scale degrees (root notes) of the progression.

    voicing: str/list(int)    If given, determines the structure of all chords in the progression,
                              in zero-based scale degrees. Must be a key or value in basic_voicings or
                              a list of ints in range(scale_length). If not given, all chords have a
                              separate randomly chosen voicing.

    voicing_list: list(list(int))  List of voicings for each chord in the progression.

    chord_progression_notes: list(list(int))  A list containing a list of allowed notes for each chord.

    allow_outside: bool       Whether to allow chords in the progression that are based on notes 
                              outside of the given scale.

    """
    
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

    def __init__(self, scale, length=8, voicing=None, allow_outside=None):

        if scale.scale_type_name != 'major':
            warnings.warn('voicings do not correspond to scale degrees properly with non-diatonic scales')
        
        self.scale = scale
        self.length = length
        self.scale_length = len(self.scale.scale_type)
        self.scale_degrees = random.choices(range(self.scale_length), k=length)
        self.voicing_list = None
        self.chord_progression_notes = None

        if allow_outside is not None:
            raise NotImplementedError
        # self.allow_outside = allow_outside if allow_outside is not None else random.choice([True, False])

        if voicing is None: 
            self.voicing_list = [random.choice(list(self.basic_voicings.values())) for _ in range(self.length)]
        else:
            if voicing in self.basic_voicings:
                voicing = self.basic_voicings[voicing]
            elif voicing in list(self.basic_voicings.values()):
                pass
            else:
                assert all([isinstance(note, int) for note in voicing]), 'bad value for voicing'
                assert all([(note in range(self.scale_length)) for note in voicing]), 'bad value for voicing'
            self.voicing_list = [voicing for _ in range(self.length)]


        chord_progression_notes = []

        for scale_degree, current_voicing in zip(self.scale_degrees, self.voicing_list):

            voicings = current_voicing * 8
            all_chord_idxs = []
            for octave in range(8):
                all_chord_idxs.extend([note + self.scale_length*octave for note in current_voicing])

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

        self.chord_progression_notes = chord_progression_notes



def generate_chord_progression(scale, length=8, voicing=None, allow_outside=None):
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
        allow_outside: bool       Whether to allow chords in the progression that are based on notes 
                                  outside of the given scale.

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

    if allow_outside is None:
        allow_outside = random.choice([True, False])

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

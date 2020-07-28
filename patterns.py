import random
from numpy import exp
from scipy.stats import norm
from abc import ABC, abstractmethod


# TODO: percussionsingle
# TODO: better durations
# TODO: class "Song" for song generation handling
    # chords, chord progressions, arpeggios, chord tones for melodies, pedal point for bass, ...
    # modulate given pattern
# TODO: type checking (at user level), default values, None
# TODO: docs for argument types
# TODO: docs for class attributes
# TODO: docs for patterns if not self-explanatory
# TODO: input Scale instance into Pattern to get mode center
# TODO: drums vs percs
    # too sparse rhythm
    # percussion subpatterns
# TODO: randomize length, repeat at user input level
# TODO: chords as scales
# TODO: pattern interaction
# TODO: sample_notes bass option cleanup
# TODO: modulate / diatonic_modulate
    # ------- cleanup & bugfix --------
    # modulate called -> update key, scale & write to parameters.txt
# TODO: mutations:
    # new class?
    # streching / squeezing time
    # single (/multiple) note shift (pitch)
    # single (/multiple) note shift (time)
    # displace / rotate rhythm
    # add notes
    # drop notes


class Scale:
    """
    Create random scale and filter notes in range 0-127 accordingly.

    Attributes:
        key: int
        scale_type_name: str
        key_name: str
        scale_type: list[int]
        mode: list[int]
        mode_name: str
        names: list[str]
        all_scale_notes: list[int]
    """

    scale_types = {
        'major':                [0, 2, 4, 5, 7, 9, 11],
        'pentatonic':           [0, 3, 5, 7, 10],
        'major_no4':            [0, 2, 4, 7, 9, 11],
        'major_no7':            [0, 2, 4, 5, 7, 9],
        'maj':                  [0, 4, 7],
        'maj6':                 [0, 4, 7, 9],
        'maj7':                 [0, 4, 7, 11],
        'blues':                [0, 3, 5, 6, 7, 10],
        'melodic_minor':        [0, 2, 3, 5, 7, 9, 11],
        'harmonic_minor':       [0, 2, 3, 5, 7, 8, 11],
        'harmonic_major':       [0, 2, 4, 5, 7, 8, 11],
        'dominant_diminished':  [0, 1, 3, 4, 6, 7, 9, 10],
        'wholetone':            [0, 2, 4, 6, 8, 10],
        'chromatic':            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]    
    }

    note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    major_mode_names = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']

    def __init__(self, key=None, scale_type_name=None, mode_idx=None, limit_range=True):

        # Choose random key
        self.key = key if key is not None else random.randint(0, 11)
        self.key_name = Scale.note_names[self.key]

        # Choose random scale type
        if scale_type_name is None:
            scale_type_name, scale_type = random.choice(list(Scale.scale_types.items()))
        else:
            scale_type = Scale.scale_types[scale_type_name]
        self.scale_type_name = scale_type_name
        self.scale_type = scale_type

        # Choose random mode
        if mode_idx is None:
            mode_idx = random.randint(0, len(scale_type) - 1)
        mode = sorted([(note - scale_type[mode_idx]) % 12 for note in scale_type])
        self.mode = mode
        if scale_type_name == 'major':
            self.mode_name = Scale.major_mode_names[mode_idx]
        else:
            self.mode_name = str(mode_idx)

        # Create scale and determine all notes in the available range 0-127
        # belonging to the chosen scale (optionally limit note range to B0...C7 (scientific))
        scale = [(note + self.key) % 12 for note in mode]
        self.names = [Scale.note_names[note] for note in scale]
        if limit_range:
            self.all_scale_notes = [i for i in range(23, 97) if (i % 12) in scale]
        else:
            self.all_scale_notes = [i for i in range(128) if (i % 12) in scale]


class Pattern(ABC):
    """
    Abstract base class for creating a random (1/4th) note pattern.
    """
    def __init__(self, key, scale, length=None, repeat=None):
        self.key = key
        self.scale = scale
        self.allowed_range = range(23,97)
        self.length = length if length is not None else random.randint(1, 16)
        self.repeat = repeat if repeat is not None else random.randint(2, 8)
        self.total_length = self.length * self.repeat
        self.note_amount = None
        self.notes = None
        self.start_times = None
        self.durations = None
        self.volumes = None
        self.root_note = None
        self.percussion_pattern_types = [PercussionSingle, BassDrum, Snare, Cymbals, AccentCymbals]

    @abstractmethod
    def generate_rhythm(self):
        """
        Generate random rhythm pattern based on instrument role.
        """
        pass

    @abstractmethod
    def generate_melody(self):
        """
        Generate random melodic pattern based on instrument role.
        """
        pass

    def generate_volumes(self):
        """
        Choose random volume for each note and limit the volumes of high notes.
        """
        assert self.notes is not None, 'generate_rhythm and generate_melody must be called first'
        volumes = random.choices(range(70,110), k=self.note_amount*self.repeat)
        if self.__class__ not in (self.percussion_pattern_types + [Percussion]):
            for i, note in enumerate(self.notes):
                if note > 72 and volumes[i] > 70:
                    volumes[i] = 70
        self.volumes = volumes

    def initialize(self):
        """
        Initialize pattern by generating rhythm, pitch and volume information.
        """
        self.generate_rhythm()
        self.generate_melody()
        self.generate_volumes()

    def repeat_rhythm(self, start_times, durations):
        """
        Helper function for repeating the created rhythm.
        """
        start_times_repeat = []
        for i in range(self.repeat):
            for s in start_times:
                start_times_repeat.append(s + i*self.length)
        self.start_times = start_times_repeat
        self.durations = durations * self.repeat
    
    def regenerate_rhythm(self):
        """
        Regenerate rhythm pattern when it has already been generated.
        """
        assert self.start_times is not None, 'Pattern has not been initialized'
        running_length = (self.start_times[0] // self.total_length) * self.total_length
        self.generate_rhythm()
        self.start_times = [x + running_length for x in self.start_times]

    def reverse_melody(self):
        """
        Reverse generated pitches.
        """
        assert self.notes is not None, 'Pattern has not been initialized'
        self.notes = list(reversed(self.notes))

    def invert(self):
        """
        Invert intervals in self.notes relative to a random reference pitch in self.notes.
        Does nothing if at least one inverted note ends up out of the allowed range. 
        """
        assert self.notes is not None, 'Pattern has not been initialized'
        if self.__class__  in (self.percussion_pattern_types + [Percussion]):
            return True, self.notes

        scale_idxs = range(len(self.scale))
        ref_pitch = random.choice(scale_idxs)
        idxs = [self.scale.index(x) for x in self.notes]
        inversion_idxs = [(2*ref_pitch - i) for i in idxs if (2*ref_pitch - i) in scale_idxs]
        inversion = [self.scale[i] for i in inversion_idxs if self.scale[i] in self.allowed_range]
        if len(inversion) == len(self.notes):
            return True, inversion
        else:
            return False, self.notes

    # TODO: how to change self.scale
    def modulate(self, shift):
        """
        Modulate all notes of self.notes by 'shift' amount of semitones. 
        
        Does nothing if at least one modulated note ends up out of the allowed range. 
        Shift may be positive or negative. 
        """
        if self.__class__  in (self.percussion_pattern_types + [Percussion]):
            return True, self.notes, self.key, self.scale
        
        new_notes = [note + shift for note in self.notes if note + shift in self.allowed_range]
        if len(new_notes) == len(self.notes):
            new_key = (self.key + shift) % 12
            new_scale = [note + shift for note in self.scale]
            return True, new_notes, new_key, new_scale
        else:
            return False, self.notes, self.key, self.scale

    # TODO: allowed range (self.scale vs ?)
    def diatonic_modulate(self, shift):
        """
        Modulate all notes of self.notes by 'shift' amount of steps in the scale. 
        
        The new notes belong to self.scale. Does nothing if at least one modulated 
        note ends up out of the allowed range. Shift may be positive or negative.
        """
        if self.__class__  in (self.percussion_pattern_types + [Percussion]):
            return True, self.notes

        idxs = [self.scale.index(x) for x in self.notes]
        new_idxs = [i + shift for i in idxs if i + shift in range(len(self.scale))]
        if len(new_idxs) == len(idxs):
            new_notes = [self.scale[i] for i in new_idxs]
            return True, new_notes
        else:
            return False, self.notes

    def sample_notes(self, note_amount, all_notes, std_dev=6):
        """
        Sample note_amount notes from all_notes using a gaussian jumping distribution
        centered on the previous note.
        """
        notes = [random.choice(all_notes)]
        for _ in range(note_amount - 1):
            N = norm(notes[-1], std_dev)
            W = [N.pdf(x) for x in all_notes]
            notes.append(random.choices(all_notes, weights=W, k=1)[0])
        return notes
   
    def sample_arpeggio_notes(self, all_notes, root_note):
        """
        Sample notes from an arpeggio-type note distribution.
        
        TODO (notes rising in thirds from the root note).
        """
        while root_note not in all_notes:
            root_note += 12
            if root_note > 127:
                root_note = root_note % 12
        idx = all_notes.index(root_note)
        all_notes = all_notes[idx::2]
        notes = random.choices(all_notes, k=self.note_amount)
        return notes


# TODO: make abstract / deprecate
class Percussion(Pattern):
    """
    Generic percussion type pattern (no drum kit sounds). Each note in the pattern 
    is potentially a different sound/instrument.
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        default_note_amount = random.randint(self.length, 2*self.length)
        self.note_amount = note_amount if note_amount is not None else default_note_amount

    def generate_rhythm(self):
        start_times = sorted(random.choices(range(self.length), k=self.note_amount))
        durations = [1] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        allowed_range = range(60, 71)
        self.notes = random.choices(allowed_range, k=self.note_amount) * self.repeat


class PercussionSingle(Percussion):
    """
    Generic percussion type pattern (no drum kit sounds). Each note in the pattern 
    is the same sound/instrument.
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        default_note_amount = random.randint(1, self.length)
        self.note_amount = note_amount if note_amount is not None else default_note_amount
    
    def generate_melody(self):
        allowed_range = range(60, 71)
        self.notes = random.choices(allowed_range, k=1) * self.note_amount * self.repeat


class BassDrum(PercussionSingle):
    """
    Bass drum pattern. Rhythm heavily weighted on quarter notes (TODO).
    """
    def generate_rhythm(self):
        w = []
        for i in range(self.length):
            if i % 4 == 0:
                w.append(5)
            else:
                w.append(1)
        start_times = sorted(random.choices(range(self.length), k=self.note_amount, weights=w))
        durations = [1] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        self.notes = [35] * self.note_amount * self.repeat


class Snare(Pattern):
    """
    Snare drum pattern. Rhythm heavily weighted on quarter notes 2 and 4 (where applicable).
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        default_note_amount = random.randint(1, self.length // 2)
        self.note_amount = note_amount if note_amount is not None else default_note_amount

    def generate_rhythm(self):
        w = []
        for i in range(self.length):
            if i % 8 == 4:
                w.append(10)
            else:
                w.append(1)
        start_times = sorted(random.choices(range(self.length), k=self.note_amount, weights=w))
        durations = [1] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        self.notes = [40] * self.note_amount * self.repeat


class Cymbals(PercussionSingle):
    """
    Cymbal pattern with no accent/crash cymbals. Each note in the pattern is the same sound/instrument.
    """
    def generate_melody(self):
        allowed_range = [42,44,46,51,53,59]
        self.notes = random.choices(allowed_range, k=1) * self.note_amount * self.repeat


class AccentCymbals(Pattern):
    """
    Accent (crash) cymbal pattern. Each note in the pattern is the same sound/instrument. Only plays
    1 note per repeat (alternatively 1 note per all repeats) in the beginning of the pattern.
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None, play_each_repeat=False):
        super().__init__(key, scale, length, repeat)
        self.note_amount = 1
        self.allowed_range = [49,52,55,57]
        self.play_each_repeat = play_each_repeat

    def generate_rhythm(self):
        self.start_times = [0]
        self.durations = [1]
        if self.play_each_repeat:
            self.repeat_rhythm(self.start_times, self.durations)

    def generate_melody(self):
        self.notes = random.choices(self.allowed_range, k=1) * self.note_amount
        if self.play_each_repeat:
            self.notes = self.notes * self.repeat


class Bass(Pattern):
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        # Low amount of notes more likely
        L = list(range(1, self.length+1))
        W = [exp(-x) for x in L]
        default_note_amount = random.choices(L, weights=W, k=1)[0]
        self.note_amount = note_amount if note_amount is not None else default_note_amount
        self.allowed_range = range(23, 49)
    
    def generate_rhythm(self):
        # Sustained notes
        start_times = sorted(random.sample(range(self.length), self.note_amount))
        durations = [0] * self.note_amount
        for i in range(self.note_amount - 1):
            durations[i] = start_times[i+1] - start_times[i]
        durations[-1] = self.length - start_times[-1]
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        all_notes = [x for x in self.scale if x <= 48]
        self.notes = self.sample_notes(self.repeat, all_notes) * self.note_amount


class SimpleBass(Pattern):
    """
    Plays one note that is the length of the pattern and that is the same for all repeats.
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        self.allowed_range = range(23, 49)
        self.note_amount = 1

    def generate_rhythm(self):
        start_times = [0]
        durations = [self.length]
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        all_notes = [x for x in self.scale if x <= 48]
        self.notes = self.sample_notes(self.repeat, all_notes) * self.note_amount


class SimpleBass2(SimpleBass):
    """
    Plays one note that is the length of the pattern and that may change for repeats.
    """
    def generate_melody(self):
        all_notes = [x for x in self.scale if x <= 48]
        self.notes = self.sample_notes(self.note_amount, all_notes) * self.repeat


class SimpleBass3(Bass):
    """
    Plays the key/mode center only.
    """
    def generate_melody(self):
        all_notes = [x for x in self.scale if x <= 48 and x%12 == self.key]
        self.notes = self.sample_notes(self.repeat, all_notes) * self.note_amount


class Melodic(Pattern, ABC):
    """
    Abstract base class for melody type patterns.
    """
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None):
        super().__init__(key, scale, length, repeat)
        default_note_amount = random.randint(1, self.length)
        self.note_amount = note_amount if note_amount is not None else default_note_amount
        self.allowed_range = range(36, 97)

    def generate_rhythm(self):
        start_times = sorted(random.sample(range(self.length), self.note_amount))
        durations = [1] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self, note_range):
        all_notes = [x for x in self.scale if x in note_range]
        self.notes = self.sample_notes(self.note_amount, all_notes) * self.repeat


class LowMelodic(Melodic):
    def generate_melody(self):
        allowed_notes = range(self.key + 36, self.key + 61)
        super().generate_melody(allowed_notes)


class MidMelodic(Melodic):
    def generate_melody(self):
        allowed_notes = range(self.key + 48, self.key + 73)
        super().generate_melody(allowed_notes)


class HighMelodic(Melodic):
    def generate_melody(self):
        allowed_notes = range(self.key + 60, self.key + 85)
        super().generate_melody(allowed_notes)


class Harmonic(Pattern):
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None, root_note=None):
        super().__init__(key, scale, length, repeat)
        default_root_note = random.choice(self.scale) % 12
        default_note_amount = random.randint(3, 6)
        self.root_note = root_note if root_note is not None else default_root_note
        self.note_amount = note_amount if note_amount is not None else default_note_amount
        self.allowed_range = range(48, 85)

    def generate_rhythm(self):
        start_times = [0] * self.note_amount
        durations = [self.length] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        all_notes = [x for x in self.scale if self.key + 48 <= x <= self.key + 72]
        self.notes = self.sample_arpeggio_notes(all_notes, self.root_note) * self.repeat


class Arpeggio(Pattern):
    def __init__(self, key, scale, length=None, repeat=None, note_amount=None, root_note=None):
        super().__init__(key, scale, length, repeat)
        default_root_note = random.choice(self.scale) % 12
        default_note_amount = self.length
        self.root_note = root_note if root_note is not None else default_root_note
        self.note_amount = note_amount if note_amount is not None else default_note_amount
        self.allowed_range = range(36, 85)

    def generate_rhythm(self):
        start_times = list(range(self.length))
        durations = [1] * self.note_amount
        self.repeat_rhythm(start_times, durations)

    def generate_melody(self):
        all_notes = [x for x in self.scale if self.key + 36 <= x <= self.key + 72]
        self.notes = self.sample_arpeggio_notes(all_notes, self.root_note) * self.repeat





    # def sample_notes(self, note_amount, all_notes, bass=False, std_dev=6):
    #     """
    #     Sample note_amount notes from all_notes using a gaussian jumping distribution.
    #     """
    #     notes = []
    #     for i in range(note_amount):
    #         if i == 0:
    #             # First note key center weighted more if instrument role is bass
    #             W = []
    #             for n in all_notes:
    #                 if bass and n % 12 == self.key:
    #                     W.append(3)
    #                 else:
    #                     W.append(1)
    #             notes.append(random.choices(all_notes, weights=W, k=1)[0])
    #         else:
    #             # Gaussian jumping distribution centered on previous note
    #             # Standard deviation can be tuned
    #             N = norm(notes[-1], std_dev)  
    #             W = [N.pdf(x) for x in all_notes]
    #             notes.append(random.choices(all_notes, weights=W, k=1)[0])
    #     return notes

    # def sample_notes(self, note_amount, all_notes, std_dev=6):
    #     # First note key center weighted more
    #     notes = []
    #     for i in range(note_amount):
    #         if i == 0:
    #             W = []
    #             for n in all_notes:
    #                 if n % 12 == self.key:
    #                     W.append(3)
    #                 else:
    #                     W.append(1)
    #             notes.append(random.choices(all_notes, weights=W, k=1)[0])
    #         else:
    #             N = norm(notes[-1], std_dev)  
    #             W = [N.pdf(x) for x in all_notes]
    #             notes.append(random.choices(all_notes, weights=W, k=1)[0])
    #     return notes
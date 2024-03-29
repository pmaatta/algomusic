import os
import sys
import random
import argparse
from itertools import groupby

from midiutil import MIDIFile
from music.chordprogression import generate_chord_progression
from music.patterns import (
    Scale, Pattern, Bass, SimpleBass, SimpleBass2, SimpleBass3, Harmonic, 
    Arpeggio, LowMelodic, MidMelodic, HighMelodic, PercussionSingle, BassDrum,
    Snare, Cymbals, AccentCymbals, ChordProgression
)


def run(arg_str_list=[], filepath='midis/test.mid'):


    #=====================================================================#
    #                     Parse command line arguments                    #
    #=====================================================================#


    parser = argparse.ArgumentParser(
        description='Create midi file of algorithmically generated music.'
    )

    # Allowed ranges when chosen manually
    tempo_range = range(10, 1200)
    length_range = range(2, 1000)
    repeat_range = range(1, 1000)
    pattern_range = range(1, 100)

    # Allowed ranges when randomized (input 0)
    random_tempo_min = 60
    random_tempo_max = 300
    random_length_min = 3
    random_length_max = 32
    random_repeat_choices = list(range(2, 18, 2))

    parser.add_argument('-s', '--seed', default=None, help='random seed', metavar='')
    parser.add_argument('-c', '--scale', default='major', choices=Scale.scale_types.keys(), help='scale type shared by patterns', metavar='')
    parser.add_argument('-m', '--mode', type=int, default=0, choices=range(12), help='mode index in range(12)', metavar='')
    parser.add_argument('-k', '--key', type=int, default=None, choices=range(12), help='key center in range(12)', metavar='')
    parser.add_argument('-l', '--length', type=int, default=8, help=f'pattern length in {length_range} (0 = random)', metavar='')
    parser.add_argument('-r', '--repeat', type=int, default=4, help=f'pattern repeat amount in {repeat_range} (0 = random)', metavar='')
    parser.add_argument('-t', '--tempo', type=int, default=90, help=f'song tempo in {tempo_range} (0 = random)', metavar='')
    parser.add_argument('-n', '--numtracks', type=int, default=16, choices=range(1, 21), help='number of tracks in range(1, 9)', metavar='')
    parser.add_argument('-p', '--numpatterns', type=int, default=16, help=f'number of patterns in {pattern_range}', metavar='')
    parser.add_argument('-v', '--voicing', type=str, default=None, choices=ChordProgression.basic_voicings.keys(), help=f'type of the chords in the chord progression', metavar='')
    parser.add_argument('-lt', '--limittracks', type=int, default=1, choices=[1,0], help=f'whether to limit number of tracks per pattern type', metavar='')
    parser.add_argument('-ar', '--arpeggio', type=int, default=1, choices=[1,0], help=f'whether to allow arpeggio pattern type', metavar='')
    parser.add_argument('-nc', '--nicescales', type=int, default=1, choices=[1,0], help=f'whether to use "nice" or "spicy" scales', metavar='')
    parser.add_argument('-cpl', '--chordproglen', type=int, default=4, choices=range(1,33), help=f'length of chord progression', metavar='')
    parser.add_argument('-gen', '--gentype', type=int, default=4, choices=[1,2,3,4], help=f'music generation type', metavar='')
    parser.add_argument('-all', '--allpatterns', type=int, default=0, choices=[1,0], help=f'whether to use all patterns in available_patterns', metavar='')
    parser.add_argument('-rig', '--rigidity', type=float, default=0.8, help=f'controls how strictly the drum patterns follow a basic backbeat', metavar='')


    args = parser.parse_args(arg_str_list)

    random.seed(args.seed)

    if args.length not in length_range:
        parser.error(f'length is not in {length_range}')
    if args.length == 0:
        args.length = random.randint(random_length_min, random_length_max)

    if args.repeat not in repeat_range:
        parser.error(f'repeat is not in {repeat_range}')
    if args.repeat == 0:
        args.repeat = random.choice(random_repeat_choices)

    if args.tempo not in tempo_range:
        parser.error(f'tempo is not in {tempo_range}')
    if args.tempo == 0:
        args.tempo = random.randint(random_tempo_min, random_tempo_max)

    if args.numpatterns not in pattern_range:
        parser.error(f'number of patterns is not in {pattern_range}')

    if args.scale is None and args.mode is not None:
        parser.error('mode given but scale type not given')

    if args.scale is not None and args.mode is not None:
        valid_mode_range = range(len(Scale.scale_types[args.scale]))
        if args.mode not in valid_mode_range:
            parser.error(f'invalid mode index for chosen scale type ({args.scale}: {valid_mode_range})')

    if args.rigidity < 0.0 or args.rigidity > 1.0:
        parser.error('rigidity must be between 0.0 and 1.0')

    if args.allpatterns:
        args.numtracks = 16



    #=====================================================================#
    #                 Create MIDI file, define parameters                 #
    #=====================================================================#


    midi_file = MIDIFile(args.numtracks)

    for track in range(args.numtracks):
        midi_file.addTempo(track, time=0, tempo=args.tempo * 4)   # TODO

    store_info = False

    # file number, storing parameters
    if store_info:

        # Get latest number from test midi file names
        def split_numeric(s):
            for _, g in groupby(s, str.isalpha):
                yield ''.join(g)
                
        midis = [x for x in sorted(os.listdir('../midis')) if x.endswith('.mid')]
        last_midi_name = midis[-1][:-4]
        if last_midi_name.endswith('+'):
            last_midi_name = last_midi_name[:-1]
        parts = list(split_numeric(last_midi_name))
        new_number = str(int(parts[-1]) + 1)

        # Keep track of options & scales and instruments used
        param_filename = '../midis/parameters' + new_number + '.txt'
        with open(param_filename, 'w+') as text_file:
            text_file.write('Options:\n')
            text_file.write('\n'.join([str(arg) for arg in vars(args).items()]))
            text_file.write('\n\n')


    instruments_used = []

    # Allowed instruments
    all_instruments = [1,8,10,11,12,15,23,35,45,46,48,49,50,51,52,62,71,72,73,74,75,76,78,79,88,89,90,102,114]
    bass_instruments = [0,33,35,48,49,50,51,62]
    arp_instruments = [90,102]

    # Patterns
    all_pattern_types = [Bass, SimpleBass, SimpleBass2, SimpleBass3, Harmonic, Arpeggio, \
                        LowMelodic, MidMelodic, HighMelodic, PercussionSingle, BassDrum, \
                        Snare, Cymbals, AccentCymbals]

    percussion_pattern_types = [PercussionSingle, BassDrum, Snare, Cymbals, AccentCymbals]

    bass_pattern_types = [Bass, SimpleBass, SimpleBass2, SimpleBass3]

    melody_pattern_types = [LowMelodic, MidMelodic, HighMelodic]

    # Max 1 bass type and 2 melody types
    bass = random.choice(bass_pattern_types)
    melodies = melody_pattern_types.copy()
    melody1 = random.choice(melodies)
    melodies.remove(melody1)
    melody2 = random.choice(melodies)

    allowed_pattern_types = [
        PercussionSingle,
        BassDrum,
        Snare,
        Cymbals,
        AccentCymbals,
        bass,
        Harmonic,
        Arpeggio,
        melody1,
        melody2
    ]

    if not args.arpeggio:
        allowed_pattern_types.remove(Arpeggio)

    # Scales
    nice_scale_types = [
        'major',
        'pentatonic',
        'major_no4',
        'major_no7'
    ]

    # Choose random scale if not given
    if args.scale is None:
        if args.nicescales:
            args.scale = random.choice(nice_scale_types)
        else:
            args.scale = random.choice(Scale.scale_types.keys())

    scale = Scale(args.key, args.scale, args.mode)
    keys_used = [Scale.note_names[scale.key]]


    def add_notes(track, channel, pattern, midi_file, repeat=0):
        """
        Add notes of a pattern to a midi file.
        """
        pattern.start_times = [x + pattern.total_length * repeat for x in pattern.start_times]
        for i in range(len(pattern.notes)):
            midi_file.addNote(track, 
                            channel,
                            pattern.notes[i],
                            pattern.start_times[i],
                            pattern.durations[i],
                            pattern.volumes[i])

    def add_info(param_filename, scale, keys_used, instruments_used, patterns):
        """
        Write scale, instrument & pattern information to text file.
        """
        with open(param_filename, 'a+') as text_file:
            text_file.write('Key(s): ' + ', '.join(keys_used) + '\n')
            text_file.write(f'Scale type: {scale.scale_type_name}\n')
            text_file.write(f'Mode: {scale.mode_name}\n\n')
            text_file.write('Instruments: {}\n'.format(' '.join(instruments_used)))
            text_file.write('Pattern types:\n')
            p_strs = [str(p.__class__).split('.')[1].split("'")[0] for _, _, p in patterns]
            text_file.write(' '.join(p_strs))



    #=====================================================================#
    #                           Generate music                            #
    #=====================================================================#


    def generate_music_1():
        """
        Generate a set of patterns based on a scale, mutate the patterns
        args.numpatterns - 1 times and write to an output midi file.
        """

        patterns = []

        for i in range(args.numpatterns):

            # Generate one set of patterns
            if i == 0:

                available_patterns = allowed_pattern_types.copy()

                for track in range(len(available_patterns)):    ##### bug
                # for track in range(args.numtracks):
                    channel = track

                    # Generate random pattern and initialize
                    pattern = random.choice(available_patterns)(
                        scale.key,
                        scale.all_scale_notes,
                        args.length,
                        args.repeat
                    )
                    pattern.initialize()
                    if args.limittracks:
                        available_patterns.remove(pattern.__class__) 

                    # Choose instrument
                    if pattern.__class__ in percussion_pattern_types:
                        channel = 9
                        instr = 0
                    elif pattern.__class__ in bass_pattern_types:
                        instr = random.choice(bass_instruments)
                    elif pattern.__class__ == Arpeggio:
                        instr = random.choice(arp_instruments)
                    else:
                        instr = random.choice(all_instruments)
                    instruments_used.append(str(instr))
                    midi_file.addProgramChange(track, channel, 0, instr)
                    
                    # Limit volumes
                    if pattern.__class__ == Harmonic:
                        pattern.volumes = [50 for x in pattern.volumes]
                    # if pattern.__class__ in percussion_pattern_types:
                    #     pattern.volumes = [50 for x in pattern.volumes]

                    patterns.append((track, channel, pattern))

                    # Add notes to MIDI file
                    for i in range(len(pattern.notes)):
                        midi_file.addNote(track, 
                                        channel,
                                        pattern.notes[i],
                                        pattern.start_times[i],
                                        pattern.durations[i],
                                        pattern.volumes[i])

            # Mutate patterns
            else:

                # Choose random mutation type
                mutation_types = [
                    'modulate',
                    'diatonic_modulate',
                    'invert',
                    'reverse_melody',
                    'regenerate_melody',
                    'regenerate_rhythm'
                ]
                mutation_weights = [1, 5, 2, 1, 1, 2]
                mutation = random.choices(mutation_types, mutation_weights, k=1)[0]

                if mutation == 'modulate':
                    modulations = []
                    successes = [False]
                    tries = 0
                    while not all(successes) and tries < 20:
                        tries += 1
                        shifts = list(range(-5, 0)) + list(range(1, 6))
                        shift = random.choice(shifts)
                        modulations = []
                        successes = []
                        for _, _, pattern in patterns:
                            success, new_notes, new_key, new_scale = pattern.modulate(shift)
                            modulations.append((new_notes, new_key, new_scale))
                            successes.append(success)
                    if all(successes):
                        new_key = modulations[0][1]
                        keys_used.append(Scale.note_names[new_key])
                        for i, (_, _, pattern) in enumerate(patterns):
                            pattern.notes = modulations[i][0]
                            pattern.key = modulations[i][1]
                            pattern.scale = modulations[i][2]
                    
                elif mutation == 'diatonic_modulate':
                    modulations = []
                    successes = [False]
                    tries = 0
                    while not all(successes) and tries < 20:
                        tries += 1
                        shifts = list(range(-4, 0)) + list(range(1, 5))
                        shift = random.choice(shifts)
                        modulations = []
                        successes = []
                        for _, _, pattern in patterns:
                            success, new_notes = pattern.diatonic_modulate(shift)
                            modulations.append(new_notes)
                            successes.append(success)
                    if all(successes):
                        for i, (_, _, pattern) in enumerate(patterns):
                            pattern.notes = modulations[i]

                elif mutation == 'invert':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            success = False
                            tries = 0
                            while not success and tries < 20:
                                success, new_notes = pattern.invert()
                                tries += 1
                            if success:
                                pattern.notes = new_notes

                elif mutation == 'reverse_melody':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.reverse_melody()

                elif mutation == 'regenerate_melody':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.generate_melody()

                elif mutation == 'regenerate_rhythm':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.regenerate_rhythm()

                # Add notes to MIDI file
                for track, channel, pattern in patterns:
                    pattern.start_times = [x + pattern.total_length for x in pattern.start_times]
                    for i in range(len(pattern.notes)):
                        midi_file.addNote(track, 
                                        channel,
                                        pattern.notes[i],
                                        pattern.start_times[i],
                                        pattern.durations[i],
                                        pattern.volumes[i])

        if store_info:
            # Write scale, instrument, pattern information to text file
            with open(param_filename, 'a+') as text_file:
                text_file.write('Key(s): ' + ', '.join(keys_used) + '\n')
                text_file.write(f'Scale type: {scale.scale_type_name}\n')
                text_file.write(f'Mode: {scale.mode_name}\n\n')
                text_file.write('Instruments: {}\n'.format(' '.join(instruments_used)))
                text_file.write('Pattern types:\n')
                p_strs = [str(p.__class__).split('.')[1].split("'")[0] for _, _, p in patterns]
                text_file.write(' '.join(p_strs))
                #text_file.write('Notes: {}\n'.format(', '.join(scale.names)))

        # # Write to MIDI
        # with open("test.mid", "wb") as output_file:
        #     midi_file.writeFile(output_file)



    def generate_music_2():
        """
        Generate a chord progression, generate a set of patterns for each chord 
        and write to an output midi file.
        """
        # TODO: keep instruments same
        # TODO: mutate patterns instead of generating new

        if args.chordproglen is not None:
            chords = generate_chord_progression(scale, args.chordproglen)
        else:
            chords = generate_chord_progression(scale)

        allowed_pattern_types = [
            # Percussion,
            Bass,
            Harmonic,
            Arpeggio
            # MidMelodic
        ]

        running_length = 0

        for chord in chords:

            available_patterns = allowed_pattern_types.copy()

            for track in range(args.numtracks):
                patterns = []
                channel = track

                # Generate random pattern and initialize
                pattern = random.choice(available_patterns)(
                    scale.key,
                    chord,
                    args.length,
                    args.repeat
                )
                pattern.initialize()
                available_patterns.remove(pattern.__class__) 

                # Choose instrument
                if pattern.__class__ in percussion_pattern_types:
                    channel = 9
                    instr = 0
                elif pattern.__class__ in bass_pattern_types:
                    instr = random.choice(bass_instruments)
                elif pattern.__class__ == Arpeggio:
                    instr = random.choice(arp_instruments)
                else:
                    instr = random.choice(all_instruments)
                
                instruments_used.append(str(instr))
                midi_file.addProgramChange(track, channel, 0, instr)
                
                # Limit volumes
                if pattern.__class__ == Harmonic:
                    pattern.volumes = [50 for x in pattern.volumes]
                # elif pattern.__class__ == percussion_pattern_types:
                #     pattern.volumes = [50 for x in pattern.volumes]

                patterns.append((track, channel, pattern))

                # Add notes to MIDI file
                for i in range(len(pattern.notes)):
                    midi_file.addNote(track, 
                                    channel,
                                    pattern.notes[i],
                                    pattern.start_times[i] + running_length,
                                    pattern.durations[i],
                                    pattern.volumes[i])

            running_length += args.length * args.repeat

        if store_info:
            # Write scale, instrument, pattern information to text file
            with open(param_filename, 'a+') as text_file:
                text_file.write('Key(s): ' + ', '.join(keys_used) + '\n')
                text_file.write(f'Scale type: {scale.scale_type_name}\n')
                text_file.write(f'Mode: {scale.mode_name}\n\n')
                text_file.write('Instruments: {}\n'.format(' '.join(instruments_used)))
                text_file.write('Pattern types:\n')
                p_strs = [str(p.__class__).split('.')[1].split("'")[0] for _, _, p in patterns]
                text_file.write(' '.join(p_strs))
                #text_file.write('Notes: {}\n'.format(', '.join(scale.names)))

        # # Write to MIDI
        # with open("test.mid", "wb") as output_file:
        #     midi_file.writeFile(output_file)


    def generate_music_3():
        """

        TODO: 9+ tracks -> channel 9 percussion (better fix)
        """
        patterns = []

        for i in range(args.numpatterns):

            # Generate one set of patterns
            if i == 0:

                available_patterns = [
                    bass,
                    Harmonic,
                    # Arpeggio,
                    melody1,
                    melody2,
                    PercussionSingle,
                    BassDrum,
                    Snare,
                    Cymbals,
                    AccentCymbals
                ]

                # available_patterns = [
                #     bass,
                #     Harmonic,
                #     melody1,
                #     melody2,
                #     PercussionSingle,
                #     BassDrum,
                #     Snare,
                #     Cymbals,
                #     AccentCymbals
                #     # Arpeggio,
                # ]

                if args.allpatterns:
                    last_track_number = len(available_patterns)
                else:
                    last_track_number = args.numtracks

                for track in range(last_track_number):
                    channel = track

                    # Generate random pattern and initialize

                    if args.allpatterns:
                        pattern = available_patterns[track]
                    else:
                        # Always include bass, bass drum
                        if track == 0:
                            pattern = bass
                        elif track == 1:
                            pattern = BassDrum
                        else:
                            pattern = random.choice(available_patterns)

                    pattern = pattern(
                                scale.key,
                                scale.all_scale_notes,
                                args.length,
                                args.repeat
                            )
                    pattern.initialize()

                    if not args.allpatterns and pattern.__class__ not in [PercussionSingle, Cymbals]:
                        available_patterns.remove(pattern.__class__) 

                    # Choose instrument
                    if pattern.__class__ in percussion_pattern_types:
                        channel = 9
                        instr = 0
                    elif pattern.__class__ in bass_pattern_types:
                        instr = random.choice(bass_instruments)
                    elif pattern.__class__ == Arpeggio:
                        instr = random.choice(arp_instruments)
                    else:
                        instr = random.choice(all_instruments)

                    instruments_used.append(str(instr))
                    midi_file.addProgramChange(track, channel, 0, instr)
                    
                    # Limit volumes
                    if pattern.__class__ in [Harmonic, PercussionSingle, Cymbals, AccentCymbals]:
                        pattern.volumes = [40 for x in pattern.volumes]
                    # elif pattern.__class__ in percussion_pattern_types:
                    #     pattern.volumes = [50 for x in pattern.volumes]

                    patterns.append((track, channel, pattern))

                    # Add notes to MIDI file
                    for i in range(len(pattern.notes)):
                        midi_file.addNote(track, 
                                        channel,
                                        pattern.notes[i],
                                        pattern.start_times[i],
                                        pattern.durations[i],
                                        pattern.volumes[i])

            # Mutate patterns
            else:

                # Choose random mutation type
                mutation_types = [
                    'modulate',
                    'diatonic_modulate',
                    'invert',
                    'reverse_melody',
                    'regenerate_melody',
                    'regenerate_rhythm'
                ]
                mutation_weights = [1, 5, 2, 1, 1, 2]
                mutation = random.choices(mutation_types, mutation_weights, k=1)[0]

                if mutation == 'modulate':
                    modulations = []
                    successes = [False]
                    tries = 0
                    while not all(successes) and tries < 20:
                        tries += 1
                        shifts = list(range(-5, 0)) + list(range(1, 6))
                        shift = random.choice(shifts)
                        modulations = []
                        successes = []
                        for _, _, pattern in patterns:
                            success, new_notes, new_key, new_scale = pattern.modulate(shift)
                            modulations.append((new_notes, new_key, new_scale))
                            successes.append(success)
                    if all(successes):
                        new_key = modulations[0][1]
                        keys_used.append(Scale.note_names[new_key])
                        for i, (_, _, pattern) in enumerate(patterns):
                            pattern.notes = modulations[i][0]
                            pattern.key = modulations[i][1]
                            pattern.scale = modulations[i][2]
                    
                elif mutation == 'diatonic_modulate':
                    modulations = []
                    successes = [False]
                    tries = 0
                    while not all(successes) and tries < 20:
                        tries += 1
                        shifts = list(range(-4, 0)) + list(range(1, 5))
                        shift = random.choice(shifts)
                        modulations = []
                        successes = []
                        for _, _, pattern in patterns:
                            success, new_notes = pattern.diatonic_modulate(shift)
                            modulations.append(new_notes)
                            successes.append(success)
                    if all(successes):
                        for i, (_, _, pattern) in enumerate(patterns):
                            pattern.notes = modulations[i]

                elif mutation == 'invert':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            success = False
                            tries = 0
                            while not success and tries < 20:
                                success, new_notes = pattern.invert()
                                tries += 1
                            if success:
                                pattern.notes = new_notes

                elif mutation == 'reverse_melody':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.reverse_melody()

                elif mutation == 'regenerate_melody':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.generate_melody()

                elif mutation == 'regenerate_rhythm':
                    for _, _, pattern in patterns:
                        if random.random() < 0.5:
                            pattern.regenerate_rhythm()

                # Add notes to MIDI file
                for track, channel, pattern in patterns:
                    pattern.start_times = [x + pattern.total_length for x in pattern.start_times]
                    for i in range(len(pattern.notes)):
                        midi_file.addNote(track, 
                                        channel,
                                        pattern.notes[i],
                                        pattern.start_times[i],
                                        pattern.durations[i],
                                        pattern.volumes[i])

        if store_info:
            # Write scale, instrument, pattern information to text file
            with open(param_filename, 'a+') as text_file:
                text_file.write('Key(s): ' + ', '.join(keys_used) + '\n')
                text_file.write(f'Scale type: {scale.scale_type_name}\n')
                text_file.write(f'Mode: {scale.mode_name}\n\n')
                text_file.write('Instruments: {}\n'.format(' '.join(instruments_used)))
                text_file.write('Pattern types:\n')
                p_strs = [str(p.__class__).split('.')[1].split("'")[0] for _, _, p in patterns]
                text_file.write(' '.join(p_strs))
                #text_file.write('Notes: {}\n'.format(', '.join(scale.names)))

        # # Write to MIDI
        # with open("test.mid", "wb") as output_file:
        #     midi_file.writeFile(output_file)




    def generate_music_4():

        default_pattern_types = [
            SimpleBass,
            Harmonic,
            Harmonic,
            Harmonic,
            MidMelodic,
            BassDrum,
            Snare,
            Cymbals,
            AccentCymbals,
            PercussionSingle
        ]

        chord_prog = ChordProgression(scale, length=args.chordproglen, voicing=args.voicing)

        for track, pattern_type in enumerate(default_pattern_types):

            if pattern_type in percussion_pattern_types:
                channel = 9
                instr = 0
                instruments_used.append(str(instr))
                midi_file.addProgramChange(track, channel, 0, instr)

                drum_pattern_bars = 2  # args.___
                drum_pattern_repeat = chord_prog.total_length // drum_pattern_bars  # remainder

                pattern = pattern_type(
                    scale.key,
                    scale.all_scale_notes,
                    args.length * drum_pattern_bars,
                    drum_pattern_repeat,
                    rigidity=args.rigidity
                )
                pattern.initialize()

                if pattern_type in [PercussionSingle, Cymbals, AccentCymbals]:
                    pattern.volumes = [40 for x in pattern.volumes]
                if pattern_type in [BassDrum, Snare]:
                    for i, vol in enumerate(pattern.volumes):
                        if vol > 75:
                            pattern.volumes[i] = 75

                add_notes(track, channel, pattern, midi_file)

            else:
                channel = (track % 16) if (track % 16) != 9 else 8
                if pattern_type in bass_pattern_types:
                    instr = random.choice(bass_instruments)
                else: 
                    instr = random.choice(all_instruments)
                instruments_used.append(str(instr))
                midi_file.addProgramChange(track, channel, 0, instr)

                for bar, chord in enumerate(chord_prog.chord_progression_notes):
                    pattern = pattern_type(
                        scale.key,
                        chord,
                        args.length,
                        1   # args.repeat
                    )
                    pattern.initialize()

                    if pattern_type == Harmonic:
                        pattern.volumes = [35 for x in pattern.volumes]

                    add_notes(track, channel, pattern, midi_file, repeat=bar)



    if args.gentype == 1:
        generate_music_1()
        
    elif args.gentype == 2:
        generate_music_2()

    elif args.gentype == 3:
        generate_music_3()

    elif args.gentype == 4:
        generate_music_4()

    # Write to MIDI
    with open(filepath, 'wb') as output_file:
        midi_file.writeFile(output_file)


if __name__ == "__main__":
    run(sys.argv)

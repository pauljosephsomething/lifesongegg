"""
DNA Lifesong Studio - DNA Processor v6.0
Codon Harmony Algorithm - Research-based DNA to Music conversion

Based on work by:
- Susumu Ohno (1986) - Repetitious recurrence principle
- Stuart Mitchell - Amino acid resonance frequencies
- John Dunn & Mary Anne Clark (1996) - Amino acid properties mapping
- MIT Protein Music Project (2019) - Hierarchical structure encoding

v6.0 - RHYTHMIC VARIETY + CHORD PROGRESSIONS:
- Melodic rhythm patterns (not just quarter notes!)
- DNA-driven chord progressions (I-IV-V, i-VI-III-VII, etc.)
- Third base determines note duration
- Codon pairs determine rhythm feel
- Amino acid properties select progression type
"""

import os
import subprocess
from midiutil import MIDIFile
from collections import Counter


class DNAProcessor:
    """
    Codon Harmony Algorithm v6.0

    New in v6.0:
    - RHYTHM: Third base of codon determines note duration
    - RHYTHM PATTERNS: Codon pairs create rhythmic motifs
    - CHORD PROGRESSIONS: Real harmonic movement (I-IV-V, etc.)
    - Progression type selected by amino acid properties
    """

    # ==================== KEY & MODE ====================

    ROOT_KEYS = {
        (0.0, 0.7): (11, 'B'), (0.7, 0.85): (4, 'E'),
        (0.85, 1.0): (9, 'A'), (1.0, 1.15): (2, 'D'),
        (1.15, 1.3): (7, 'G'), (1.3, 1.5): (0, 'C'),
        (1.5, 999): (5, 'F'),
    }

    MODES = {
        (0.0, 0.85): ([0, 1, 3, 5, 6, 8, 10], 'locrian', 'unstable'),
        (0.85, 0.92): ([0, 1, 3, 5, 7, 8, 10], 'phrygian', 'dark'),
        (0.92, 0.97): ([0, 2, 3, 5, 7, 8, 10], 'aeolian', 'reflective'),
        (0.97, 1.03): ([0, 2, 3, 5, 7, 9, 10], 'dorian', 'sophisticated'),
        (1.03, 1.08): ([0, 2, 4, 5, 7, 9, 10], 'mixolydian', 'bluesy'),
        (1.08, 1.15): ([0, 2, 4, 5, 7, 9, 11], 'ionian', 'bright'),
        (1.15, 999): ([0, 2, 4, 6, 7, 9, 11], 'lydian', 'ethereal'),
    }

    # ==================== CODON TABLES ====================

    CODON_TABLE = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
        'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
        'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
        'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
        'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
        'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
        'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
        'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
        'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
    }

    # Codon to scale degree (0-6)
    CODON_DEGREE = {
        'TTT': 0, 'TTC': 1, 'TTA': 0, 'TTG': 1,
        'CTT': 2, 'CTC': 3, 'CTA': 4, 'CTG': 5,
        'ATT': 1, 'ATC': 2, 'ATA': 3, 'ATG': 0,
        'GTT': 2, 'GTC': 3, 'GTA': 4, 'GTG': 2,
        'TCT': 0, 'TCC': 1, 'TCA': 2, 'TCG': 3,
        'AGT': 4, 'AGC': 5,
        'CCT': 3, 'CCC': 4, 'CCA': 5, 'CCG': 6,
        'ACT': 0, 'ACC': 1, 'ACA': 2, 'ACG': 3,
        'GCT': 0, 'GCC': 1, 'GCA': 2, 'GCG': 0,
        'TAT': 3, 'TAC': 4, 'CAT': 4, 'CAC': 5,
        'CAA': 2, 'CAG': 4, 'AAT': 1, 'AAC': 2,
        'AAA': 4, 'AAG': 6, 'GAT': 0, 'GAC': 1,
        'GAA': 2, 'GAG': 3, 'TGT': 5, 'TGC': 6,
        'TGG': 6, 'CGT': 3, 'CGC': 4, 'CGA': 5,
        'CGG': 6, 'AGA': 4, 'AGG': 5,
        'GGT': 0, 'GGC': 1, 'GGA': 0, 'GGG': 1,
        'TAA': -1, 'TAG': -1, 'TGA': -1,
    }

    # ==================== RHYTHM SYSTEM ====================

    # Third base determines base note duration (in beats)
    # A = long, T = medium, G = short, C = very short
    THIRD_BASE_DURATION = {
        'A': 1.5,    # Dotted quarter / half note feel
        'T': 1.0,    # Quarter note
        'G': 0.5,    # Eighth note
        'C': 0.25,   # Sixteenth note
    }

    # Rhythm patterns based on codon pair (first bases of consecutive codons)
    # Each pattern fills 4 beats and creates a rhythmic motif
    RHYTHM_PATTERNS = {
        # AA, AT, AG, AC - Flowing patterns (A-starting = legato)
        'AA': [1.5, 1.0, 1.5],           # Long-medium-long (waltz-like)
        'AT': [1.0, 1.0, 1.0, 1.0],      # Steady quarters
        'AG': [1.5, 0.5, 1.0, 1.0],      # Dotted eighth-sixteenth feel
        'AC': [1.0, 0.5, 0.5, 1.0, 1.0], # Syncopated

        # TA, TT, TG, TC - Driving patterns (T = rhythmic push)
        'TA': [1.0, 1.5, 1.5],           # Push to long notes
        'TT': [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],  # Driving eighths
        'TG': [0.75, 0.75, 0.5, 1.0, 1.0],     # Shuffle feel
        'TC': [0.5, 0.5, 0.5, 0.5, 2.0],       # Buildup to long

        # GA, GT, GG, GC - Sparse patterns (G = space)
        'GA': [2.0, 2.0],                # Half notes (breathing room)
        'GT': [1.5, 0.5, 2.0],           # Dotted quarter rest feel
        'GG': [1.0, 1.0, 2.0],           # Quarter quarter half
        'GC': [0.5, 1.5, 2.0],           # Pickup to sustained

        # CA, CT, CG, CC - Complex patterns (C = ornamentation)
        'CA': [0.25, 0.25, 0.5, 1.0, 2.0],     # Grace notes to sustained
        'CT': [0.5, 0.25, 0.25, 1.0, 1.0, 1.0], # Ornamental
        'CG': [0.25, 0.75, 1.0, 2.0],          # Quick pickup
        'CC': [0.25, 0.25, 0.25, 0.25, 1.0, 2.0], # Rapid to slow
    }

    # ==================== CHORD PROGRESSIONS ====================

    # Scale degree progressions (0=I, 1=ii, 2=iii, 3=IV, 4=V, 5=vi, 6=vii)
    # Selected by amino acid type
    PROGRESSIONS = {
        # Hydrophobic amino acids → Classic/Strong progressions
        'classic': [0, 3, 4, 0],         # I - IV - V - I (most common)
        'fifths': [0, 4, 0, 4],          # I - V - I - V (anthem)
        'rock': [0, 3, 0, 4],            # I - IV - I - V (rock/pop)

        # Polar amino acids → Gentle progressions
        'pastoral': [0, 4, 5, 3],        # I - V - vi - IV (pop ballad)
        'descending': [0, 5, 3, 4],      # I - vi - IV - V (50s)
        'gentle': [0, 2, 3, 0],          # I - iii - IV - I (soft)

        # Charged amino acids → Dramatic progressions
        'dramatic': [0, 5, 2, 4],        # I - vi - iii - V (emotional)
        'minor_feel': [5, 3, 0, 4],      # vi - IV - I - V (Axis)
        'tension': [0, 6, 5, 4],         # I - vii - vi - V (building)

        # Aromatic amino acids → Jazz/Complex progressions
        'jazz': [0, 1, 4, 0],            # I - ii - V - I (jazz standard)
        'circle': [0, 3, 6, 2, 5, 1, 4, 0],  # Circle of fifths
        'chromatic': [0, 5, 1, 4],       # I - vi - ii - V (rhythm changes)
    }

    # Map amino acid to progression type
    AMINO_PROGRESSION = {
        # Hydrophobic → Classic
        'L': 'classic', 'I': 'fifths', 'V': 'rock', 'M': 'classic',
        'A': 'fifths', 'F': 'jazz', 'W': 'circle',
        # Polar → Gentle
        'S': 'pastoral', 'T': 'descending', 'N': 'gentle', 'Q': 'pastoral',
        'Y': 'chromatic', 'C': 'tension',
        # Charged → Dramatic
        'K': 'dramatic', 'R': 'minor_feel', 'H': 'tension',
        'D': 'dramatic', 'E': 'minor_feel',
        # Special
        'P': 'rock', 'G': 'gentle',
        '*': 'classic',
    }

    # Chord qualities based on scale degree and mode character
    CHORD_QUALITIES = {
        0: [0, 2, 4],       # I - triad
        1: [0, 2, 4],       # ii - triad
        2: [0, 2, 4],       # iii - triad
        3: [0, 2, 4],       # IV - triad
        4: [0, 2, 4],       # V - triad
        5: [0, 2, 4],       # vi - triad
        6: [0, 2, 4],       # vii - triad (diminished in major)
    }

    # ==================== PHRASE CONTOURS ====================

    CONTOURS = {
        'A': [0, 1, 2, 1],      # Arch up
        'T': [2, 1, 0, 1],      # Trough
        'G': [0, 1, 1, 2],      # Rise
        'C': [2, 1, 1, 0],      # Fall
    }

    # Octave by amino acid property
    AMINO_OCTAVE = {
        'L': -12, 'I': -12, 'V': -12, 'M': 0, 'A': -12, 'F': 0, 'W': 0,
        'S': 0, 'T': 0, 'N': 0, 'Q': 0, 'Y': 0, 'C': 0,
        'K': 12, 'R': 12, 'H': 0, 'D': 0, 'E': 0,
        'P': 0, 'G': -12, '*': 0,
    }

    # ==================== INSTRUMENTS ====================

    INSTRUMENT_SETS = {
        'low_gc': {'melody': 71, 'harmony': 46, 'bass': 33, 'pad': 92},
        'mid_gc': {'melody': 73, 'harmony': 48, 'bass': 33, 'pad': 89},
        'high_gc': {'melody': 79, 'harmony': 88, 'bass': 39, 'pad': 91},
        'very_high_gc': {'melody': 80, 'harmony': 95, 'bass': 38, 'pad': 94},
    }

    # ==================== ANALYSIS ====================

    def analyze(self, sequence):
        if not sequence or len(sequence) < 3:
            return self._default_analysis()

        sequence = sequence.upper()
        length = len(sequence)

        gc_count = sequence.count('G') + sequence.count('C')
        at_count = sequence.count('A') + sequence.count('T')
        gc_content = (gc_count / length) * 100

        at_gc_ratio = at_count / gc_count if gc_count > 0 else 1.5
        root_note, key_name = self._get_root_key(at_gc_ratio)

        purines = sequence.count('A') + sequence.count('G')
        pyrimidines = sequence.count('T') + sequence.count('C')
        pu_py_ratio = purines / pyrimidines if pyrimidines > 0 else 1.0
        scale, mode_name, character = self._get_mode(pu_py_ratio)

        tempo = int(65 + (gc_content / 100) * 30)

        codons = self._get_codons(sequence)
        amino_acids = [self.CODON_TABLE.get(c, 'X') for c in codons]
        motifs = self._detect_motifs(sequence)

        # Determine dominant amino acid type for progression selection
        # Exclude stop codons from the count
        amino_counts = Counter(aa for aa in amino_acids if aa != '*' and aa != 'X')
        dominant_amino = amino_counts.most_common(1)[0][0] if amino_counts else 'A'

        return {
            'key': key_name, 'root_note': root_note,
            'mode': mode_name, 'scale': scale, 'character': character,
            'tempo': tempo, 'gc': gc_content,
            'at_gc_ratio': round(at_gc_ratio, 3),
            'pu_py_ratio': round(pu_py_ratio, 3),
            'codons': codons, 'amino_acids': amino_acids,
            'codon_count': len(codons),
            'motifs': motifs, 'motif_count': len(motifs),
            'length': length,
            'dominant_amino': dominant_amino,
        }

    def _default_analysis(self):
        return {
            'key': 'C', 'root_note': 0,
            'mode': 'aeolian', 'scale': [0, 2, 3, 5, 7, 8, 10],
            'character': 'reflective', 'tempo': 72, 'gc': 50.0,
            'at_gc_ratio': 1.0, 'pu_py_ratio': 1.0,
            'codons': [], 'amino_acids': [],
            'codon_count': 0, 'motifs': [], 'motif_count': 0, 'length': 0,
            'dominant_amino': 'A',
        }

    def _get_root_key(self, ratio):
        for (low, high), (note, name) in self.ROOT_KEYS.items():
            if low <= ratio < high:
                return note, name
        return 0, 'C'

    def _get_mode(self, ratio):
        for (low, high), (scale, name, char) in self.MODES.items():
            if low <= ratio < high:
                return scale, name, char
        return [0, 2, 3, 5, 7, 8, 10], 'aeolian', 'reflective'

    def _get_codons(self, sequence):
        codons = []
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if len(codon) == 3 and all(b in 'ATGC' for b in codon):
                codons.append(codon)
        return codons

    def _detect_motifs(self, sequence):
        motifs = []
        for length in range(6, 19, 3):
            pattern_counts = Counter()
            for i in range(len(sequence) - length + 1):
                pattern = sequence[i:i+length]
                if all(b in 'ATGC' for b in pattern):
                    pattern_counts[pattern] += 1
            for pattern, count in pattern_counts.items():
                if count >= 2:
                    motifs.append({'pattern': pattern, 'count': count, 'length': length})
        motifs.sort(key=lambda x: (-x['count'], -x['length']))
        return motifs[:5]

    def _snap_to_scale(self, pitch, root, scale):
        pitch_class = (pitch - root) % 12
        min_distance = 12
        nearest_interval = 0
        for interval in scale:
            distance = min(abs(pitch_class - interval), 12 - abs(pitch_class - interval))
            if distance < min_distance:
                min_distance = distance
                nearest_interval = interval
        octave = (pitch - root) // 12
        snapped = root + (octave * 12) + nearest_interval
        if snapped > pitch + 6:
            snapped -= 12
        elif snapped < pitch - 6:
            snapped += 12
        return snapped

    # ==================== MIDI GENERATION ====================

    def generate_midi(self, dna, duration, output_path):
        analysis = self.analyze(dna)

        if analysis['codon_count'] < 3:
            return self._generate_simple_midi(dna, duration, output_path, analysis)

        root = analysis['root_note']
        scale = analysis['scale']
        tempo = analysis['tempo']
        codons = analysis['codons']
        gc = analysis['gc']

        if gc < 35:
            instruments = self.INSTRUMENT_SETS['low_gc']
        elif gc < 50:
            instruments = self.INSTRUMENT_SETS['mid_gc']
        elif gc < 65:
            instruments = self.INSTRUMENT_SETS['high_gc']
        else:
            instruments = self.INSTRUMENT_SETS['very_high_gc']

        midi = MIDIFile(4, deinterleave=False)

        for track, (name, inst) in enumerate([
            ('Melody', instruments['melody']),
            ('Harmony', instruments['harmony']),
            ('Bass', instruments['bass']),
            ('Pad', instruments['pad']),
        ]):
            midi.addTrackName(track, 0, name)
            midi.addTempo(track, 0, tempo)
            midi.addProgramChange(track, track, 0, inst)

        beats_per_second = tempo / 60
        total_beats = int(duration * beats_per_second)

        # Generate chord progression first (harmony drives everything)
        progression = self._build_progression(codons, analysis)

        # Generate tracks
        self._generate_melody_v6(midi, codons, root, scale, total_beats, analysis, progression)
        self._generate_harmony_v6(midi, root, scale, total_beats, progression)
        self._generate_bass_v6(midi, root, scale, total_beats, progression)
        self._generate_pad_v6(midi, root, scale, total_beats, progression)

        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        return analysis

    def _build_progression(self, codons, analysis):
        """
        Build the chord progression for the entire piece.
        Uses DNA to select progression type and creates a sequence of chords.

        Returns list of (chord_degree, duration_beats, codon) tuples
        """
        if not codons:
            return [(0, 4.0, 'ATG')]

        # Get progression type from dominant amino acid
        dominant = analysis.get('dominant_amino', 'A')
        prog_type = self.AMINO_PROGRESSION.get(dominant, 'classic')
        base_progression = self.PROGRESSIONS.get(prog_type, [0, 3, 4, 0])

        # Each chord lasts 4 beats (one bar)
        CHORD_DURATION = 4.0

        progression = []
        prog_idx = 0
        codon_idx = 0

        # Calculate how many chords we need
        # Use enough codons to cycle through progression multiple times
        num_chords = max(8, len(codons) // 4)  # At least 8 chords, or 1 per 4 codons

        for i in range(num_chords):
            # Get chord degree from progression pattern
            chord_degree = base_progression[prog_idx % len(base_progression)]

            # Get the codon that "owns" this chord (for bass pattern variation)
            codon = codons[codon_idx % len(codons)]

            progression.append((chord_degree, CHORD_DURATION, codon))

            prog_idx += 1
            codon_idx += 1

        return progression

    def _generate_melody_v6(self, midi, codons, root, scale, total_beats, analysis, progression):
        """
        v6.0 Melody with rhythmic variety

        - Uses rhythm patterns based on codon pairs
        - Third base affects individual note duration
        - Melodic contour shapes phrases
        - Stays in sync with chord changes
        """
        if not codons:
            return

        time_pos = 0.0
        codon_idx = 0
        last_pitch = 60 + root
        chord_idx = 0

        while time_pos < total_beats and codon_idx < len(codons):
            # Get current and next codon for rhythm pattern
            codon = codons[codon_idx]
            next_codon = codons[(codon_idx + 1) % len(codons)]

            # Skip stop codons (rest)
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += 1.0
                codon_idx += 1
                continue

            # Get rhythm pattern from codon pair
            pattern_key = codon[0] + next_codon[0]
            rhythm_pattern = self.RHYTHM_PATTERNS.get(pattern_key, [1.0, 1.0, 1.0, 1.0])

            # Get current chord for harmonic reference
            if chord_idx < len(progression):
                current_chord_degree = progression[chord_idx][0]
            else:
                current_chord_degree = 0

            # Generate notes following the rhythm pattern
            pattern_time = 0.0
            pattern_total = sum(rhythm_pattern)

            for note_idx, note_duration in enumerate(rhythm_pattern):
                if time_pos + pattern_time >= total_beats:
                    break

                # Cycle through codons for each note in pattern
                note_codon_idx = (codon_idx + note_idx) % len(codons)
                note_codon = codons[note_codon_idx]

                if self.CODON_TABLE.get(note_codon) == '*':
                    pattern_time += note_duration
                    continue

                # Get scale degree from codon
                base_degree = self.CODON_DEGREE.get(note_codon, 0)
                if base_degree == -1:
                    pattern_time += note_duration
                    continue

                # Apply contour based on position in pattern
                contour_key = note_codon[0]
                contour = self.CONTOURS.get(contour_key, [0, 1, 2, 1])
                contour_offset = contour[note_idx % len(contour)]

                final_degree = (base_degree + contour_offset) % len(scale)

                # Get octave from amino acid
                amino = self.CODON_TABLE.get(note_codon, 'A')
                octave_offset = self.AMINO_OCTAVE.get(amino, 0)

                raw_pitch = 60 + root + scale[final_degree] + octave_offset

                # Stepwise motion constraint
                max_jump = 5
                if abs(raw_pitch - last_pitch) > max_jump:
                    direction = 1 if raw_pitch > last_pitch else -1
                    raw_pitch = last_pitch + (direction * max_jump)

                pitch = self._snap_to_scale(raw_pitch, root, scale)
                pitch = max(48, min(84, pitch))

                # Modify duration based on third base
                third_base = note_codon[2]
                duration_mod = self.THIRD_BASE_DURATION.get(third_base, 1.0)
                final_duration = note_duration * duration_mod
                final_duration = max(0.2, min(note_duration, final_duration))

                # Velocity based on beat strength
                if note_idx == 0:
                    velocity = 85  # Downbeat strong
                elif note_idx % 2 == 0:
                    velocity = 75  # Other strong beats
                else:
                    velocity = 65  # Weak beats

                midi.addNote(
                    track=0, channel=0, pitch=pitch,
                    time=time_pos + pattern_time,
                    duration=final_duration * 0.9,
                    volume=velocity
                )

                last_pitch = pitch
                pattern_time += note_duration

            time_pos += pattern_total
            codon_idx += len(rhythm_pattern)  # Advance by notes used

            # Advance chord index if we've passed a chord boundary
            while chord_idx < len(progression) - 1:
                chord_end = sum(p[1] for p in progression[:chord_idx + 1])
                if time_pos >= chord_end:
                    chord_idx += 1
                else:
                    break

    def _generate_harmony_v6(self, midi, root, scale, total_beats, progression):
        """
        v6.0 Harmony - Follows the DNA-selected chord progression
        """
        time_pos = 0.0

        for chord_degree, duration, codon in progression:
            if time_pos >= total_beats:
                break

            # Get chord tones (triad)
            chord_intervals = self.CHORD_QUALITIES.get(chord_degree, [0, 2, 4])

            # Build chord from scale
            for interval in chord_intervals:
                # Chord is built on the scale degree
                actual_degree = (chord_degree + interval) % len(scale)
                pitch = 48 + root + scale[actual_degree]
                pitch = max(36, min(72, pitch))

                actual_duration = min(duration, total_beats - time_pos)

                midi.addNote(
                    track=1, channel=1, pitch=pitch,
                    time=time_pos, duration=actual_duration * 0.95,
                    volume=50
                )

            time_pos += duration

    def _generate_bass_v6(self, midi, root, scale, total_beats, progression):
        """
        v6.0 Bass - Root-fifth pattern following chord progression
        """
        time_pos = 0.0

        for chord_degree, duration, codon in progression:
            if time_pos >= total_beats:
                break

            # Root note of chord
            root_pitch = 36 + root + scale[chord_degree % len(scale)]
            root_pitch = max(28, min(48, root_pitch))

            # Fifth of chord
            fifth_degree = (chord_degree + 4) % len(scale)
            fifth_pitch = 36 + root + scale[fifth_degree]
            fifth_pitch = max(28, min(48, fifth_pitch))

            # Bass pattern varies by codon's second base
            second_base = codon[1] if len(codon) > 1 else 'A'

            if second_base == 'A':
                # Whole note root
                midi.addNote(track=2, channel=2, pitch=root_pitch,
                            time=time_pos, duration=min(duration * 0.9, total_beats - time_pos), volume=70)
            elif second_base == 'T':
                # Root and fifth
                midi.addNote(track=2, channel=2, pitch=root_pitch,
                            time=time_pos, duration=1.8, volume=70)
                if time_pos + 2 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=fifth_pitch,
                                time=time_pos + 2, duration=1.8, volume=60)
            elif second_base == 'G':
                # Walking pattern
                midi.addNote(track=2, channel=2, pitch=root_pitch,
                            time=time_pos, duration=0.9, volume=70)
                if time_pos + 1 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=fifth_pitch,
                                time=time_pos + 1, duration=0.9, volume=60)
                if time_pos + 2 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=root_pitch,
                                time=time_pos + 2, duration=0.9, volume=65)
                if time_pos + 3 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=fifth_pitch,
                                time=time_pos + 3, duration=0.9, volume=55)
            else:  # C
                # Syncopated
                midi.addNote(track=2, channel=2, pitch=root_pitch,
                            time=time_pos, duration=1.4, volume=70)
                if time_pos + 1.5 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=fifth_pitch,
                                time=time_pos + 1.5, duration=1.0, volume=65)
                if time_pos + 2.5 < total_beats:
                    midi.addNote(track=2, channel=2, pitch=root_pitch,
                                time=time_pos + 2.5, duration=1.4, volume=60)

            time_pos += duration

    def _generate_pad_v6(self, midi, root, scale, total_beats, progression):
        """
        v6.0 Pad - Sustained chords, changes every 2 chord progressions
        """
        time_pos = 0.0
        chord_idx = 0

        while time_pos < total_beats and chord_idx < len(progression):
            # Use every other chord for pad (slower movement)
            chord_degree, _, _ = progression[chord_idx]

            # Pad duration is 2 chords worth (8 beats)
            pad_duration = 8.0
            actual_duration = min(pad_duration, total_beats - time_pos)

            # Build pad chord
            for interval in [0, 2, 4]:
                actual_degree = (chord_degree + interval) % len(scale)
                pitch = 54 + root + scale[actual_degree]
                pitch = max(48, min(72, pitch))

                midi.addNote(
                    track=3, channel=3, pitch=pitch,
                    time=time_pos, duration=actual_duration,
                    volume=35
                )

            time_pos += pad_duration
            chord_idx += 2  # Skip every other chord

    def _generate_simple_midi(self, dna, duration, output_path, analysis):
        midi = MIDIFile(1, deinterleave=False)
        midi.addTrackName(0, 0, "Simple")
        midi.addTempo(0, 0, analysis['tempo'])
        midi.addProgramChange(0, 0, 0, 73)

        root = analysis['root_note']
        scale = analysis['scale']

        time_pos = 0
        for base in dna.upper():
            if time_pos >= duration * 2:
                break
            if base in 'ATGC':
                degree = {'A': 0, 'T': 1, 'G': 2, 'C': 3}.get(base, 0)
                pitch = 60 + root + scale[degree % len(scale)]
                midi.addNote(0, 0, pitch, time_pos, 1, 70)
                time_pos += 1

        with open(output_path, 'wb') as f:
            midi.writeFile(f)
        return analysis

    # ==================== MP3 CONVERSION ====================

    def convert_to_mp3(self, midi_path, mp3_path):
        try:
            wav_path = midi_path.replace('.mid', '.wav')
            subprocess.run(['timidity', midi_path, '-Ow', '-o', wav_path],
                          check=True, capture_output=True, text=True)
            try:
                subprocess.run(['lame', '-V2', wav_path, mp3_path],
                              check=True, capture_output=True, text=True)
            except FileNotFoundError:
                subprocess.run(['afconvert', wav_path, mp3_path, '-d', 'aac', '-f', 'mp4f'],
                              check=True, capture_output=True, text=True)
            if os.path.exists(wav_path):
                os.remove(wav_path)
            return True
        except Exception as e:
            print(f"Conversion error: {e}")
            return False

"""
DNA Lifesong Studio - DNA Processor v5.0
Codon Harmony Algorithm - Research-based DNA to Music conversion

Based on work by:
- Susumu Ohno (1986) - Repetitious recurrence principle
- Stuart Mitchell - Amino acid resonance frequencies
- John Dunn & Mary Anne Clark (1996) - Amino acid properties mapping
- MIT Protein Music Project (2019) - Hierarchical structure encoding

v5.0 - MUSICAL COHERENCE WITH DNA VARIETY:
- Phrases: 4-bar musical sentences with DNA-driven content
- Motifs: Repeating themes based on detected DNA patterns
- Stepwise motion: Adjacent notes move by small intervals (musical)
- Phrase contour: Each phrase has a shape (rise/fall/arch) from DNA
- Chord tones: Strong beat notes align with harmony
- Different DNA = different music, but ALL music sounds musical
"""

import os
import subprocess
from midiutil import MIDIFile
from collections import Counter
import re


class DNAProcessor:
    """
    Codon Harmony Algorithm v5.0 - Musical + Varied

    The key insight: Musical coherence comes from STRUCTURE, not randomness.
    DNA drives WHAT notes to play, but musical rules govern HOW they connect.

    Principles:
    1. Stepwise motion (notes move by small intervals most of the time)
    2. Phrase structure (4-bar sentences with beginning, middle, end)
    3. Chord tone emphasis (strong beats land on harmonically stable notes)
    4. Motif repetition (DNA patterns become recurring musical themes)
    5. Contour (phrases have shapes - DNA determines which shape)
    """

    # ==================== LAYER 1: KEY & MODE TABLES ====================

    ROOT_KEYS = {
        (0.0, 0.7): (11, 'B'),
        (0.7, 0.85): (4, 'E'),
        (0.85, 1.0): (9, 'A'),
        (1.0, 1.15): (2, 'D'),
        (1.15, 1.3): (7, 'G'),
        (1.3, 1.5): (0, 'C'),
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

    # ==================== LAYER 2: CODON TO AMINO ACID ====================

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

    AMINO_ACID_CHORDS = {
        'L': ('min', [0, 2, 4]), 'I': ('min', [0, 2, 4]),
        'V': ('min', [0, 2, 4]), 'M': ('min', [0, 2, 4]),
        'A': ('min', [0, 2, 4]),
        'F': ('maj7', [0, 2, 4, 6]), 'Y': ('min7', [0, 2, 4, 6]),
        'W': ('maj9', [0, 2, 4, 6, 1]),
        'S': ('maj', [0, 2, 4]), 'T': ('maj', [0, 2, 4]),
        'N': ('maj', [0, 2, 4]), 'Q': ('maj', [0, 2, 4]),
        'K': ('dom7', [0, 2, 4, 5]), 'R': ('dom7', [0, 2, 4, 5]),
        'H': ('dom7', [0, 2, 4, 5]),
        'D': ('min7', [0, 2, 4, 5]), 'E': ('min7', [0, 2, 4, 5]),
        'P': ('sus4', [0, 3, 4]), 'G': ('sus2', [0, 1, 4]),
        'C': ('dim', [0, 2, 4]),
        '*': ('rest', []),
    }

    # ==================== LAYER 3: CODON FREQUENCY ====================

    CODON_FREQUENCY = {
        'TTT': 17.6, 'TTC': 20.3, 'TTA': 7.7, 'TTG': 12.9,
        'TCT': 15.2, 'TCC': 17.7, 'TCA': 12.2, 'TCG': 4.4,
        'TAT': 12.2, 'TAC': 15.3, 'TAA': 1.0, 'TAG': 0.8,
        'TGT': 10.6, 'TGC': 12.6, 'TGA': 1.6, 'TGG': 13.2,
        'CTT': 13.2, 'CTC': 19.6, 'CTA': 7.2, 'CTG': 39.6,
        'CCT': 17.5, 'CCC': 19.8, 'CCA': 16.9, 'CCG': 6.9,
        'CAT': 10.9, 'CAC': 15.1, 'CAA': 12.3, 'CAG': 34.2,
        'CGT': 4.5, 'CGC': 10.4, 'CGA': 6.2, 'CGG': 11.4,
        'ATT': 16.0, 'ATC': 20.8, 'ATA': 7.5, 'ATG': 22.0,
        'ACT': 13.1, 'ACC': 18.9, 'ACA': 15.1, 'ACG': 6.1,
        'AAT': 17.0, 'AAC': 19.1, 'AAA': 24.4, 'AAG': 31.9,
        'AGT': 12.1, 'AGC': 19.5, 'AGA': 12.2, 'AGG': 12.0,
        'GTT': 11.0, 'GTC': 14.5, 'GTA': 7.1, 'GTG': 28.1,
        'GCT': 18.4, 'GCC': 27.7, 'GCA': 15.8, 'GCG': 7.4,
        'GAT': 21.8, 'GAC': 25.1, 'GAA': 29.0, 'GAG': 39.6,
        'GGT': 10.8, 'GGC': 22.2, 'GGA': 16.5, 'GGG': 16.5,
    }

    # ==================== LAYER 4: CODON TO SCALE DEGREE ====================
    # Maps each codon to a scale degree (0-6) for melodic coherence
    # Grouped by amino acid for musical "family" consistency

    CODON_DEGREE = {
        # Phenylalanine - low (0-1)
        'TTT': 0, 'TTC': 1,
        # Leucine - spans range (0-5)
        'TTA': 0, 'TTG': 1, 'CTT': 2, 'CTC': 3, 'CTA': 4, 'CTG': 5,
        # Isoleucine - mid-low (1-3)
        'ATT': 1, 'ATC': 2, 'ATA': 3,
        # Methionine (START) - root (0)
        'ATG': 0,
        # Valine - mid (2-4)
        'GTT': 2, 'GTC': 3, 'GTA': 4, 'GTG': 2,
        # Serine - spans (0-5)
        'TCT': 0, 'TCC': 1, 'TCA': 2, 'TCG': 3, 'AGT': 4, 'AGC': 5,
        # Proline - tension (3-6)
        'CCT': 3, 'CCC': 4, 'CCA': 5, 'CCG': 6,
        # Threonine - stable (0-3)
        'ACT': 0, 'ACC': 1, 'ACA': 2, 'ACG': 3,
        # Alanine - grounded (0-2)
        'GCT': 0, 'GCC': 1, 'GCA': 2, 'GCG': 0,
        # Tyrosine - mid-high (3-4)
        'TAT': 3, 'TAC': 4,
        # Histidine - bright (4-5)
        'CAT': 4, 'CAC': 5,
        # Glutamine - flowing (2-4)
        'CAA': 2, 'CAG': 4,
        # Asparagine - gentle (1-2)
        'AAT': 1, 'AAC': 2,
        # Lysine - bright/high (4-6)
        'AAA': 4, 'AAG': 6,
        # Aspartic acid - grounded (0-1)
        'GAT': 0, 'GAC': 1,
        # Glutamic acid - mid (2-3)
        'GAA': 2, 'GAG': 3,
        # Cysteine - tension (5-6)
        'TGT': 5, 'TGC': 6,
        # Tryptophan - high (6)
        'TGG': 6,
        # Arginine - spans high (3-6)
        'CGT': 3, 'CGC': 4, 'CGA': 5, 'CGG': 6, 'AGA': 4, 'AGG': 5,
        # Glycine - root/stable (0-1)
        'GGT': 0, 'GGC': 1, 'GGA': 0, 'GGG': 1,
        # Stop codons - rest
        'TAA': -1, 'TAG': -1, 'TGA': -1,
    }

    # ==================== PHRASE CONTOURS ====================
    # These define the SHAPE of a 4-note phrase (relative movement)
    # Selected by DNA, but musically coherent regardless

    CONTOURS = {
        'A': [0, 1, 2, 1],      # Arch up (A for Arch)
        'T': [2, 1, 0, 1],      # Arch down (T for Trough)
        'G': [0, 1, 1, 2],      # Gradual rise (G for Growth)
        'C': [2, 1, 1, 0],      # Gradual fall (C for Cascade)
    }

    # Octave placement by amino acid property
    AMINO_OCTAVE = {
        # Hydrophobic = lower register
        'L': -12, 'I': -12, 'V': -12, 'M': 0, 'A': -12, 'F': 0, 'W': 0,
        # Polar = middle register
        'S': 0, 'T': 0, 'N': 0, 'Q': 0, 'Y': 0, 'C': 0,
        # Charged = higher register
        'K': 12, 'R': 12, 'H': 0, 'D': 0, 'E': 0,
        # Special
        'P': 0, 'G': -12,
        # Stop
        '*': 0,
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

        tempo = int(65 + (gc_content / 100) * 30)  # 65-95 BPM range

        codons = self._get_codons(sequence)
        amino_acids = [self.CODON_TABLE.get(c, 'X') for c in codons]
        motifs = self._detect_motifs(sequence)

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
        }

    def _default_analysis(self):
        return {
            'key': 'C', 'root_note': 0,
            'mode': 'aeolian', 'scale': [0, 2, 3, 5, 7, 8, 10],
            'character': 'reflective', 'tempo': 72, 'gc': 50.0,
            'at_gc_ratio': 1.0, 'pu_py_ratio': 1.0,
            'codons': [], 'amino_acids': [],
            'codon_count': 0, 'motifs': [], 'motif_count': 0, 'length': 0,
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

        # Generate musically coherent tracks
        self._generate_melody_v5(midi, codons, root, scale, total_beats, analysis)
        self._generate_harmony_v5(midi, codons, root, scale, total_beats)
        self._generate_bass_v5(midi, codons, root, scale, total_beats)
        self._generate_pad_v5(midi, codons, root, scale, total_beats)

        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        return analysis

    def _generate_melody_v5(self, midi, codons, root, scale, total_beats, analysis):
        """
        v5.0 Melody - Musical phrases with DNA-driven content

        Structure:
        - 4-beat phrases (musical sentences)
        - Each phrase has a contour (shape) determined by DNA
        - Notes within phrase move stepwise (musical)
        - Strong beats (1, 3) emphasize chord tones
        - Phrase boundaries get longer notes (breathing room)
        """
        if not codons:
            return

        # Work in 4-beat phrases
        PHRASE_LENGTH = 4  # beats
        NOTES_PER_PHRASE = 4  # one note per beat in phrase

        total_phrases = total_beats // PHRASE_LENGTH
        codons_per_phrase = max(1, len(codons) // total_phrases) if total_phrases > 0 else 1

        time_pos = 0.0
        codon_idx = 0
        last_pitch = 60 + root  # Start at middle C + key

        for phrase_num in range(total_phrases):
            if codon_idx >= len(codons):
                codon_idx = 0  # Loop codons if needed

            # Get codons for this phrase
            phrase_codons = codons[codon_idx:codon_idx + NOTES_PER_PHRASE]
            if len(phrase_codons) < NOTES_PER_PHRASE:
                phrase_codons = phrase_codons + codons[:NOTES_PER_PHRASE - len(phrase_codons)]

            # Determine phrase contour from first codon's first base
            contour_key = phrase_codons[0][0] if phrase_codons else 'A'
            contour = self.CONTOURS.get(contour_key, [0, 1, 2, 1])

            # Generate notes for this phrase
            for note_in_phrase in range(NOTES_PER_PHRASE):
                if note_in_phrase < len(phrase_codons):
                    codon = phrase_codons[note_in_phrase]
                else:
                    codon = phrase_codons[-1]

                # Skip stop codons (rest)
                if self.CODON_TABLE.get(codon) == '*':
                    time_pos += 1.0
                    continue

                # Get base scale degree from codon
                base_degree = self.CODON_DEGREE.get(codon, 0)
                if base_degree == -1:  # Stop codon
                    time_pos += 1.0
                    continue

                # Apply contour offset
                contour_offset = contour[note_in_phrase % len(contour)]

                # Final degree combines codon's natural degree + contour shape
                final_degree = (base_degree + contour_offset) % len(scale)

                # Get pitch from scale
                amino = self.CODON_TABLE.get(codon, 'A')
                octave_offset = self.AMINO_OCTAVE.get(amino, 0)

                raw_pitch = 60 + root + scale[final_degree] + octave_offset

                # STEPWISE MOTION: Don't jump more than a 4th from last note
                # This is what makes it sound MUSICAL
                max_jump = 5  # semitones (a 4th)
                if abs(raw_pitch - last_pitch) > max_jump:
                    # Move toward target by step
                    direction = 1 if raw_pitch > last_pitch else -1
                    raw_pitch = last_pitch + (direction * max_jump)

                pitch = self._snap_to_scale(raw_pitch, root, scale)
                pitch = max(48, min(84, pitch))

                # Duration: phrase start/end notes are longer
                if note_in_phrase == 0:
                    duration = 1.2  # Phrase start - slightly longer
                elif note_in_phrase == NOTES_PER_PHRASE - 1:
                    duration = 1.5  # Phrase end - breath
                else:
                    duration = 0.9  # Middle notes - connected

                # Velocity: strong beats (1, 3) louder
                if note_in_phrase % 2 == 0:
                    velocity = 80
                else:
                    velocity = 65

                # Phrase dynamics (crescendo/decrescendo)
                phrase_progress = phrase_num / max(1, total_phrases - 1)
                if phrase_progress < 0.3:
                    velocity = int(velocity * (0.7 + phrase_progress))
                elif phrase_progress > 0.7:
                    velocity = int(velocity * (1.3 - phrase_progress))

                velocity = max(50, min(100, velocity))

                midi.addNote(
                    track=0, channel=0, pitch=pitch,
                    time=time_pos,
                    duration=min(duration, 1.0) * 0.9,
                    volume=velocity
                )

                last_pitch = pitch
                time_pos += 1.0

            codon_idx += codons_per_phrase

    def _generate_harmony_v5(self, midi, codons, root, scale, total_beats):
        """
        v5.0 Harmony - Chord changes every 4 beats (one per phrase)
        """
        if not codons:
            return

        CHORD_LENGTH = 4.0  # One chord per phrase
        num_chords = int(total_beats // CHORD_LENGTH)
        codons_per_chord = max(1, len(codons) // num_chords) if num_chords > 0 else 1

        time_pos = 0.0
        codon_idx = 0

        for _ in range(num_chords):
            if time_pos >= total_beats:
                break

            codon = codons[codon_idx % len(codons)]
            amino = self.CODON_TABLE.get(codon, 'A')
            chord_name, degrees = self.AMINO_ACID_CHORDS.get(amino, ('maj', [0, 2, 4]))

            if chord_name == 'rest':
                time_pos += CHORD_LENGTH
                codon_idx += codons_per_chord
                continue

            # Chord root from first base
            root_degree = {'A': 0, 'T': 1, 'G': 4, 'C': 3}.get(codon[0], 0)

            for deg in degrees:
                actual_deg = (root_degree + deg) % len(scale)
                pitch = 48 + root + scale[actual_deg]
                pitch = max(36, min(72, pitch))

                midi.addNote(
                    track=1, channel=1, pitch=pitch,
                    time=time_pos, duration=CHORD_LENGTH * 0.95,
                    volume=50
                )

            time_pos += CHORD_LENGTH
            codon_idx += codons_per_chord

    def _generate_bass_v5(self, midi, codons, root, scale, total_beats):
        """
        v5.0 Bass - Root-fifth pattern locked to chord changes
        """
        if not codons:
            return

        CHORD_LENGTH = 4.0
        num_chords = int(total_beats // CHORD_LENGTH)
        codons_per_chord = max(1, len(codons) // num_chords) if num_chords > 0 else 1

        time_pos = 0.0
        codon_idx = 0

        for _ in range(num_chords):
            if time_pos >= total_beats:
                break

            codon = codons[codon_idx % len(codons)]
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += CHORD_LENGTH
                codon_idx += codons_per_chord
                continue

            # Root degree from first base
            root_degree = {'A': 0, 'T': 1, 'G': 4, 'C': 3}.get(codon[0], 0)
            root_pitch = 36 + root + scale[root_degree % len(scale)]
            root_pitch = max(28, min(48, root_pitch))

            # Fifth
            fifth_degree = (root_degree + 4) % len(scale)
            fifth_pitch = 36 + root + scale[fifth_degree]
            fifth_pitch = max(28, min(48, fifth_pitch))

            # Pattern: root on 1, fifth on 3
            midi.addNote(track=2, channel=2, pitch=root_pitch,
                        time=time_pos, duration=1.8, volume=70)
            midi.addNote(track=2, channel=2, pitch=fifth_pitch,
                        time=time_pos + 2.0, duration=1.8, volume=60)

            time_pos += CHORD_LENGTH
            codon_idx += codons_per_chord

    def _generate_pad_v5(self, midi, codons, root, scale, total_beats):
        """
        v5.0 Pad - Slow-moving sustained harmony (changes every 8 beats)
        """
        if not codons:
            return

        PAD_LENGTH = 8.0
        num_pads = int(total_beats // PAD_LENGTH) + 1
        codons_per_pad = max(1, len(codons) // num_pads) if num_pads > 0 else 1

        time_pos = 0.0
        codon_idx = 0

        while time_pos < total_beats:
            codon = codons[codon_idx % len(codons)]
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += PAD_LENGTH
                codon_idx += codons_per_pad
                continue

            root_degree = {'A': 0, 'T': 1, 'G': 4, 'C': 3}.get(codon[0], 0)

            # Simple triad pad
            for deg_offset in [0, 2, 4]:
                actual_deg = (root_degree + deg_offset) % len(scale)
                pitch = 54 + root + scale[actual_deg]
                pitch = max(48, min(72, pitch))

                remaining = total_beats - time_pos
                dur = min(PAD_LENGTH, remaining)

                midi.addNote(
                    track=3, channel=3, pitch=pitch,
                    time=time_pos, duration=dur,
                    volume=35
                )

            time_pos += PAD_LENGTH
            codon_idx += codons_per_pad

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

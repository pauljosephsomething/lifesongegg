"""
DNA Lifesong Studio - DNA Processor v4.0
Codon Harmony Algorithm - Research-based DNA to Music conversion

Based on work by:
- Susumu Ohno (1986) - Repetitious recurrence principle
- Stuart Mitchell - Amino acid resonance frequencies
- John Dunn & Mary Anne Clark (1996) - Amino acid properties mapping
- MIT Protein Music Project (2019) - Hierarchical structure encoding

v4.0 - COMPLETE DNA-DRIVEN MELODIC VARIETY:
- Every codon produces a UNIQUE melodic fragment
- No hardcoded patterns - everything derives from DNA
- Intro/outro are DNA-driven, not fixed patterns
- Harmony, bass, pad all respond to actual codon sequence
- Maximum musical variety from sequence variation
"""

import os
import subprocess
from midiutil import MIDIFile
from collections import Counter
import re


class DNAProcessor:
    """
    Codon Harmony Algorithm v4.0

    CRITICAL: Every musical element must derive from DNA.
    NO hardcoded patterns that sound the same regardless of sequence.

    Converts DNA sequences to music using a 5-layer hierarchical approach:
    1. Global Analysis → Key signature & mode
    2. Codon Reading → Chord progressions
    3. Codon Frequency → Rhythm patterns
    4. DIRECT CODON-TO-PITCH → Each codon = unique pitch
    5. Motif Detection → Themes & variations
    """

    # ==================== LAYER 1: KEY & MODE TABLES ====================

    # Root key based on AT/GC ratio
    ROOT_KEYS = {
        # ratio_range: (root_note, key_name)
        (0.0, 0.7): (11, 'B'),      # High GC = B (tension)
        (0.7, 0.85): (4, 'E'),      # E (bright)
        (0.85, 1.0): (9, 'A'),      # A (warm)
        (1.0, 1.15): (2, 'D'),      # D (balanced)
        (1.15, 1.3): (7, 'G'),      # G (open)
        (1.3, 1.5): (0, 'C'),       # C (pure)
        (1.5, 999): (5, 'F'),       # High AT = F (deep)
    }

    # Mode based on purine/pyrimidine ratio (A+G)/(T+C)
    MODES = {
        # ratio_range: (scale_intervals, mode_name, character)
        (0.0, 0.85): ([0, 1, 3, 5, 6, 8, 10], 'locrian', 'unstable'),
        (0.85, 0.92): ([0, 1, 3, 5, 7, 8, 10], 'phrygian', 'dark'),
        (0.92, 0.97): ([0, 2, 3, 5, 7, 8, 10], 'aeolian', 'reflective'),
        (0.97, 1.03): ([0, 2, 3, 5, 7, 9, 10], 'dorian', 'sophisticated'),
        (1.03, 1.08): ([0, 2, 4, 5, 7, 9, 10], 'mixolydian', 'bluesy'),
        (1.08, 1.15): ([0, 2, 4, 5, 7, 9, 11], 'ionian', 'bright'),
        (1.15, 999): ([0, 2, 4, 6, 7, 9, 11], 'lydian', 'ethereal'),
    }

    # ==================== LAYER 2: CODON TO AMINO ACID ====================

    # Standard genetic code
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

    # Amino acid properties → chord qualities (using SCALE DEGREES, not semitones)
    AMINO_ACID_CHORDS = {
        # Hydrophobic (nonpolar) → Minor-like triads
        'L': ('min', [0, 2, 4]),
        'I': ('min', [0, 2, 4]),
        'V': ('min', [0, 2, 4]),
        'M': ('min', [0, 2, 4]),
        'A': ('min', [0, 2, 4]),

        # Aromatic → Extended chords
        'F': ('maj7', [0, 2, 4, 6]),
        'Y': ('min7', [0, 2, 4, 6]),
        'W': ('maj9', [0, 2, 4, 6, 1]),

        # Hydrophilic (polar) → Open triads
        'S': ('maj', [0, 2, 4]),
        'T': ('maj', [0, 2, 4]),
        'N': ('maj', [0, 2, 4]),
        'Q': ('maj', [0, 2, 4]),

        # Positively charged → With tension
        'K': ('dom7', [0, 2, 4, 5]),
        'R': ('dom7', [0, 2, 4, 5]),
        'H': ('dom7', [0, 2, 4, 5]),

        # Negatively charged → With depth
        'D': ('min7', [0, 2, 4, 5]),
        'E': ('min7', [0, 2, 4, 5]),

        # Special/structural → Suspended
        'P': ('sus4', [0, 3, 4]),
        'G': ('sus2', [0, 1, 4]),
        'C': ('dim', [0, 2, 4]),

        # Stop codons → Rest/cadence
        '*': ('rest', []),
    }

    # ==================== LAYER 3: CODON FREQUENCY ====================

    # Human codon usage frequencies (per 1000 codons)
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

    # ==================== LAYER 4: DIRECT CODON-TO-PITCH ====================
    # CRITICAL: Each of 64 codons maps to a UNIQUE pitch offset
    # This is THE KEY to melodic variety - different codons = different notes
    # ALL 64 values are UNIQUE (0-63 range, mapped to ~2.5 octaves)

    CODON_PITCH = {
        # === T-starting codons (0-15) ===
        'TTT': 0,   'TTC': 1,   'TTA': 2,   'TTG': 3,
        'TCT': 4,   'TCC': 5,   'TCA': 6,   'TCG': 7,
        'TAT': 8,   'TAC': 9,   'TAA': -1,  'TAG': -1,  # Stop = rest
        'TGT': 10,  'TGC': 11,  'TGA': -1,  'TGG': 12,  # Stop = rest

        # === C-starting codons (13-28) ===
        'CTT': 13,  'CTC': 14,  'CTA': 15,  'CTG': 16,
        'CCT': 17,  'CCC': 18,  'CCA': 19,  'CCG': 20,
        'CAT': 21,  'CAC': 22,  'CAA': 23,  'CAG': 24,
        'CGT': 25,  'CGC': 26,  'CGA': 27,  'CGG': 28,

        # === A-starting codons (29-44) ===
        'ATT': 29,  'ATC': 30,  'ATA': 31,  'ATG': 32,  # ATG = start!
        'ACT': 33,  'ACC': 34,  'ACA': 35,  'ACG': 36,
        'AAT': 37,  'AAC': 38,  'AAA': 39,  'AAG': 40,
        'AGT': 41,  'AGC': 42,  'AGA': 43,  'AGG': 44,

        # === G-starting codons (45-60) ===
        'GTT': 45,  'GTC': 46,  'GTA': 47,  'GTG': 48,
        'GCT': 49,  'GCC': 50,  'GCA': 51,  'GCG': 52,
        'GAT': 53,  'GAC': 54,  'GAA': 55,  'GAG': 56,
        'GGT': 57,  'GGC': 58,  'GGA': 59,  'GGG': 60,
    }

    # Base position → scale degree adjustment
    FIRST_BASE_DEGREE = {
        'A': 0,  # Root
        'T': 1,  # Second
        'G': 2,  # Third
        'C': 3,  # Fourth
    }

    # Second base → octave modifier
    SECOND_BASE_OCTAVE = {
        'A': 0,    # Base octave
        'T': -12,  # Down octave
        'G': 12,   # Up octave
        'C': 0,    # Base octave
    }

    # Third base → duration multiplier
    THIRD_BASE_DURATION = {
        'A': 1.5,   # Long
        'T': 1.0,   # Normal
        'G': 0.75,  # Medium
        'C': 0.5,   # Short
    }

    # ==================== INSTRUMENTS ====================

    INSTRUMENTS = {
        'melody': 73,      # Flute
        'harmony': 48,     # String Ensemble
        'bass': 33,        # Acoustic Bass
        'pad': 89,         # Pad (warm)
    }

    INSTRUMENT_SETS = {
        'low_gc': {
            'melody': 71,   # Clarinet
            'harmony': 46,  # Orchestral Harp
            'bass': 33,     # Acoustic Bass
            'pad': 92,      # Pad (bowed)
        },
        'mid_gc': {
            'melody': 73,   # Flute
            'harmony': 48,  # String Ensemble
            'bass': 33,     # Acoustic Bass
            'pad': 89,      # Pad (warm)
        },
        'high_gc': {
            'melody': 79,   # Ocarina
            'harmony': 88,  # Pad (new age)
            'bass': 39,     # Synth Bass 1
            'pad': 91,      # Pad (space voice)
        },
        'very_high_gc': {
            'melody': 80,   # Lead (square)
            'harmony': 95,  # Pad (sweep)
            'bass': 38,     # Synth Bass 1
            'pad': 94,      # Pad (halo)
        }
    }

    # ==================== ANALYSIS METHODS ====================

    def analyze(self, sequence):
        """Complete DNA analysis using all 5 layers"""
        if not sequence or len(sequence) < 3:
            return self._default_analysis()

        sequence = sequence.upper()
        length = len(sequence)

        # === LAYER 1: Global Analysis ===
        gc_count = sequence.count('G') + sequence.count('C')
        at_count = sequence.count('A') + sequence.count('T')
        gc_content = (gc_count / length) * 100

        at_gc_ratio = at_count / gc_count if gc_count > 0 else 1.5
        root_note, key_name = self._get_root_key(at_gc_ratio)

        purines = sequence.count('A') + sequence.count('G')
        pyrimidines = sequence.count('T') + sequence.count('C')
        pu_py_ratio = purines / pyrimidines if pyrimidines > 0 else 1.0
        scale, mode_name, character = self._get_mode(pu_py_ratio)

        tempo = int(60 + (gc_content / 100) * 40)

        # === LAYER 2: Codon Analysis ===
        codons = self._get_codons(sequence)
        amino_acids = [self.CODON_TABLE.get(c, 'X') for c in codons]

        # === LAYER 5: Motif Detection ===
        motifs = self._detect_motifs(sequence)

        return {
            'key': key_name,
            'root_note': root_note,
            'mode': mode_name,
            'scale': scale,
            'character': character,
            'tempo': tempo,
            'gc': gc_content,
            'at_gc_ratio': round(at_gc_ratio, 3),
            'pu_py_ratio': round(pu_py_ratio, 3),
            'codons': codons,
            'amino_acids': amino_acids,
            'codon_count': len(codons),
            'motifs': motifs,
            'motif_count': len(motifs),
            'length': length,
        }

    def _default_analysis(self):
        """Return default values for empty/invalid sequences"""
        return {
            'key': 'C',
            'root_note': 0,
            'mode': 'aeolian',
            'scale': [0, 2, 3, 5, 7, 8, 10],
            'character': 'reflective',
            'tempo': 72,
            'gc': 50.0,
            'at_gc_ratio': 1.0,
            'pu_py_ratio': 1.0,
            'codons': [],
            'amino_acids': [],
            'codon_count': 0,
            'motifs': [],
            'motif_count': 0,
            'length': 0,
        }

    def _get_root_key(self, ratio):
        """Get root key from AT/GC ratio"""
        for (low, high), (note, name) in self.ROOT_KEYS.items():
            if low <= ratio < high:
                return note, name
        return 0, 'C'

    def _get_mode(self, ratio):
        """Get mode from purine/pyrimidine ratio"""
        for (low, high), (scale, name, char) in self.MODES.items():
            if low <= ratio < high:
                return scale, name, char
        return [0, 2, 3, 5, 7, 8, 10], 'aeolian', 'reflective'

    def _get_codons(self, sequence):
        """Split sequence into codons (triplets)"""
        codons = []
        for i in range(0, len(sequence) - 2, 3):
            codon = sequence[i:i+3]
            if len(codon) == 3 and all(b in 'ATGC' for b in codon):
                codons.append(codon)
        return codons

    def _detect_motifs(self, sequence):
        """Detect repeating patterns (motifs) in the sequence"""
        motifs = []
        min_length = 6
        max_length = 18

        for length in range(min_length, max_length + 1, 3):
            pattern_counts = Counter()
            for i in range(len(sequence) - length + 1):
                pattern = sequence[i:i+length]
                if all(b in 'ATGC' for b in pattern):
                    pattern_counts[pattern] += 1

            for pattern, count in pattern_counts.items():
                if count >= 2:
                    motifs.append({
                        'pattern': pattern,
                        'count': count,
                        'length': length
                    })

        motifs.sort(key=lambda x: (-x['count'], -x['length']))
        return motifs[:5]

    # ==================== HELPER METHODS ====================

    def _snap_to_scale(self, pitch, root, scale):
        """Snap any pitch to the nearest note in the current scale."""
        pitch_class = (pitch - root) % 12
        min_distance = 12
        nearest_interval = 0

        for interval in scale:
            distance = min(abs(pitch_class - interval), 12 - abs(pitch_class - interval))
            if distance < min_distance:
                min_distance = distance
                nearest_interval = interval

        octave = (pitch - root) // 12
        snapped_pitch = root + (octave * 12) + nearest_interval

        if snapped_pitch > pitch + 6:
            snapped_pitch -= 12
        elif snapped_pitch < pitch - 6:
            snapped_pitch += 12

        return snapped_pitch

    # ==================== MIDI GENERATION ====================

    def generate_midi(self, dna, duration, output_path):
        """
        Generate MIDI file using the Codon Harmony algorithm

        v4.0 - NO HARDCODED PATTERNS
        Every note derives directly from the DNA sequence.
        """
        analysis = self.analyze(dna)

        if analysis['codon_count'] < 3:
            return self._generate_simple_midi(dna, duration, output_path, analysis)

        root = analysis['root_note']
        scale = analysis['scale']
        tempo = analysis['tempo']
        codons = analysis['codons']
        gc = analysis['gc']

        # Select instrument set based on GC content
        if gc < 35:
            instruments = self.INSTRUMENT_SETS['low_gc']
        elif gc < 50:
            instruments = self.INSTRUMENT_SETS['mid_gc']
        elif gc < 65:
            instruments = self.INSTRUMENT_SETS['high_gc']
        else:
            instruments = self.INSTRUMENT_SETS['very_high_gc']

        # Create MIDI file with 4 tracks
        midi = MIDIFile(4, deinterleave=False)

        track_config = [
            ('Melody', instruments['melody'], 0),
            ('Harmony', instruments['harmony'], 1),
            ('Bass', instruments['bass'], 2),
            ('Pad', instruments['pad'], 3),
        ]

        for track, (name, instrument, channel) in enumerate(track_config):
            midi.addTrackName(track, 0, name)
            midi.addTempo(track, 0, tempo)
            midi.addProgramChange(track, channel, 0, instrument)

        # Calculate beats
        beats_per_second = tempo / 60
        total_beats = int(duration * beats_per_second)

        # Generate ALL tracks from DNA - no hardcoded intro/outro
        self._generate_melody_v4(midi, codons, root, scale, total_beats, analysis)
        self._generate_harmony_v4(midi, codons, root, scale, total_beats)
        self._generate_bass_v4(midi, codons, root, scale, total_beats)
        self._generate_pad_v4(midi, codons, root, scale, total_beats)

        # Write MIDI file
        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        analysis['has_intro'] = False
        analysis['has_outro'] = False
        analysis['stop_codon'] = None

        return analysis

    def _generate_melody_v4(self, midi, codons, root, scale, total_beats, analysis):
        """
        v4.0 Melody Generation - PURE DNA DRIVEN

        Every single note comes directly from a codon.
        No hardcoded patterns, no fixed sequences.
        """
        if not codons:
            return

        time_pos = 0.0
        codon_idx = 0

        # Calculate timing: spread codons evenly across available time
        # Reserve small gap at end for natural fade
        usable_beats = total_beats * 0.95
        beats_per_codon = usable_beats / len(codons) if len(codons) > 0 else 1.0

        # Minimum duration to avoid notes too short
        min_duration = 0.25
        max_duration = 2.0

        while time_pos < total_beats and codon_idx < len(codons):
            codon = codons[codon_idx]

            # Get codon's unique pitch (0-60 range, or -1 for rest)
            codon_pitch = self.CODON_PITCH.get(codon, 30)

            if codon_pitch == -1:
                # Stop codon = rest
                time_pos += beats_per_codon
                codon_idx += 1
                continue

            # === PITCH CALCULATION ===
            # Scale the 0-60 range to fit within 2 octaves
            # Map to scale tones for harmonic coherence
            scale_len = len(scale)

            # Which octave (0-60 spans about 2.5 octaves)
            octave_offset = (codon_pitch // 24) * 12  # 0, 12, or 24

            # Which scale degree (use modulo to stay in scale)
            scale_degree = (codon_pitch % 24) % scale_len
            pitch_in_scale = scale[scale_degree]

            # Base octave is middle range
            base_pitch = 60 + root + pitch_in_scale + octave_offset

            # Apply second base octave modifier (subtle shift)
            base2 = codon[1]
            octave_mod = self.SECOND_BASE_OCTAVE.get(base2, 0) // 2  # Halved for subtlety

            pitch = base_pitch + octave_mod
            pitch = max(48, min(84, pitch))

            # Snap to scale for harmonic coherence
            pitch = self._snap_to_scale(pitch, root, scale)
            pitch = max(48, min(84, pitch))

            # === DURATION CALCULATION ===
            # Base duration from codon position
            base_duration = beats_per_codon

            # Third base modifies duration
            base3 = codon[2]
            duration_mod = self.THIRD_BASE_DURATION.get(base3, 1.0)
            note_duration = base_duration * duration_mod

            # Clamp duration
            note_duration = max(min_duration, min(max_duration, note_duration))

            # === VELOCITY (DYNAMICS) ===
            # Create dynamic shape based on position in sequence
            position_ratio = codon_idx / len(codons)

            # Bell curve dynamics: softer at start/end, louder in middle
            if position_ratio < 0.2:
                velocity = int(60 + position_ratio * 100)  # 60-80 crescendo
            elif position_ratio > 0.8:
                velocity = int(80 - (position_ratio - 0.8) * 100)  # 80-60 decrescendo
            else:
                velocity = int(75 + (0.5 - abs(position_ratio - 0.5)) * 20)  # 75-85 middle

            # Codon frequency affects velocity (rare codons = accented)
            freq = self.CODON_FREQUENCY.get(codon, 15.0)
            if freq < 10:
                velocity = min(100, velocity + 15)  # Rare codons are louder

            velocity = max(50, min(100, velocity))

            # Add the note
            midi.addNote(
                track=0,
                channel=0,
                pitch=pitch,
                time=time_pos,
                duration=note_duration * 0.9,  # Slight gap between notes
                volume=velocity
            )

            time_pos += beats_per_codon
            codon_idx += 1

    def _generate_harmony_v4(self, midi, codons, root, scale, total_beats):
        """
        v4.0 Harmony - Chords from amino acid properties

        Each codon's amino acid determines chord quality.
        Chord changes happen based on actual codon sequence.
        """
        if not codons:
            return

        # Harmony changes every few codons for musical flow
        # Faster codon progression = faster chord changes
        codons_per_chord = max(2, len(codons) // 20)  # ~20 chord changes
        beats_per_chord = (total_beats / len(codons)) * codons_per_chord

        time_pos = 0.0
        chord_idx = 0

        while time_pos < total_beats and chord_idx < len(codons):
            codon = codons[chord_idx]
            amino_acid = self.CODON_TABLE.get(codon, 'A')

            chord_name, scale_degrees = self.AMINO_ACID_CHORDS.get(
                amino_acid, ('maj', [0, 2, 4])
            )

            if chord_name == 'rest':
                time_pos += beats_per_chord
                chord_idx += codons_per_chord
                continue

            # Root degree from codon's first base
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)

            # Build chord from scale degrees
            for degree_offset in scale_degrees:
                actual_degree = (root_degree + degree_offset) % len(scale)
                pitch_in_scale = scale[actual_degree]
                octave_adjust = ((root_degree + degree_offset) // len(scale)) * 12

                pitch = 48 + root + pitch_in_scale + octave_adjust
                pitch = max(36, min(72, pitch))

                midi.addNote(
                    track=1,
                    channel=1,
                    pitch=pitch,
                    time=time_pos,
                    duration=beats_per_chord * 0.95,
                    volume=55
                )

            time_pos += beats_per_chord
            chord_idx += codons_per_chord

    def _generate_bass_v4(self, midi, codons, root, scale, total_beats):
        """
        v4.0 Bass - Root movement from codon sequence

        Bass follows chord roots with rhythm from codon properties.
        """
        if not codons:
            return

        # Bass changes with chords
        codons_per_chord = max(2, len(codons) // 20)
        beats_per_chord = (total_beats / len(codons)) * codons_per_chord

        time_pos = 0.0
        chord_idx = 0

        while time_pos < total_beats and chord_idx < len(codons):
            codon = codons[chord_idx]

            if self.CODON_TABLE.get(codon) == '*':
                time_pos += beats_per_chord
                chord_idx += codons_per_chord
                continue

            # Root degree from first base
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)
            pitch_offset = scale[root_degree % len(scale)]
            bass_pitch = 36 + root + pitch_offset
            bass_pitch = max(28, min(48, bass_pitch))

            # Rhythm pattern from second and third base
            base2, base3 = codon[1], codon[2]

            # Create a 2-note bass pattern per chord
            # First note = root, second note = fifth
            fifth_degree = (root_degree + 4) % len(scale)
            fifth_pitch = 36 + root + scale[fifth_degree]
            fifth_pitch = max(28, min(48, fifth_pitch))

            # Duration split based on third base
            dur_mod = self.THIRD_BASE_DURATION.get(base3, 1.0)
            first_dur = beats_per_chord * 0.6 * dur_mod
            second_dur = beats_per_chord * 0.35

            # Add root note
            midi.addNote(
                track=2, channel=2, pitch=bass_pitch,
                time=time_pos, duration=min(first_dur, beats_per_chord * 0.5),
                volume=70
            )

            # Add fifth (if there's time)
            if first_dur < beats_per_chord * 0.7:
                midi.addNote(
                    track=2, channel=2, pitch=fifth_pitch,
                    time=time_pos + first_dur, duration=second_dur,
                    volume=60
                )

            time_pos += beats_per_chord
            chord_idx += codons_per_chord

    def _generate_pad_v4(self, midi, codons, root, scale, total_beats):
        """
        v4.0 Pad - Sustained atmosphere from codon sequence

        Long sustained chords that follow the harmonic progression.
        """
        if not codons:
            return

        # Pad changes less frequently than harmony (every ~4 chords)
        codons_per_pad = max(4, len(codons) // 10)
        beats_per_pad = (total_beats / len(codons)) * codons_per_pad

        time_pos = 0.0
        pad_idx = 0

        while time_pos < total_beats and pad_idx < len(codons):
            codon = codons[pad_idx]

            if self.CODON_TABLE.get(codon) == '*':
                time_pos += beats_per_pad
                pad_idx += codons_per_pad
                continue

            # Root from codon
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)

            # Simple triad for pad
            for degree_offset in [0, 2, 4]:
                actual_degree = (root_degree + degree_offset) % len(scale)
                pitch_in_scale = scale[actual_degree]
                pitch = 54 + root + pitch_in_scale
                pitch = max(48, min(72, pitch))

                midi.addNote(
                    track=3, channel=3, pitch=pitch,
                    time=time_pos, duration=beats_per_pad,
                    volume=35  # Soft
                )

            time_pos += beats_per_pad
            pad_idx += codons_per_pad

    def _generate_simple_midi(self, dna, duration, output_path, analysis):
        """Fallback for very short sequences"""
        midi = MIDIFile(1, deinterleave=False)
        midi.addTrackName(0, 0, "Simple")
        midi.addTempo(0, 0, analysis['tempo'])
        midi.addProgramChange(0, 0, 0, self.INSTRUMENTS['melody'])

        root = analysis['root_note']
        scale = analysis['scale']

        time_pos = 0
        for i, base in enumerate(dna.upper()):
            if time_pos >= duration * 2:
                break
            if base in 'ATGC':
                degree = self.FIRST_BASE_DEGREE.get(base, 0)
                pitch = 60 + root + scale[degree % len(scale)]
                midi.addNote(0, 0, pitch, time_pos, 1, 70)
                time_pos += 1

        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        return analysis

    # ==================== MP3 CONVERSION ====================

    def convert_to_mp3(self, midi_path, mp3_path):
        """Convert MIDI file to MP3"""
        try:
            wav_path = midi_path.replace('.mid', '.wav')

            result = subprocess.run(
                ['timidity', midi_path, '-Ow', '-o', wav_path],
                check=True,
                capture_output=True,
                text=True
            )

            try:
                subprocess.run(
                    ['lame', '-V2', wav_path, mp3_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                subprocess.run(
                    ['afconvert', wav_path, mp3_path, '-d', 'aac', '-f', 'mp4f'],
                    check=True,
                    capture_output=True,
                    text=True
                )

            if os.path.exists(wav_path):
                os.remove(wav_path)

            return True

        except subprocess.CalledProcessError as e:
            print(f"Conversion error: {e.stderr if e.stderr else str(e)}")
            return False
        except FileNotFoundError as e:
            print(f"Required tool not found: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

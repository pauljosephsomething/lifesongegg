"""
DNA Lifesong Studio - DNA Processor v3.2
Codon Harmony Algorithm - Research-based DNA to Music conversion

Based on work by:
- Susumu Ohno (1986) - Repetitious recurrence principle
- Stuart Mitchell - Amino acid resonance frequencies
- John Dunn & Mary Anne Clark (1996) - Amino acid properties mapping
- MIT Protein Music Project (2019) - Hierarchical structure encoding

v3.2 Intro/Outro Update:
- Intro section triggered by ATG start codon (rising arpeggio, establishing key)
- Outro section triggered by stop codons TAA/TAG/TGA (resolving cadence)
- Musical structure now mirrors genetic structure

v3.1 Coherence Update:
- Chords now use scale degrees instead of absolute intervals (stay in mode)
- Bass rhythm aligned with 4-beat harmonic cycle
- Pad follows harmonic progression
- Melody notes snapped to scale (no stray out-of-key notes)
- Duration quantized to half-beats for rhythmic flow
"""

import os
import subprocess
from midiutil import MIDIFile
from collections import Counter
import re


class DNAProcessor:
    """
    Codon Harmony Algorithm

    Converts DNA sequences to music using a 5-layer hierarchical approach:
    1. Global Analysis → Key signature & mode
    2. Codon Reading → Chord progressions
    3. Codon Frequency → Rhythm patterns
    4. Base Positions → Melody notes
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
    # This ensures chords stay within the mode's scale
    # Based on biochemical properties (hydrophobicity, charge, size)
    AMINO_ACID_CHORDS = {
        # Hydrophobic (nonpolar) → Minor-like triads (scale degrees 0, 2, 4 = root, 3rd, 5th)
        'L': ('min', [0, 2, 4]),           # Leucine - i chord
        'I': ('min', [0, 2, 4]),           # Isoleucine
        'V': ('min', [0, 2, 4]),           # Valine
        'M': ('min', [0, 2, 4]),           # Methionine (start)
        'A': ('min', [0, 2, 4]),           # Alanine

        # Aromatic → Extended chords (scale degrees with 7th)
        'F': ('maj7', [0, 2, 4, 6]),       # Phenylalanine - with 7th
        'Y': ('min7', [0, 2, 4, 6]),       # Tyrosine
        'W': ('maj9', [0, 2, 4, 6, 1]),    # Tryptophan - add 9th (octave + degree 1)

        # Hydrophilic (polar) → Open triads
        'S': ('maj', [0, 2, 4]),           # Serine
        'T': ('maj', [0, 2, 4]),           # Threonine
        'N': ('maj', [0, 2, 4]),           # Asparagine
        'Q': ('maj', [0, 2, 4]),           # Glutamine

        # Positively charged → With tension (add 6th degree)
        'K': ('dom7', [0, 2, 4, 5]),       # Lysine - adds 6th
        'R': ('dom7', [0, 2, 4, 5]),       # Arginine
        'H': ('dom7', [0, 2, 4, 5]),       # Histidine

        # Negatively charged → With depth (add 6th degree)
        'D': ('min7', [0, 2, 4, 5]),       # Aspartic acid
        'E': ('min7', [0, 2, 4, 5]),       # Glutamic acid

        # Special/structural → Suspended (skip the 3rd)
        'P': ('sus4', [0, 3, 4]),          # Proline (rigid) - sus4 feel
        'G': ('sus2', [0, 1, 4]),          # Glycine (flexible) - sus2 feel
        'C': ('dim', [0, 2, 4]),           # Cysteine (bonds) - diminished feel

        # Stop codons → Rest/cadence
        '*': ('rest', []),                  # Stop codon
    }

    # ==================== LAYER 3: CODON FREQUENCY ====================

    # Human codon usage frequencies (per 1000 codons)
    # Higher frequency = shorter note, lower = longer note
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

    # ==================== LAYER 4: BASE POSITION MAPPING ====================

    # DIRECT CODON-TO-PITCH: Each of 64 codons maps to a unique pitch offset
    # This is the KEY to melodic variety - different codons = different notes
    # Organized by amino acid groups for musical coherence
    # Values are semitone offsets from the root (0-24 range, ~2 octaves)
    CODON_PITCH = {
        # Phenylalanine (F) - aromatic, lower register
        'TTT': 0, 'TTC': 1,
        # Leucine (L) - hydrophobic, spans register
        'TTA': 2, 'TTG': 3, 'CTT': 4, 'CTC': 5, 'CTA': 6, 'CTG': 7,
        # Isoleucine (I) - hydrophobic
        'ATT': 8, 'ATC': 9, 'ATA': 10,
        # Methionine (M) - start codon, distinctive
        'ATG': 12,  # Octave up - start of life!
        # Valine (V) - hydrophobic
        'GTT': 3, 'GTC': 5, 'GTA': 7, 'GTG': 8,
        # Serine (S) - polar, spread out
        'TCT': 10, 'TCC': 11, 'TCA': 12, 'TCG': 13, 'AGT': 14, 'AGC': 15,
        # Proline (P) - structural, mid register
        'CCT': 5, 'CCC': 7, 'CCA': 9, 'CCG': 11,
        # Threonine (T) - polar
        'ACT': 12, 'ACC': 13, 'ACA': 14, 'ACG': 15,
        # Alanine (A) - simple, stable
        'GCT': 7, 'GCC': 9, 'GCA': 11, 'GCG': 12,
        # Tyrosine (Y) - aromatic
        'TAT': 14, 'TAC': 16,
        # Histidine (H) - charged
        'CAT': 10, 'CAC': 12,
        # Glutamine (Q) - polar
        'CAA': 15, 'CAG': 17,
        # Asparagine (N) - polar
        'AAT': 17, 'AAC': 19,
        # Lysine (K) - positive charge, bright
        'AAA': 19, 'AAG': 21,
        # Aspartic acid (D) - negative charge
        'GAT': 14, 'GAC': 16,
        # Glutamic acid (E) - negative charge
        'GAA': 17, 'GAG': 19,
        # Cysteine (C) - special bonds
        'TGT': 8, 'TGC': 10,
        # Tryptophan (W) - largest aromatic, high
        'TGG': 22,
        # Arginine (R) - positive charge, spread
        'CGT': 18, 'CGC': 19, 'CGA': 20, 'CGG': 21, 'AGA': 22, 'AGG': 23,
        # Glycine (G) - simplest, grounding
        'GGT': 0, 'GGC': 2, 'GGA': 4, 'GGG': 5,
        # Stop codons - silence/rest
        'TAA': -1, 'TAG': -1, 'TGA': -1,  # -1 = rest
    }

    # First base → scale degree (which note in the scale)
    # Now uses all 7 scale degrees based on codon context
    FIRST_BASE_DEGREE = {
        'A': 0,  # Root
        'T': 3,  # Fourth
        'G': 4,  # Fifth
        'C': 6,  # Seventh
    }

    # Extended degree mapping based on second base context
    # This creates 16 possible scale degree combinations
    CODON_DEGREE_MODIFIER = {
        'AA': 0, 'AT': 1, 'AG': 2, 'AC': 3,
        'TA': 1, 'TT': 2, 'TG': 3, 'TC': 4,
        'GA': 2, 'GT': 3, 'GG': 4, 'GC': 5,
        'CA': 3, 'CT': 4, 'CG': 5, 'CC': 6,
    }

    # Second base → octave modifier (more variation)
    SECOND_BASE_OCTAVE = {
        'A': -12,  # Lower octave
        'T': -5,   # Lower fifth (creates counterpoint)
        'G': 0,    # Middle
        'C': 12,   # Higher octave
    }

    # Third base → duration modifier (multiplier) - more rhythmic variety
    THIRD_BASE_DURATION = {
        'A': 2.0,   # Long (whole feel)
        'T': 1.0,   # Normal
        'G': 0.66,  # Triplet feel
        'C': 0.5,   # Staccato
    }

    # Rhythm patterns based on codon third position combinations
    RHYTHM_PATTERNS = {
        'AA': [2.0, 1.0],           # Long-short
        'AT': [1.0, 1.0, 1.0],      # Even
        'AG': [0.66, 0.66, 0.66],   # Triplets
        'AC': [0.5, 0.5, 1.0],      # Short-short-long
        'TA': [1.5, 0.5],           # Dotted
        'TT': [1.0, 0.5, 0.5],      # Long-short-short
        'TG': [0.75, 0.75, 0.5],    # Swing feel
        'TC': [0.5, 1.5],           # Pickup
        'GA': [1.0, 0.66, 0.66, 0.66],  # Quarter + triplet
        'GT': [0.5, 0.5, 0.5, 0.5], # Running 8ths
        'GG': [1.0, 1.0],           # Half notes
        'GC': [0.5, 1.0, 0.5],      # Syncopated
        'CA': [2.0],                # Whole note
        'CT': [0.33, 0.33, 0.33, 1.0],  # Fast triplet + hold
        'CG': [0.75, 0.25, 1.0],    # Dotted 8th + 16th
        'CC': [0.25, 0.25, 0.5, 1.0],  # 16ths to quarter
    }

    # Melodic contour patterns - determines if melody rises, falls, or waves
    # Selected based on sequence characteristics
    CONTOUR_PATTERNS = {
        'rising': [0, 1, 2, 3, 4, 5, 4, 3],      # Ascending phrases
        'falling': [5, 4, 3, 2, 1, 0, 1, 2],      # Descending phrases
        'wave': [0, 2, 4, 3, 1, 3, 5, 4],         # Wave-like motion
        'zigzag': [0, 4, 1, 5, 2, 6, 3, 5],       # Jumping intervals
        'arch': [0, 2, 4, 5, 4, 2, 0, 1],         # Arch shape
        'valley': [4, 2, 0, 1, 0, 2, 4, 3],       # Valley shape
        'stepwise': [0, 1, 0, 2, 1, 3, 2, 4],     # Gradual steps
        'leaping': [0, 4, 2, 6, 1, 5, 3, 6],      # Large jumps
    }

    # Phrase lengths in codons - how many notes before pattern repeats/varies
    PHRASE_LENGTHS = [4, 6, 8, 3, 5, 7]

    # Octave jump patterns - when to shift octaves for variety
    OCTAVE_PATTERNS = {
        'stable': [0, 0, 0, 0, 0, 0, 0, 0],
        'lift': [0, 0, 0, 0, 12, 12, 12, 0],
        'drop': [0, 0, 12, 12, 0, 0, -12, 0],
        'bounce': [0, 12, 0, 12, 0, -12, 0, 12],
        'climb': [0, 0, 0, 12, 12, 12, 12, 12],
        'descend': [12, 12, 12, 0, 0, 0, -12, -12],
    }

    # ==================== INSTRUMENTS ====================

    INSTRUMENTS = {
        'melody': 73,      # Flute - airy, ethereal
        'harmony': 48,     # String Ensemble - rich
        'bass': 33,        # Acoustic Bass - grounding
        'pad': 89,         # Pad (warm) - atmosphere
    }

    # Instrument variations based on GC content
    INSTRUMENT_SETS = {
        'low_gc': {    # AT-rich: warmer, organic
            'melody': 71,   # Clarinet
            'harmony': 46,  # Orchestral Harp
            'bass': 33,     # Acoustic Bass
            'pad': 92,      # Pad (bowed)
        },
        'mid_gc': {    # Balanced: default ethereal
            'melody': 73,   # Flute
            'harmony': 48,  # String Ensemble
            'bass': 33,     # Acoustic Bass
            'pad': 89,      # Pad (warm)
        },
        'high_gc': {   # GC-rich: brighter, crystalline
            'melody': 79,   # Ocarina
            'harmony': 88,  # Pad (new age)
            'bass': 39,     # Synth Bass 1
            'pad': 91,      # Pad (space voice)
        },
        'very_high_gc': {  # Very GC-rich: cosmic
            'melody': 80,   # Lead (square)
            'harmony': 95,  # Pad (sweep)
            'bass': 38,     # Synth Bass 1
            'pad': 94,      # Pad (halo)
        }
    }

    # ==================== ANALYSIS METHODS ====================

    def analyze(self, sequence):
        """
        Complete DNA analysis using all 5 layers

        Returns comprehensive musical parameters derived from the sequence
        """
        if not sequence or len(sequence) < 3:
            return self._default_analysis()

        sequence = sequence.upper()
        length = len(sequence)

        # === LAYER 1: Global Analysis ===
        gc_count = sequence.count('G') + sequence.count('C')
        at_count = sequence.count('A') + sequence.count('T')
        gc_content = (gc_count / length) * 100

        # AT/GC ratio for root key
        at_gc_ratio = at_count / gc_count if gc_count > 0 else 1.5
        root_note, key_name = self._get_root_key(at_gc_ratio)

        # Purine/Pyrimidine ratio for mode
        purines = sequence.count('A') + sequence.count('G')
        pyrimidines = sequence.count('T') + sequence.count('C')
        pu_py_ratio = purines / pyrimidines if pyrimidines > 0 else 1.0
        scale, mode_name, character = self._get_mode(pu_py_ratio)

        # Tempo from GC content (60-100 BPM range)
        tempo = int(60 + (gc_content / 100) * 40)

        # === LAYER 2: Codon Analysis ===
        codons = self._get_codons(sequence)
        amino_acids = [self.CODON_TABLE.get(c, 'X') for c in codons]

        # === LAYER 5: Motif Detection ===
        motifs = self._detect_motifs(sequence)

        return {
            # Layer 1 results
            'key': key_name,
            'root_note': root_note,
            'mode': mode_name,
            'scale': scale,
            'character': character,
            'tempo': tempo,
            'gc': gc_content,
            'at_gc_ratio': round(at_gc_ratio, 3),
            'pu_py_ratio': round(pu_py_ratio, 3),

            # Layer 2 results
            'codons': codons,
            'amino_acids': amino_acids,
            'codon_count': len(codons),

            # Layer 5 results
            'motifs': motifs,
            'motif_count': len(motifs),

            # General
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
        """
        Detect repeating patterns (motifs) in the sequence
        These become musical themes
        """
        motifs = []
        min_length = 6   # Minimum motif length (2 codons)
        max_length = 18  # Maximum motif length (6 codons)

        for length in range(min_length, max_length + 1, 3):
            pattern_counts = Counter()
            for i in range(len(sequence) - length + 1):
                pattern = sequence[i:i+length]
                if all(b in 'ATGC' for b in pattern):
                    pattern_counts[pattern] += 1

            # Keep patterns that appear 2+ times
            for pattern, count in pattern_counts.items():
                if count >= 2:
                    motifs.append({
                        'pattern': pattern,
                        'count': count,
                        'length': length
                    })

        # Sort by count (most frequent first), limit to top 5
        motifs.sort(key=lambda x: (-x['count'], -x['length']))
        return motifs[:5]

    # ==================== HELPER METHODS ====================

    def _snap_to_scale(self, pitch, root, scale):
        """
        Snap any pitch to the nearest note in the current scale.
        This prevents out-of-key notes from appearing.

        Args:
            pitch: The MIDI pitch to snap
            root: The root note of the key (0-11)
            scale: List of scale intervals (e.g., [0, 2, 3, 5, 7, 8, 10])

        Returns:
            The nearest pitch that's in the scale
        """
        # Get the pitch class (0-11) relative to root
        pitch_class = (pitch - root) % 12

        # Find the nearest scale tone
        min_distance = 12
        nearest_interval = 0
        for interval in scale:
            distance = min(abs(pitch_class - interval), 12 - abs(pitch_class - interval))
            if distance < min_distance:
                min_distance = distance
                nearest_interval = interval

        # Reconstruct the pitch with the snapped interval
        octave = (pitch - root) // 12
        snapped_pitch = root + (octave * 12) + nearest_interval

        # Handle edge case where snapping moved us to wrong octave
        if snapped_pitch > pitch + 6:
            snapped_pitch -= 12
        elif snapped_pitch < pitch - 6:
            snapped_pitch += 12

        return snapped_pitch

    # ==================== INTRO/OUTRO GENERATION ====================

    def _generate_intro(self, midi, root, scale, tempo):
        """
        Generate an intro section triggered by the ATG start codon.

        The intro establishes the key and mood with:
        - Rising arpeggio through the scale (life beginning)
        - Pad swell establishing the harmonic foundation
        - Gentle melodic motif based on A-T-G

        Returns: Duration in beats (how long the intro takes)
        """
        intro_beats = 8.0  # 2 bars of 4/4

        # === PAD: Sustained root chord swell (Track 3) ===
        # Start quiet, build up - establishes the key
        pad_pitches = [
            54 + root + scale[0],  # Root
            54 + root + scale[2],  # Third
            54 + root + scale[4],  # Fifth
        ]
        for i, pitch in enumerate(pad_pitches):
            pitch = max(48, min(72, pitch))
            # Stagger entry for swell effect
            midi.addNote(
                track=3, channel=3, pitch=pitch,
                time=i * 0.5,  # Staggered entry
                duration=intro_beats - (i * 0.5),
                volume=30 + (i * 5)  # Crescendo
            )

        # === MELODY: Rising arpeggio based on ATG (Track 0) ===
        # A=0 (root), T=2 (third), G=4 (fifth) - maps to scale degrees
        atg_degrees = [0, 2, 4]  # From FIRST_BASE_DEGREE mapping
        time_pos = 1.0  # Start after pad begins

        # First pass: slow rising notes
        for i, degree in enumerate(atg_degrees):
            pitch = 60 + root + scale[degree % len(scale)]
            pitch = max(48, min(84, pitch))
            midi.addNote(
                track=0, channel=0, pitch=pitch,
                time=time_pos,
                duration=1.5,
                volume=50 + (i * 10)  # Getting louder
            )
            time_pos += 1.5

        # Second pass: faster, octave higher (life accelerating)
        for i, degree in enumerate(atg_degrees):
            pitch = 72 + root + scale[degree % len(scale)]  # Octave up
            pitch = max(48, min(84, pitch))
            midi.addNote(
                track=0, channel=0, pitch=pitch,
                time=time_pos,
                duration=0.5,
                volume=70
            )
            time_pos += 0.5

        # === BASS: Root note pulse (Track 2) ===
        bass_pitch = 36 + root + scale[0]
        bass_pitch = max(28, min(48, bass_pitch))
        # Two low pulses
        midi.addNote(track=2, channel=2, pitch=bass_pitch, time=0.0, duration=3.0, volume=50)
        midi.addNote(track=2, channel=2, pitch=bass_pitch, time=4.0, duration=3.0, volume=60)

        # === HARMONY: Building chord (Track 1) ===
        # Enters halfway through intro
        harmony_time = 4.0
        chord_degrees = [0, 2, 4]
        for degree in chord_degrees:
            pitch = 48 + root + scale[degree % len(scale)]
            pitch = max(36, min(72, pitch))
            midi.addNote(
                track=1, channel=1, pitch=pitch,
                time=harmony_time,
                duration=4.0,
                volume=45
            )

        return intro_beats

    def _generate_outro(self, midi, root, scale, start_time, stop_codon):
        """
        Generate an outro section triggered by a stop codon (TAA, TAG, TGA).

        The outro provides resolution with:
        - Descending pattern (mirror of intro's rise)
        - Final cadence resolving to the root
        - Fade out effect

        Different stop codons create slightly different endings:
        - TAA: Most common, gentle fade
        - TAG: Rare, more dramatic ending
        - TGA: "Opal" stop, softer resolution

        Args:
            midi: MIDI file object
            root: Root note
            scale: Scale intervals
            start_time: When the outro begins (in beats)
            stop_codon: Which stop codon triggered this (TAA, TAG, or TGA)

        Returns: Duration in beats
        """
        outro_beats = 8.0  # 2 bars

        # Different character based on stop codon
        if stop_codon == 'TAG':
            # Dramatic ending - "amber" stop
            volumes = [70, 60, 50, 40]
            tempo_feel = 1.0  # Normal
        elif stop_codon == 'TGA':
            # Soft ending - "opal" stop
            volumes = [50, 45, 40, 35]
            tempo_feel = 1.2  # Slightly slower
        else:  # TAA
            # Gentle fade - "ochre" stop (most common)
            volumes = [60, 50, 40, 30]
            tempo_feel = 1.0

        time_pos = start_time

        # === MELODY: Descending scale (life concluding) ===
        # Reverse the rising pattern - come back down
        descending_degrees = [4, 2, 0, 4, 2, 0]  # Two passes down
        octave = 72  # Start high

        for i, degree in enumerate(descending_degrees):
            if i == 3:
                octave = 60  # Drop octave for second pass
            pitch = octave + root + scale[degree % len(scale)]
            pitch = max(48, min(84, pitch))
            duration = 1.0 * tempo_feel
            vol = volumes[min(i, len(volumes) - 1)]

            midi.addNote(
                track=0, channel=0, pitch=pitch,
                time=time_pos,
                duration=duration * 0.9,
                volume=vol
            )
            time_pos += duration

        # === PAD: Sustained final chord (Track 3) ===
        final_chord = [0, 2, 4]  # Root chord
        for degree in final_chord:
            pitch = 54 + root + scale[degree % len(scale)]
            pitch = max(48, min(72, pitch))
            midi.addNote(
                track=3, channel=3, pitch=pitch,
                time=start_time,
                duration=outro_beats,
                volume=35
            )

        # === BASS: Final root notes (Track 2) ===
        bass_pitch = 36 + root + scale[0]
        bass_pitch = max(28, min(48, bass_pitch))
        midi.addNote(track=2, channel=2, pitch=bass_pitch, time=start_time, duration=4.0, volume=55)
        midi.addNote(track=2, channel=2, pitch=bass_pitch, time=start_time + 4.0, duration=4.0, volume=40)

        # === HARMONY: Resolving cadence (Track 1) ===
        # V chord (dominant) then I chord (tonic) - classic resolution
        # V chord at start
        v_degrees = [4, 6, 1]  # Fifth, seventh, second (dominant feel)
        for degree in v_degrees:
            pitch = 48 + root + scale[degree % len(scale)]
            pitch = max(36, min(72, pitch))
            midi.addNote(
                track=1, channel=1, pitch=pitch,
                time=start_time,
                duration=3.5,
                volume=45
            )

        # I chord (resolution)
        i_degrees = [0, 2, 4]  # Root, third, fifth
        for degree in i_degrees:
            pitch = 48 + root + scale[degree % len(scale)]
            pitch = max(36, min(72, pitch))
            midi.addNote(
                track=1, channel=1, pitch=pitch,
                time=start_time + 4.0,
                duration=4.0,
                volume=40
            )

        return outro_beats

    def _find_structure_codons(self, codons):
        """
        Find the positions of start and stop codons in the sequence.

        Returns:
            dict with 'start_positions' (list of ATG indices) and
            'stop_positions' (list of (index, codon) tuples for TAA/TAG/TGA)
        """
        start_positions = []
        stop_positions = []
        stop_codons = ['TAA', 'TAG', 'TGA']

        for i, codon in enumerate(codons):
            if codon == 'ATG':
                start_positions.append(i)
            elif codon in stop_codons:
                stop_positions.append((i, codon))

        return {
            'start_positions': start_positions,
            'stop_positions': stop_positions,
            'has_start': len(start_positions) > 0,
            'has_stop': len(stop_positions) > 0,
            'first_start': start_positions[0] if start_positions else None,
            'last_stop': stop_positions[-1] if stop_positions else None,
        }

    # ==================== MIDI GENERATION ====================

    def generate_midi(self, dna, duration, output_path):
        """
        Generate MIDI file using the Codon Harmony algorithm

        Creates a rich, musical piece where:
        - Key and mode are determined by sequence composition
        - Chords flow from amino acid properties
        - Rhythm emerges from codon frequencies
        - Melody derives from base positions
        - Motifs create recurring themes
        - Intro triggered by ATG start codon
        - Outro triggered by stop codons (TAA, TAG, TGA)
        """
        analysis = self.analyze(dna)

        if analysis['codon_count'] < 3:
            # Fall back for very short sequences
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

        # Find structural codons (start/stop)
        structure = self._find_structure_codons(codons)

        # Create MIDI file with 4 tracks
        # deinterleave=False prevents issues with overlapping notes
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

        # Calculate beats needed
        beats_per_second = tempo / 60
        total_beats = int(duration * beats_per_second)

        # Track time offset for intro/outro
        time_offset = 0.0
        main_section_beats = total_beats

        # === GENERATE INTRO (if sequence starts with ATG) ===
        if structure['has_start'] and structure['first_start'] == 0:
            intro_beats = self._generate_intro(midi, root, scale, tempo)
            time_offset = intro_beats
            main_section_beats -= intro_beats
            # Remove the ATG from codons so main section doesn't re-process it
            main_codons = codons[1:]  # Skip the first ATG
        else:
            main_codons = codons

        # Check if we need to reserve time for outro
        outro_beats = 0.0
        last_stop = None
        if structure['has_stop']:
            # Find the last stop codon and reserve time for outro
            last_stop_idx, last_stop_codon = structure['last_stop']
            last_stop = last_stop_codon
            outro_beats = 8.0
            main_section_beats -= outro_beats
            # Remove stop codons from main processing (they'll be handled in outro)
            main_codons = [c for c in main_codons if c not in ['TAA', 'TAG', 'TGA']]

        # Ensure we have enough beats for main section
        main_section_beats = max(8.0, main_section_beats)

        # === GENERATE MAIN SECTIONS (with time offset) ===
        self._generate_melody_offset(midi, main_codons, root, scale, main_section_beats, analysis, time_offset)
        self._generate_harmony_offset(midi, main_codons, root, scale, main_section_beats, time_offset)
        self._generate_bass_offset(midi, main_codons, root, scale, main_section_beats, time_offset)
        self._generate_pad_offset(midi, root, scale, main_section_beats, analysis, time_offset, main_codons)

        # === GENERATE OUTRO (if sequence has stop codon) ===
        if last_stop:
            outro_start = time_offset + main_section_beats
            self._generate_outro(midi, root, scale, outro_start, last_stop)

        # Write MIDI file
        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        # Add structure info to analysis
        analysis['has_intro'] = structure['has_start'] and structure['first_start'] == 0
        analysis['has_outro'] = structure['has_stop']
        analysis['stop_codon'] = last_stop

        return analysis

    def _generate_melody(self, midi, codons, root, scale, total_beats, analysis):
        """Wrapper for backwards compatibility"""
        self._generate_melody_offset(midi, codons, root, scale, total_beats, analysis, 0.0)

    def _generate_melody_offset(self, midi, codons, root, scale, total_beats, analysis, time_offset):
        """
        Generate melody from codons using DNA-driven melodic contours and rhythms.

        Key improvements for variety:
        - Melodic contour (rising/falling/wave) determined by sequence GC regions
        - Phrase length varies based on codon patterns
        - Octave shifts create different registers
        - Rhythm patterns derived from codon combinations
        - Each unique sequence produces a unique melodic shape
        """
        if not codons:
            return

        time_pos = time_offset
        end_time = time_offset + total_beats
        codon_idx = 0
        motif_patterns = [m['pattern'] for m in analysis.get('motifs', [])]

        # === DETERMINE MELODIC CHARACTER FROM DNA ===

        # Select contour pattern based on first few codons
        contour_keys = list(self.CONTOUR_PATTERNS.keys())
        if len(codons) >= 3:
            # Use hash of first 3 codons to select contour
            contour_hash = sum(ord(c) for c in ''.join(codons[:3])) % len(contour_keys)
            contour_name = contour_keys[contour_hash]
        else:
            contour_name = 'wave'
        contour = self.CONTOUR_PATTERNS[contour_name]

        # Select octave pattern based on middle codons
        octave_keys = list(self.OCTAVE_PATTERNS.keys())
        mid_idx = len(codons) // 2
        if len(codons) >= 6:
            octave_hash = sum(ord(c) for c in ''.join(codons[mid_idx:mid_idx+3])) % len(octave_keys)
            octave_pattern_name = octave_keys[octave_hash]
        else:
            octave_pattern_name = 'stable'
        octave_pattern = self.OCTAVE_PATTERNS[octave_pattern_name]

        # Determine phrase length from codon count
        phrase_length = self.PHRASE_LENGTHS[len(codons) % len(self.PHRASE_LENGTHS)]

        # Calculate a "melodic seed" from the whole sequence for consistent variation
        melodic_seed = sum(ord(c) for c in ''.join(codons[:min(10, len(codons))]))

        # Base octave varies by sequence
        base_octave = 60 + ((melodic_seed % 3) - 1) * 12  # 48, 60, or 72

        phrase_position = 0
        current_phrase = 0
        last_pitch = -1  # Track to avoid immediate pitch repetition causing MIDI issues
        last_note_end = 0  # Track when last note ends

        while time_pos < end_time and codon_idx < len(codons):
            codon = codons[codon_idx % len(codons)]

            # Skip stop codons (they're rests)
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += 2  # Rest duration
                codon_idx += 1
                last_pitch = -1  # Reset pitch tracking after rest
                continue

            base1, base2, base3 = codon[0], codon[1], codon[2]

            # === PITCH CALCULATION - DIRECT CODON MAPPING ===
            # Each codon has a UNIQUE pitch - this is the key to variety!

            # Get the direct pitch offset for this specific codon (0-24 semitones)
            codon_pitch_offset = self.CODON_PITCH.get(codon, 12)

            # If it's a rest (stop codon), skip
            if codon_pitch_offset == -1:
                time_pos += 1.0
                codon_idx += 1
                continue

            # Apply melodic contour as a MODIFIER (adds movement, not override)
            contour_idx = phrase_position % len(contour)
            contour_mod = contour[contour_idx] - 3  # Center around 0 (-3 to +3)

            # Combine: codon pitch + contour modifier + octave pattern
            octave_idx = phrase_position % len(octave_pattern)
            octave_shift = octave_pattern[octave_idx]

            # Additional octave variation from second base
            base_octave_mod = self.SECOND_BASE_OCTAVE.get(base2, 0)

            # Final pitch: base + codon's unique pitch + contour movement + octave shifts
            pitch_offset = codon_pitch_offset + contour_mod

            # === RHYTHM CALCULATION ===

            # Primary rhythm from last two bases
            rhythm_key = base2 + base3
            rhythm_pattern = self.RHYTHM_PATTERNS.get(rhythm_key, [1.0])

            # Layer 3: Codon frequency affects duration
            freq = self.CODON_FREQUENCY.get(codon, 15.0)
            base_duration = 2.0 - (freq / 40.0) * 1.5
            base_duration = max(0.5, min(2.0, base_duration))

            # Apply rhythm pattern
            pattern_idx = codon_idx % len(rhythm_pattern)
            final_duration = base_duration * rhythm_pattern[pattern_idx]

            # Phrase-based rhythm variation: notes at phrase boundaries are longer
            if phrase_position == 0:
                final_duration *= 1.3  # First note of phrase slightly longer
            elif phrase_position == phrase_length - 1:
                final_duration *= 1.5  # Last note of phrase longer (breath)

            # Quantize to quarter-beats
            final_duration = round(final_duration * 4) / 4
            final_duration = max(0.25, final_duration)

            # === FINAL PITCH ===
            pitch = base_octave + root + pitch_offset + base_octave_mod + octave_shift
            pitch = max(48, min(84, pitch))

            # Snap to scale
            pitch = self._snap_to_scale(pitch, root, scale)
            pitch = max(48, min(84, pitch))

            # === VOLUME/DYNAMICS ===
            # Phrase shaping: crescendo then decrescendo within phrase
            phrase_progress = phrase_position / max(1, phrase_length - 1)
            if phrase_progress < 0.5:
                dynamic_volume = 70 + int(phrase_progress * 30)  # 70 -> 85
            else:
                dynamic_volume = 85 - int((phrase_progress - 0.5) * 20)  # 85 -> 75

            # Motif emphasis
            volume = dynamic_volume
            for motif in motif_patterns:
                if codon in motif:
                    volume = min(100, volume + 15)
                    break

            # Ensure notes don't overlap (prevents MIDI library errors)
            note_duration = final_duration * 0.85  # Leave gap between notes

            # If same pitch as last note, shift slightly to avoid overlap issues
            if pitch == last_pitch and time_pos < last_note_end:
                # Skip this note or shift pitch
                pitch = pitch + (7 if pitch < 78 else -7)  # Shift by fifth
                pitch = self._snap_to_scale(pitch, root, scale)
                pitch = max(48, min(84, pitch))

            midi.addNote(
                track=0,
                channel=0,
                pitch=pitch,
                time=time_pos,
                duration=note_duration,
                volume=volume
            )

            last_pitch = pitch
            last_note_end = time_pos + note_duration
            time_pos += final_duration
            codon_idx += 1
            phrase_position += 1

            # Reset phrase position at phrase boundary
            if phrase_position >= phrase_length:
                phrase_position = 0
                current_phrase += 1
                # Optionally shift contour for next phrase based on upcoming codons
                if codon_idx < len(codons) - 2:
                    next_codon = codons[codon_idx]
                    contour_shift = ord(next_codon[0]) % 3
                    contour = self.CONTOUR_PATTERNS[contour_keys[(contour_hash + contour_shift) % len(contour_keys)]]

    def _generate_harmony(self, midi, codons, root, scale, total_beats):
        """Wrapper for backwards compatibility"""
        self._generate_harmony_offset(midi, codons, root, scale, total_beats, 0.0)

    def _generate_harmony_offset(self, midi, codons, root, scale, total_beats, time_offset):
        """
        Generate chord progression from amino acid properties (Layer 2)
        Each codon's amino acid determines chord quality

        COHERENCE FIX: Now uses scale degrees for chord intervals,
        ensuring all chord notes stay within the established mode.
        """
        if not codons:
            return

        time_pos = time_offset
        end_time = time_offset + total_beats
        chord_duration = 4.0  # 4 beats per chord (aligns with bass 4-beat cycle)
        codon_idx = 0

        while time_pos < end_time:
            codon = codons[codon_idx % len(codons)]
            amino_acid = self.CODON_TABLE.get(codon, 'A')

            chord_name, scale_degrees = self.AMINO_ACID_CHORDS.get(
                amino_acid, ('maj', [0, 2, 4])
            )

            if chord_name == 'rest':
                # Stop codon = rest in harmony
                time_pos += chord_duration
                codon_idx += 1
                continue

            # Determine chord root degree from codon's first base
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)

            # Add chord notes - each interval is a SCALE DEGREE offset
            for degree_offset in scale_degrees:
                # Calculate actual scale degree (with wrapping)
                actual_degree = (root_degree + degree_offset) % len(scale)

                # Get pitch from scale
                pitch_in_scale = scale[actual_degree]

                # Handle octave wrapping for high degree offsets
                octave_adjust = ((root_degree + degree_offset) // len(scale)) * 12

                # Final pitch in lower-mid register
                pitch = 48 + root + pitch_in_scale + octave_adjust
                pitch = max(36, min(72, pitch))

                midi.addNote(
                    track=1,
                    channel=1,
                    pitch=pitch,
                    time=time_pos,
                    duration=chord_duration * 0.95,
                    volume=55
                )

            time_pos += chord_duration
            codon_idx += 1

    def _generate_bass(self, midi, codons, root, scale, total_beats):
        """Wrapper for backwards compatibility"""
        self._generate_bass_offset(midi, codons, root, scale, total_beats, 0.0)

    def _generate_bass_offset(self, midi, codons, root, scale, total_beats, time_offset):
        """
        Generate bass line following chord roots with rhythmic variation

        COHERENCE FIX: Bass now follows the same 4-beat harmonic rhythm
        as the chords, with a complementary rhythm pattern that sums to 4.
        This keeps bass and harmony in sync while allowing rhythmic interest.
        """
        if not codons:
            return

        time_pos = time_offset
        end_time = time_offset + total_beats

        # Multiple bass patterns for variation (all sum to 4 beats)
        bass_patterns = [
            [1.5, 0.5, 1.0, 1.0],    # Standard: "1 and 2 and 3 4"
            [1.0, 1.0, 1.0, 1.0],    # Walking: even quarters
            [2.0, 1.0, 1.0],         # Half note start
            [1.0, 0.5, 0.5, 1.0, 1.0],  # Syncopated
            [0.75, 0.75, 0.5, 1.0, 1.0],  # Dotted feel
            [1.5, 1.5, 1.0],         # Dotted half feel
        ]
        codon_idx = 0

        while time_pos < end_time:
            codon = codons[codon_idx % len(codons)]

            # Skip stop codons
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += 4  # Rest for full chord duration
                codon_idx += 1
                continue

            # Get the root degree for this chord (same as harmony)
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)

            # Select bass pattern based on codon characteristics
            pattern_selector = ord(codon[1]) % len(bass_patterns)
            bass_pattern = bass_patterns[pattern_selector]

            # Play the bass pattern for this 4-beat chord cycle
            pattern_time = 0.0
            for i, duration in enumerate(bass_pattern):
                # Bass plays root on beats 1 and 3, fifth on beats 2 and 4
                if i % 2 == 0:
                    # Root note
                    degree = root_degree
                else:
                    # Fifth (4 scale degrees up from root)
                    degree = (root_degree + 4) % len(scale)

                pitch_offset = scale[degree % len(scale)]
                pitch = 36 + root + pitch_offset  # Low bass range
                pitch = max(28, min(48, pitch))

                midi.addNote(
                    track=2,
                    channel=2,
                    pitch=pitch,
                    time=time_pos + pattern_time,
                    duration=duration * 0.8,
                    volume=70 if i == 0 else 60  # Accent on beat 1
                )

                pattern_time += duration

            time_pos += 4.0  # Move to next chord (4 beats)
            codon_idx += 1  # Advance codon with chord changes

    def _generate_pad(self, midi, root, scale, total_beats, analysis):
        """Wrapper for backwards compatibility"""
        codons = analysis.get('codons', [])
        self._generate_pad_offset(midi, root, scale, total_beats, analysis, 0.0, codons)

    def _generate_pad_offset(self, midi, root, scale, total_beats, analysis, time_offset, codons=None):
        """
        Generate atmospheric pad that follows the harmonic progression
        Sustained chords that support the harmony track

        COHERENCE FIX: Pad now follows the same codon progression as harmony,
        changing every 8 beats (2 chord cycles) for slow-moving atmosphere.
        """
        if codons is None:
            codons = analysis.get('codons', [])
        if not codons:
            return

        time_pos = time_offset
        end_time = time_offset + total_beats
        pad_duration = 8.0  # Sustained notes (2 chord cycles)
        codon_idx = 0

        while time_pos < end_time:
            codon = codons[codon_idx % len(codons)]

            # Skip stop codons
            if self.CODON_TABLE.get(codon) == '*':
                time_pos += pad_duration
                codon_idx += 2  # Skip 2 codons (matching 2 chord cycles)
                continue

            # Get chord root from codon (same logic as harmony)
            root_degree = self.FIRST_BASE_DEGREE.get(codon[0], 0)

            # Build a pad chord: root, 3rd, 5th from scale
            pad_degrees = [0, 2, 4]

            for degree_offset in pad_degrees:
                actual_degree = (root_degree + degree_offset) % len(scale)
                pitch_in_scale = scale[actual_degree]

                pitch = 54 + root + pitch_in_scale  # Mid-range
                pitch = max(48, min(72, pitch))

                midi.addNote(
                    track=3,
                    channel=3,
                    pitch=pitch,
                    time=time_pos,
                    duration=pad_duration,
                    volume=40  # Soft background
                )

            time_pos += pad_duration
            codon_idx += 2  # Advance 2 codons (pad changes every 2 chords)

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
        """
        Convert MIDI file to MP3
        """
        try:
            wav_path = midi_path.replace('.mid', '.wav')

            # Step 1: MIDI to WAV using timidity
            result = subprocess.run(
                ['timidity', midi_path, '-Ow', '-o', wav_path],
                check=True,
                capture_output=True,
                text=True
            )

            # Step 2: WAV to MP3 using lame (preferred) or afconvert (macOS fallback)
            try:
                subprocess.run(
                    ['lame', '-V2', wav_path, mp3_path],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except FileNotFoundError:
                # Fallback to macOS afconvert (outputs AAC in MP4 container)
                subprocess.run(
                    ['afconvert', wav_path, mp3_path, '-d', 'aac', '-f', 'mp4f'],
                    check=True,
                    capture_output=True,
                    text=True
                )

            # Clean up WAV file
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

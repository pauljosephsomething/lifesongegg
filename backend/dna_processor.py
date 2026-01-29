"""
DNA Lifesong Studio - DNA Processor v4.0
COMPLETE REWRITE - Direct Codon-to-Note Mapping

The fundamental principle: YOUR DNA SEQUENCE IS YOUR MELODY
- Each of the 64 codons maps to a specific MIDI note
- The order of codons in YOUR sequence = the order of notes in YOUR melody
- Different sequences = completely different melodies

Based on:
- Susumu Ohno (1986) - DNA sequences have musical properties
- The genetic code has 64 codons - we map them across ~2 octaves (24 notes)
"""

import os
import subprocess
from midiutil import MIDIFile


class DNAProcessor:
    """
    Direct Codon-to-Note Mapping

    Simple, deterministic, and YOUR sequence = YOUR unique melody.
    64 codons mapped to 24 chromatic notes (repeated to cover all codons).
    """

    # ==================== THE CODON-TO-NOTE MAP ====================
    # Each codon maps to a MIDI note (48-84 range, ~3 octaves)
    # This is deterministic: same codon = same note, always
    # Organized by first base, then second base, then third base

    CODON_TO_NOTE = {
        # T-- codons (lower register)
        'TTT': 48, 'TTC': 49, 'TTA': 50, 'TTG': 51,
        'TCT': 52, 'TCC': 53, 'TCA': 54, 'TCG': 55,
        'TAT': 56, 'TAC': 57, 'TAA': 0,  'TAG': 0,   # Stop codons = rest
        'TGT': 58, 'TGC': 59, 'TGA': 0,  'TGG': 60,  # Stop codon = rest

        # C-- codons (lower-mid register)
        'CTT': 52, 'CTC': 53, 'CTA': 54, 'CTG': 55,
        'CCT': 56, 'CCC': 57, 'CCA': 58, 'CCG': 59,
        'CAT': 60, 'CAC': 61, 'CAA': 62, 'CAG': 63,
        'CGT': 64, 'CGC': 65, 'CGA': 66, 'CGG': 67,

        # A-- codons (mid-upper register)
        'ATT': 60, 'ATC': 61, 'ATA': 62, 'ATG': 63,  # ATG = start codon
        'ACT': 64, 'ACC': 65, 'ACA': 66, 'ACG': 67,
        'AAT': 68, 'AAC': 69, 'AAA': 70, 'AAG': 71,
        'AGT': 72, 'AGC': 73, 'AGA': 74, 'AGG': 75,

        # G-- codons (upper register)
        'GTT': 64, 'GTC': 65, 'GTA': 66, 'GTG': 67,
        'GCT': 68, 'GCC': 69, 'GCA': 70, 'GCG': 71,
        'GAT': 72, 'GAC': 73, 'GAA': 74, 'GAG': 75,
        'GGT': 76, 'GGC': 77, 'GGA': 78, 'GGG': 79,
    }

    # Duration based on third base (rhythmic variety)
    THIRD_BASE_DURATION = {
        'T': 0.5,   # Short (eighth note)
        'C': 0.75,  # Medium-short
        'A': 1.0,   # Medium (quarter note)
        'G': 1.5,   # Long (dotted quarter)
    }

    # Velocity (volume) based on second base
    SECOND_BASE_VELOCITY = {
        'T': 60,   # Soft
        'C': 75,   # Medium
        'A': 90,   # Loud
        'G': 100,  # Very loud
    }

    # Instruments - simple and clear
    MELODY_INSTRUMENT = 73     # Flute
    BASS_INSTRUMENT = 33       # Acoustic Bass
    PAD_INSTRUMENT = 89        # Warm Pad

    def analyze(self, sequence):
        """Analyze DNA sequence and return musical parameters"""
        if not sequence or len(sequence) < 3:
            return self._default_analysis()

        sequence = sequence.upper().replace(' ', '').replace('\n', '')
        length = len(sequence)

        # Count bases
        a_count = sequence.count('A')
        t_count = sequence.count('T')
        g_count = sequence.count('G')
        c_count = sequence.count('C')

        # GC content determines tempo
        gc_count = g_count + c_count
        gc_content = (gc_count / length) * 100 if length > 0 else 50

        # Tempo: 60-100 BPM based on GC content
        tempo = int(60 + (gc_content / 100) * 40)

        # Key: based on most common base
        base_counts = {'A': a_count, 'T': t_count, 'G': g_count, 'C': c_count}
        dominant_base = max(base_counts, key=base_counts.get)
        key_map = {'A': 'A', 'T': 'D', 'G': 'G', 'C': 'C'}
        key = key_map.get(dominant_base, 'C')

        # Get codons
        codons = [sequence[i:i+3] for i in range(0, len(sequence)-2, 3)]
        codons = [c for c in codons if len(c) == 3]

        return {
            'key': key,
            'tempo': tempo,
            'gc': gc_content,
            'length': length,
            'codon_count': len(codons),
            'codons': codons,
            'mode': 'chromatic',  # We use chromatic mapping
            'character': 'unique',
        }

    def _default_analysis(self):
        return {
            'key': 'C', 'tempo': 72, 'gc': 50.0, 'length': 0,
            'codon_count': 0, 'codons': [], 'mode': 'chromatic', 'character': 'default'
        }

    def generate_midi(self, dna, duration, output_path):
        """
        Generate MIDI from DNA sequence.

        THE CORE PRINCIPLE:
        Each codon in your sequence becomes one note in your melody.
        Different sequences = different melodies. Period.
        """
        analysis = self.analyze(dna)
        codons = analysis['codons']
        tempo = analysis['tempo']

        if not codons:
            return self._generate_empty_midi(output_path, analysis)

        # Create MIDI with 3 tracks: melody, bass, pad
        midi = MIDIFile(3, deinterleave=False)

        # Track 0: Melody (your DNA sequence as notes)
        midi.addTrackName(0, 0, "DNA Melody")
        midi.addTempo(0, 0, tempo)
        midi.addProgramChange(0, 0, 0, self.MELODY_INSTRUMENT)

        # Track 1: Bass (root notes)
        midi.addTrackName(1, 0, "Bass")
        midi.addTempo(1, 0, tempo)
        midi.addProgramChange(1, 1, 0, self.BASS_INSTRUMENT)

        # Track 2: Pad (atmosphere)
        midi.addTrackName(2, 0, "Pad")
        midi.addTempo(2, 0, tempo)
        midi.addProgramChange(2, 2, 0, self.PAD_INSTRUMENT)

        # Calculate how many beats we have
        beats_per_second = tempo / 60
        total_beats = duration * beats_per_second

        # ===== GENERATE MELODY FROM DNA =====
        # This is where YOUR sequence becomes YOUR melody
        time_pos = 0.0
        codon_index = 0

        while time_pos < total_beats and codon_index < len(codons):
            codon = codons[codon_index]

            # Get note from codon
            note = self.CODON_TO_NOTE.get(codon, 60)

            if note == 0:
                # Stop codon = rest
                time_pos += 1.0
                codon_index += 1
                continue

            # Get duration from third base
            third_base = codon[2] if len(codon) == 3 else 'A'
            note_duration = self.THIRD_BASE_DURATION.get(third_base, 1.0)

            # Get velocity from second base
            second_base = codon[1] if len(codon) >= 2 else 'C'
            velocity = self.SECOND_BASE_VELOCITY.get(second_base, 75)

            # Add the note
            midi.addNote(
                track=0,
                channel=0,
                pitch=note,
                time=time_pos,
                duration=note_duration * 0.9,
                volume=velocity
            )

            time_pos += note_duration
            codon_index += 1

            # Loop if we need more music
            if codon_index >= len(codons) and time_pos < total_beats:
                codon_index = 0

        # ===== GENERATE BASS (simple root movement) =====
        bass_time = 0.0
        bass_index = 0
        while bass_time < total_beats:
            # Bass plays every 2 beats
            codon = codons[bass_index % len(codons)]
            note = self.CODON_TO_NOTE.get(codon, 60)
            if note > 0:
                bass_note = 36 + (note % 12)  # Low octave, same pitch class
                midi.addNote(
                    track=1, channel=1, pitch=bass_note,
                    time=bass_time, duration=1.8, volume=70
                )
            bass_time += 2.0
            bass_index += 4  # Jump through codons

        # ===== GENERATE PAD (sustained harmony) =====
        pad_time = 0.0
        pad_index = 0
        while pad_time < total_beats:
            # Pad plays every 4 beats
            codon = codons[pad_index % len(codons)]
            note = self.CODON_TO_NOTE.get(codon, 60)
            if note > 0:
                # Play a simple triad
                midi.addNote(track=2, channel=2, pitch=note-12, time=pad_time, duration=3.8, volume=45)
                midi.addNote(track=2, channel=2, pitch=note-12+4, time=pad_time, duration=3.8, volume=40)
                midi.addNote(track=2, channel=2, pitch=note-12+7, time=pad_time, duration=3.8, volume=40)
            pad_time += 4.0
            pad_index += 8

        # Write MIDI file
        with open(output_path, 'wb') as f:
            midi.writeFile(f)

        return analysis

    def _generate_empty_midi(self, output_path, analysis):
        """Generate a simple MIDI for empty/invalid sequences"""
        midi = MIDIFile(1, deinterleave=False)
        midi.addTrackName(0, 0, "Empty")
        midi.addTempo(0, 0, 72)
        midi.addProgramChange(0, 0, 0, self.MELODY_INSTRUMENT)
        midi.addNote(0, 0, 60, 0, 2, 70)
        with open(output_path, 'wb') as f:
            midi.writeFile(f)
        return analysis

    def convert_to_mp3(self, midi_path, mp3_path):
        """Convert MIDI to MP3 using timidity and lame"""
        try:
            wav_path = midi_path.replace('.mid', '.wav')

            # MIDI to WAV
            result = subprocess.run(
                ['timidity', midi_path, '-Ow', '-o', wav_path],
                check=True, capture_output=True, text=True
            )

            # WAV to MP3
            try:
                subprocess.run(
                    ['lame', '-V2', wav_path, mp3_path],
                    check=True, capture_output=True, text=True
                )
            except FileNotFoundError:
                # macOS fallback
                subprocess.run(
                    ['afconvert', wav_path, mp3_path, '-d', 'aac', '-f', 'mp4f'],
                    check=True, capture_output=True, text=True
                )

            # Cleanup
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

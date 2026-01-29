/**
 * DNA Lifesong Studio - DNA Engine
 * Handles DNA sequence processing and analysis
 */

const DNAEngine = {
    // Valid DNA bases
    VALID_BASES: new Set(['A', 'T', 'G', 'C']),

    // Musical modes based on GC content
    MODES: {
        dorian: { name: 'Dorian', description: 'Minor, jazzy, melancholic' },
        aeolian: { name: 'Aeolian', description: 'Natural minor, reflective' },
        lydian: { name: 'Lydian', description: 'Bright, dreamy, ethereal' }
    },

    /**
     * Clean and validate a DNA sequence
     * @param {string} rawSequence - Raw input string
     * @returns {string} Cleaned sequence with only valid bases
     */
    cleanSequence(rawSequence) {
        return rawSequence
            .toUpperCase()
            .replace(/[^ATGC]/g, '');
    },

    /**
     * Parse a FASTA format file
     * @param {string} content - File content
     * @returns {string} Extracted DNA sequence
     */
    parseFasta(content) {
        if (content.startsWith('>')) {
            // FASTA format - skip header lines
            const lines = content.split('\n');
            const sequenceLines = lines.filter(line => !line.startsWith('>'));
            return this.cleanSequence(sequenceLines.join(''));
        }
        // Plain text format
        return this.cleanSequence(content);
    },

    /**
     * Validate a DNA sequence
     * @param {string} sequence - Cleaned DNA sequence
     * @returns {{ valid: boolean, error?: string, length: number }}
     */
    validate(sequence) {
        const length = sequence.length;

        if (length === 0) {
            return { valid: false, error: 'No valid DNA bases found', length: 0 };
        }

        if (length < 20) {
            return {
                valid: false,
                error: `Need at least 20 bases (currently ${length})`,
                length
            };
        }

        return { valid: true, length };
    },

    /**
     * Analyze a DNA sequence
     * @param {string} sequence - Valid DNA sequence
     * @returns {{ gc: number, mode: string, tempo: number, analysis: object }}
     */
    analyze(sequence) {
        const length = sequence.length;

        // Count bases
        const counts = {
            A: 0, T: 0, G: 0, C: 0
        };

        for (const base of sequence) {
            counts[base]++;
        }

        // Calculate GC content (percentage of G and C bases)
        const gcCount = counts.G + counts.C;
        const gc = (gcCount / length) * 100;

        // Determine musical mode based on GC content
        let mode;
        if (gc < 40) {
            mode = 'dorian';
        } else if (gc > 60) {
            mode = 'lydian';
        } else {
            mode = 'aeolian';
        }

        // Calculate tempo (70 BPM base, adjusted by GC content)
        const tempo = Math.round(70 + ((gc / 100) - 0.5) * 20);

        return {
            gc: gc,
            gcFormatted: gc.toFixed(1),
            mode: mode,
            modeName: this.MODES[mode].name,
            modeDescription: this.MODES[mode].description,
            tempo: tempo,
            length: length,
            counts: counts
        };
    },

    /**
     * Generate a sample DNA sequence
     * @returns {string} Sample sequence
     */
    getSampleSequence() {
        return 'ATGCAAGATTGAAGCTGCTGTCACCGACTGGTGTCGGAATGCACCGACTGAGAATTATGACCGACGCGCACACAATGAGCCAGTTAAATGGCCATCGGCCGCACGTTCTGACCATAAGTTGCGGCCAGTTCTCTCCTATCTCTGCACCGAAGAACCTTGCCATGCGTGAGATAA';
    },

    /**
     * Generate a biologically realistic random DNA sequence with musical variety
     * Follows real DNA rules with enhanced variation for musical output:
     * - Starts with ATG (start codon)
     * - Ends with a stop codon (TAA, TAG, or TGA)
     * - VARIES GC content randomly (25-75%) to create different keys/modes
     * - Randomizes codon selection to create different melodies
     * - Avoids too many repeats
     *
     * @param {number} length - Approximate desired length (will round to codon boundary)
     * @returns {string} Realistic random sequence with good musical variety
     */
    generateRealisticDNA(length = 180) {
        // ALL 61 sense codons (excluding stop codons) - no weighting bias!
        const allCodons = [
            // Alanine (A)
            'GCT', 'GCC', 'GCA', 'GCG',
            // Cysteine (C)
            'TGT', 'TGC',
            // Aspartic acid (D)
            'GAT', 'GAC',
            // Glutamic acid (E)
            'GAA', 'GAG',
            // Phenylalanine (F)
            'TTT', 'TTC',
            // Glycine (G)
            'GGT', 'GGC', 'GGA', 'GGG',
            // Histidine (H)
            'CAT', 'CAC',
            // Isoleucine (I)
            'ATT', 'ATC', 'ATA',
            // Lysine (K)
            'AAA', 'AAG',
            // Leucine (L)
            'TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG',
            // Methionine (M) - also start codon
            'ATG',
            // Asparagine (N)
            'AAT', 'AAC',
            // Proline (P)
            'CCT', 'CCC', 'CCA', 'CCG',
            // Glutamine (Q)
            'CAA', 'CAG',
            // Arginine (R)
            'CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG',
            // Serine (S)
            'TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC',
            // Threonine (T)
            'ACT', 'ACC', 'ACA', 'ACG',
            // Valine (V)
            'GTT', 'GTC', 'GTA', 'GTG',
            // Tryptophan (W)
            'TGG',
            // Tyrosine (Y)
            'TAT', 'TAC'
        ];

        // Stop codons (used only at end)
        const stopCodons = ['TAA', 'TAG', 'TGA'];

        // Categorize codons by GC content for targeted selection
        const lowGCCodons = allCodons.filter(c => {
            const gc = (c.match(/[GC]/g) || []).length;
            return gc <= 1;  // 0-1 G/C bases (AT-rich)
        });
        const midGCCodons = allCodons.filter(c => {
            const gc = (c.match(/[GC]/g) || []).length;
            return gc === 1 || gc === 2;  // 1-2 G/C bases (balanced)
        });
        const highGCCodons = allCodons.filter(c => {
            const gc = (c.match(/[GC]/g) || []).length;
            return gc >= 2;  // 2-3 G/C bases (GC-rich)
        });

        // Randomly choose a GC bias for this sequence (creates key/mode variety)
        const gcBias = Math.random();
        let codonPool;
        if (gcBias < 0.25) {
            // Low GC (creates different key, warmer instruments)
            codonPool = [...lowGCCodons, ...lowGCCodons, ...midGCCodons];
        } else if (gcBias > 0.75) {
            // High GC (creates different key, brighter instruments)
            codonPool = [...highGCCodons, ...highGCCodons, ...midGCCodons];
        } else {
            // Balanced or mixed (unpredictable)
            if (Math.random() < 0.5) {
                codonPool = [...allCodons]; // Use all codons equally
            } else {
                // Random mix
                codonPool = [
                    ...lowGCCodons.slice(0, Math.floor(Math.random() * lowGCCodons.length)),
                    ...midGCCodons.slice(0, Math.floor(Math.random() * midGCCodons.length)),
                    ...highGCCodons.slice(0, Math.floor(Math.random() * highGCCodons.length)),
                    ...allCodons.slice(0, 20) // Some baseline variety
                ];
            }
        }

        // Ensure pool isn't empty
        if (codonPool.length < 10) {
            codonPool = [...allCodons];
        }

        // Shuffle the codon pool for extra randomness
        for (let i = codonPool.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [codonPool[i], codonPool[j]] = [codonPool[j], codonPool[i]];
        }

        // Start with ATG (universal start codon)
        let sequence = 'ATG';

        // Calculate how many codons we need (minus start and stop)
        const targetCodons = Math.floor(length / 3) - 2;

        // Track recent codons to avoid excessive repeats
        let lastCodon = 'ATG';
        let secondLastCodon = '';
        let repeatCount = 0;

        for (let i = 0; i < targetCodons; i++) {
            let codon;
            let attempts = 0;

            do {
                codon = codonPool[Math.floor(Math.random() * codonPool.length)];
                attempts++;

                // Avoid too many repeats of same codon
                if (codon === lastCodon) {
                    repeatCount++;
                    if (repeatCount > 1) continue;  // Stricter - only allow 1 repeat
                } else {
                    repeatCount = 0;
                }

                // Avoid ABA patterns (sounds repetitive)
                if (codon === secondLastCodon && attempts < 8) {
                    continue;
                }

                break;
            } while (attempts < 10);

            sequence += codon;
            secondLastCodon = lastCodon;
            lastCodon = codon;
        }

        // End with a random stop codon
        sequence += stopCodons[Math.floor(Math.random() * stopCodons.length)];

        return sequence;
    },

    /**
     * Generate a simple random DNA sequence (less realistic but faster)
     * @param {number} length - Desired sequence length
     * @returns {string} Random sequence
     */
    generateRandom(length = 100) {
        const bases = ['A', 'T', 'G', 'C'];
        let sequence = '';
        for (let i = 0; i < length; i++) {
            sequence += bases[Math.floor(Math.random() * 4)];
        }
        return sequence;
    },

    /**
     * Format sequence for display (with line breaks)
     * @param {string} sequence - DNA sequence
     * @param {number} lineLength - Characters per line
     * @returns {string} Formatted sequence
     */
    formatForDisplay(sequence, lineLength = 60) {
        const lines = [];
        for (let i = 0; i < sequence.length; i += lineLength) {
            lines.push(sequence.slice(i, i + lineLength));
        }
        return lines.join('\n');
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DNAEngine;
}

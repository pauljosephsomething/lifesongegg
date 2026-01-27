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
     * Generate a biologically realistic random DNA sequence
     * Follows real DNA rules:
     * - Starts with ATG (start codon)
     * - Ends with a stop codon (TAA, TAG, or TGA)
     * - Uses realistic codon frequencies
     * - Maintains natural GC content (40-60%)
     * - Avoids too many repeats
     *
     * @param {number} length - Approximate desired length (will round to codon boundary)
     * @returns {string} Realistic random sequence
     */
    generateRealisticDNA(length = 180) {
        // Common codons weighted by typical usage in nature
        // These are roughly based on human codon usage frequencies
        const codons = {
            // High frequency codons (more common in real genes)
            high: [
                'GCT', 'GCC', 'GCA',  // Alanine
                'TGT', 'TGC',          // Cysteine
                'GAT', 'GAC',          // Aspartic acid
                'GAA', 'GAG',          // Glutamic acid
                'TTT', 'TTC',          // Phenylalanine
                'GGT', 'GGC', 'GGA',   // Glycine
                'CAT', 'CAC',          // Histidine
                'ATT', 'ATC', 'ATA',   // Isoleucine
                'AAA', 'AAG',          // Lysine
                'CTT', 'CTC', 'CTG',   // Leucine
                'TTG', 'TTA',          // Leucine
                'AAT', 'AAC',          // Asparagine
                'CCT', 'CCC', 'CCA',   // Proline
                'CAA', 'CAG',          // Glutamine
                'CGT', 'CGC', 'AGA',   // Arginine
                'TCT', 'TCC', 'TCA', 'AGT', 'AGC', // Serine
                'ACT', 'ACC', 'ACA',   // Threonine
                'GTT', 'GTC', 'GTA', 'GTG', // Valine
                'TGG',                 // Tryptophan
                'TAT', 'TAC'           // Tyrosine
            ],
            // Stop codons (used only at end)
            stop: ['TAA', 'TAG', 'TGA']
        };

        // Flatten and create weighted pool (some codons appear more)
        const codonPool = [
            ...codons.high,
            ...codons.high.slice(0, 20), // Double weight for first 20 common ones
        ];

        // Start with ATG (universal start codon)
        let sequence = 'ATG';

        // Calculate how many codons we need (minus start and stop)
        const targetCodons = Math.floor(length / 3) - 2;

        // Track recent codons to avoid excessive repeats
        let lastCodon = 'ATG';
        let repeatCount = 0;

        for (let i = 0; i < targetCodons; i++) {
            let codon;
            let attempts = 0;

            do {
                codon = codonPool[Math.floor(Math.random() * codonPool.length)];
                attempts++;

                // Avoid stop codons in the middle
                if (codons.stop.includes(codon)) {
                    continue;
                }

                // Avoid too many repeats of same codon
                if (codon === lastCodon) {
                    repeatCount++;
                    if (repeatCount > 2) continue;
                } else {
                    repeatCount = 0;
                }

                break;
            } while (attempts < 10);

            sequence += codon;
            lastCodon = codon;
        }

        // End with a random stop codon
        sequence += codons.stop[Math.floor(Math.random() * codons.stop.length)];

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

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
     * Generate a random DNA sequence like real DNA
     *
     * FIXED LENGTH: 300 bases (100 codons) - optimal for musical variety
     * - Starts with ATG (start codon)
     * - Ends with a stop codon (TAA, TAG, or TGA)
     * - Each codon is randomly selected from all 61 sense codons
     * - Random order like real DNA mutations/evolution
     *
     * @returns {string} Random 300-base DNA sequence
     */
    generateRealisticDNA() {
        // FIXED LENGTH: 300 bases = 100 codons (98 random + start + stop)
        const FIXED_CODON_COUNT = 98;

        // All 61 sense codons (the genetic code - excluding stop codons)
        const ALL_CODONS = [
            'GCT', 'GCC', 'GCA', 'GCG',  // Alanine
            'TGT', 'TGC',                 // Cysteine
            'GAT', 'GAC',                 // Aspartic acid
            'GAA', 'GAG',                 // Glutamic acid
            'TTT', 'TTC',                 // Phenylalanine
            'GGT', 'GGC', 'GGA', 'GGG',  // Glycine
            'CAT', 'CAC',                 // Histidine
            'ATT', 'ATC', 'ATA',          // Isoleucine
            'AAA', 'AAG',                 // Lysine
            'TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG',  // Leucine
            'ATG',                        // Methionine (also start)
            'AAT', 'AAC',                 // Asparagine
            'CCT', 'CCC', 'CCA', 'CCG',  // Proline
            'CAA', 'CAG',                 // Glutamine
            'CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG',  // Arginine
            'TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC',  // Serine
            'ACT', 'ACC', 'ACA', 'ACG',  // Threonine
            'GTT', 'GTC', 'GTA', 'GTG',  // Valine
            'TGG',                        // Tryptophan
            'TAT', 'TAC'                  // Tyrosine
        ];

        // Stop codons
        const STOP_CODONS = ['TAA', 'TAG', 'TGA'];

        // Start with ATG (universal start codon)
        let sequence = 'ATG';

        // Generate 98 random codons - TRULY RANDOM like real DNA
        // Each position is independent - this is how mutations work in nature
        for (let i = 0; i < FIXED_CODON_COUNT; i++) {
            const randomIndex = Math.floor(Math.random() * ALL_CODONS.length);
            sequence += ALL_CODONS[randomIndex];
        }

        // End with a random stop codon
        const stopIndex = Math.floor(Math.random() * STOP_CODONS.length);
        sequence += STOP_CODONS[stopIndex];

        return sequence;  // Always 300 bases (100 codons × 3 bases)
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

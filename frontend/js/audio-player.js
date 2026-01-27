/**
 * DNA Lifesong Studio - Audio Player
 * Handles audio playback for both original and cover tracks
 */

const AudioPlayer = {
    // Audio elements
    originalPlayer: null,
    coverPlayer: null,

    // Current state
    state: {
        originalPlaying: false,
        coverPlaying: false,
        originalFile: null,
        coverFile: null
    },

    // Callbacks
    callbacks: {
        onOriginalStateChange: null,
        onCoverStateChange: null,
        onError: null
    },

    /**
     * Initialize the audio players
     */
    init() {
        this.originalPlayer = new Audio();
        this.coverPlayer = new Audio();

        // Set up event listeners for original player
        this.originalPlayer.addEventListener('ended', () => {
            this.state.originalPlaying = false;
            if (this.callbacks.onOriginalStateChange) {
                this.callbacks.onOriginalStateChange(false);
            }
        });

        this.originalPlayer.addEventListener('error', (e) => {
            this.state.originalPlaying = false;
            if (this.callbacks.onError) {
                this.callbacks.onError('original', e);
            }
        });

        // Set up event listeners for cover player
        this.coverPlayer.addEventListener('ended', () => {
            this.state.coverPlaying = false;
            if (this.callbacks.onCoverStateChange) {
                this.callbacks.onCoverStateChange(false);
            }
        });

        this.coverPlayer.addEventListener('error', (e) => {
            this.state.coverPlaying = false;
            if (this.callbacks.onError) {
                this.callbacks.onError('cover', e);
            }
        });
    },

    /**
     * Set callback functions
     * @param {object} callbacks - Callback functions
     */
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks };
    },

    /**
     * Set the original track file
     * @param {string} filename - Audio filename
     */
    setOriginalFile(filename) {
        this.state.originalFile = filename;
    },

    /**
     * Set the cover track file
     * @param {string} filename - Audio filename
     */
    setCoverFile(filename) {
        this.state.coverFile = filename;
    },

    /**
     * Toggle playback of the original track
     * @returns {boolean} New playing state
     */
    toggleOriginal() {
        if (!this.state.originalFile) {
            if (this.callbacks.onError) {
                this.callbacks.onError('original', new Error('No audio file loaded'));
            }
            return false;
        }

        if (this.state.originalPlaying) {
            this.stopOriginal();
            return false;
        } else {
            this.playOriginal();
            return true;
        }
    },

    /**
     * Play the original track
     */
    playOriginal() {
        // Stop cover if playing
        if (this.state.coverPlaying) {
            this.stopCover();
        }

        this.originalPlayer.src = `/api/audio/${encodeURIComponent(this.state.originalFile)}`;
        this.originalPlayer.play()
            .then(() => {
                this.state.originalPlaying = true;
                if (this.callbacks.onOriginalStateChange) {
                    this.callbacks.onOriginalStateChange(true);
                }
            })
            .catch((err) => {
                if (this.callbacks.onError) {
                    this.callbacks.onError('original', err);
                }
            });
    },

    /**
     * Stop the original track
     */
    stopOriginal() {
        this.originalPlayer.pause();
        this.originalPlayer.currentTime = 0;
        this.state.originalPlaying = false;
        if (this.callbacks.onOriginalStateChange) {
            this.callbacks.onOriginalStateChange(false);
        }
    },

    /**
     * Toggle playback of the cover track
     * @returns {boolean} New playing state
     */
    toggleCover() {
        if (!this.state.coverFile) {
            if (this.callbacks.onError) {
                this.callbacks.onError('cover', new Error('No cover file loaded'));
            }
            return false;
        }

        if (this.state.coverPlaying) {
            this.stopCover();
            return false;
        } else {
            this.playCover();
            return true;
        }
    },

    /**
     * Play the cover track
     */
    playCover() {
        // Stop original if playing
        if (this.state.originalPlaying) {
            this.stopOriginal();
        }

        this.coverPlayer.src = `/api/audio/${encodeURIComponent(this.state.coverFile)}`;
        this.coverPlayer.play()
            .then(() => {
                this.state.coverPlaying = true;
                if (this.callbacks.onCoverStateChange) {
                    this.callbacks.onCoverStateChange(true);
                }
            })
            .catch((err) => {
                if (this.callbacks.onError) {
                    this.callbacks.onError('cover', err);
                }
            });
    },

    /**
     * Stop the cover track
     */
    stopCover() {
        this.coverPlayer.pause();
        this.coverPlayer.currentTime = 0;
        this.state.coverPlaying = false;
        if (this.callbacks.onCoverStateChange) {
            this.callbacks.onCoverStateChange(false);
        }
    },

    /**
     * Stop all playback
     */
    stopAll() {
        this.stopOriginal();
        this.stopCover();
    },

    /**
     * Check if original is playing
     * @returns {boolean}
     */
    isOriginalPlaying() {
        return this.state.originalPlaying;
    },

    /**
     * Check if cover is playing
     * @returns {boolean}
     */
    isCoverPlaying() {
        return this.state.coverPlaying;
    },

    /**
     * Check if original file is loaded
     * @returns {boolean}
     */
    hasOriginal() {
        return !!this.state.originalFile;
    },

    /**
     * Check if cover file is loaded
     * @returns {boolean}
     */
    hasCover() {
        return !!this.state.coverFile;
    },

    /**
     * Reset all state
     */
    reset() {
        this.stopAll();
        this.state.originalFile = null;
        this.state.coverFile = null;
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioPlayer;
}

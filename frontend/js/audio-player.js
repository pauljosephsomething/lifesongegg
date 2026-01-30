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
        coverFile: null,
        suppressErrors: false  // Flag to suppress errors during cleanup
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
            // Don't fire error callback if we're suppressing errors (during cleanup)
            if (this.callbacks.onError && !this.state.suppressErrors) {
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
            // Don't fire error callback if we're suppressing errors (during cleanup)
            if (this.callbacks.onError && !this.state.suppressErrors) {
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
        try {
            this.originalPlayer.pause();
            this.originalPlayer.currentTime = 0;
            // Suppress errors during cleanup to prevent spurious error messages
            this.state.suppressErrors = true;
            this.originalPlayer.src = '';
            this.originalPlayer.load();
            // Re-enable errors after a tick
            setTimeout(() => { this.state.suppressErrors = false; }, 100);
        } catch (e) {
            console.warn('Error stopping original player:', e);
        }
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
        try {
            this.coverPlayer.pause();
            this.coverPlayer.currentTime = 0;
            // Only clear source if there was one playing (prevents error on empty stop)
            if (this.state.coverPlaying) {
                // Remove error listener temporarily to prevent spurious error on source clear
                const errorHandler = this.coverPlayer.onerror;
                this.coverPlayer.onerror = null;
                this.coverPlayer.src = '';
                this.coverPlayer.load();
                // Restore error handler after a tick
                setTimeout(() => { this.coverPlayer.onerror = errorHandler; }, 100);
            }
        } catch (e) {
            console.warn('Error stopping cover player:', e);
        }
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

/**
 * DNA Lifesong Studio - API Client
 * Handles all communication with the backend server
 */

const APIClient = {
    // Base URL for API calls
    baseUrl: '',

    // User access key for authentication
    userKey: null,

    // Request timeout (ms)
    timeout: 300000,

    /**
     * Set the base URL for API calls
     * @param {string} url - Base URL
     */
    setBaseUrl(url) {
        this.baseUrl = url;
    },

    /**
     * Set the user access key for authentication
     * @param {string} key - User access key
     */
    setUserKey(key) {
        this.userKey = key;
    },

    /**
     * Make an API request
     * @param {string} endpoint - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise<object>} Response data
     */
    async request(endpoint, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        // Build headers with optional API key
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.userKey) {
            headers['X-User-Key'] = this.userKey;
        }

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                signal: controller.signal,
                headers
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            clearTimeout(timeoutId);

            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    },

    /**
     * Generate DNA music
     * @param {string} dna - DNA sequence
     * @param {number} duration - Duration in seconds
     * @returns {Promise<object>} Generation result
     */
    async generateMusic(dna, duration) {
        return this.request('/api/generate', {
            method: 'POST',
            body: JSON.stringify({ dna, duration })
        });
    },

    /**
     * Upload MP3 to MusicAPI
     * @param {string} filePath - Path to MP3 file
     * @returns {Promise<object>} Upload result with clip_id
     */
    async uploadToMusicAPI(filePath) {
        return this.request('/api/upload', {
            method: 'POST',
            body: JSON.stringify({ file_path: filePath })
        });
    },

    /**
     * Create AI cover
     * @param {string} clipId - Clip ID from upload
     * @param {string} prompt - AI prompt
     * @param {string} tags - Tags for the cover
     * @returns {Promise<object>} Creation result with task_id
     */
    async createCover(clipId, prompt, tags) {
        return this.request('/api/create_cover', {
            method: 'POST',
            body: JSON.stringify({
                clip_id: clipId,
                prompt: prompt,
                tags: tags
            })
        });
    },

    /**
     * Wait for cover generation to complete
     * @param {string} taskId - Task ID from creation
     * @param {function} onProgress - Progress callback (0-100)
     * @param {function} checkCancelled - Function to check if cancelled
     * @returns {Promise<object>} Result with audio_url
     */
    async waitForCover(taskId, onProgress, checkCancelled) {
        const maxAttempts = 40;
        const pollInterval = 5000;

        for (let i = 0; i < maxAttempts; i++) {
            // Check if cancelled
            if (checkCancelled && checkCancelled()) {
                throw new Error('Cancelled by user');
            }

            try {
                const result = await this.request('/api/check_cover', {
                    method: 'POST',
                    body: JSON.stringify({ task_id: taskId })
                });

                // Update progress
                if (onProgress) {
                    const progress = Math.min(10 + (i * 2.25), 95);
                    onProgress(progress);
                }

                if (result.state === 'succeeded') {
                    if (onProgress) onProgress(100);
                    return result;
                }

                if (result.state === 'failed') {
                    throw new Error(result.error || 'Cover generation failed');
                }

                // Still processing - wait and retry
                await new Promise(resolve => setTimeout(resolve, pollInterval));
            } catch (error) {
                // Re-throw cancellation
                if (error.message === 'Cancelled by user') {
                    throw error;
                }
                // Log but continue polling for other errors
                console.warn('Poll error:', error.message);
                await new Promise(resolve => setTimeout(resolve, pollInterval));
            }
        }

        throw new Error('Timeout waiting for cover generation');
    },

    /**
     * Download generated cover
     * @param {string} audioUrl - URL of the generated audio
     * @returns {Promise<object>} Download result with path and filename
     */
    async downloadCover(audioUrl) {
        return this.request('/api/download', {
            method: 'POST',
            body: JSON.stringify({ audio_url: audioUrl })
        });
    },

    /**
     * Check server health
     * @returns {Promise<object>} Health status
     */
    async checkHealth() {
        try {
            const headers = {};
            if (this.userKey) {
                headers['X-User-Key'] = this.userKey;
            }
            const response = await fetch(`${this.baseUrl}/api/health`, {
                method: 'GET',
                headers
            });
            return await response.json();
        } catch (error) {
            return { healthy: false, error: error.message };
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}

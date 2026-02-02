/**
 * DNA Lifesong Studio - Main Application
 * Orchestrates all modules and handles UI interactions
 */

const App = {
    // State
    state: {
        mood: null,
        style: null,  // 'electronic', 'folk', or 'classical'
        vocalType: 'none',  // 'none', 'female', or 'male'
        mp3Path: null,
        mp3Filename: null,
        coverPath: null,
        coverFilename: null,
        isGenerating: false,
        isCreatingCover: false,
        cancelRequested: false,
        isLoggedIn: false
    },

    // DOM Elements (cached on init)
    elements: {},

    /**
     * Initialize the application
     */
    init() {
        // Check login first
        this.checkLogin();

        this.cacheElements();
        this.setupEventListeners();
        this.setupLoginListeners();
        this.initModules();
        this.initParticles();
        this.loadSettings();
        this.updatePromptPreview();

        console.log('DNA Lifesong Studio initialized');
    },

    /**
     * Check if user is already logged in
     */
    checkLogin() {
        const savedKey = localStorage.getItem('user_access_key');
        if (savedKey) {
            this.state.isLoggedIn = true;
            this.hideLoginOverlay();
        }
    },

    /**
     * Setup login event listeners
     */
    setupLoginListeners() {
        const loginBtn = document.getElementById('loginBtn');
        const loginInput = document.getElementById('loginCodeInput');
        const loginError = document.getElementById('loginError');

        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.attemptLogin());
        }

        if (loginInput) {
            loginInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.attemptLogin();
                }
                // Hide error on typing
                if (loginError) loginError.classList.add('hidden');
            });
        }
    },

    /**
     * Attempt to login with access code
     */
    async attemptLogin() {
        const loginInput = document.getElementById('loginCodeInput');
        const loginError = document.getElementById('loginError');
        const loginBtn = document.getElementById('loginBtn');
        const code = loginInput ? loginInput.value.trim() : '';

        if (!code) {
            if (loginError) {
                loginError.textContent = 'Please enter an access code';
                loginError.classList.remove('hidden');
            }
            return;
        }

        // Disable button while checking
        if (loginBtn) {
            loginBtn.disabled = true;
            loginBtn.textContent = 'Verifying...';
        }

        try {
            // Validate the code against the backend
            const response = await fetch('/api/validate-key', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-User-Key': code
                },
                body: JSON.stringify({ key: code })
            });

            const result = await response.json();

            if (result.valid) {
                // Save the access key
                localStorage.setItem('user_access_key', code);
                APIClient.setUserKey(code);
                this.state.isLoggedIn = true;
                this.hideLoginOverlay();
                this.showToast('Welcome to DNA Lifesong Studio!', 'success');
            } else {
                if (loginError) {
                    loginError.textContent = 'Invalid access code';
                    loginError.classList.remove('hidden');
                }
            }
        } catch (error) {
            // If validation endpoint doesn't exist yet, allow any code (for demo)
            console.warn('Validation endpoint not available, allowing login');
            localStorage.setItem('user_access_key', code);
            APIClient.setUserKey(code);
            this.state.isLoggedIn = true;
            this.hideLoginOverlay();
            this.showToast('Welcome to DNA Lifesong Studio!', 'success');
        } finally {
            if (loginBtn) {
                loginBtn.disabled = false;
                loginBtn.textContent = 'Enter';
            }
        }
    },

    /**
     * Hide the login overlay and unblur app
     */
    hideLoginOverlay() {
        const overlay = document.getElementById('loginOverlay');
        const appContainer = document.getElementById('appContainer');
        const appFooter = document.getElementById('appFooter');

        if (overlay) overlay.classList.add('hidden');
        if (appContainer) appContainer.classList.remove('blurred');
        if (appFooter) appFooter.classList.remove('blurred');
    },

    /**
     * Show the login overlay (for logout)
     */
    showLoginOverlay() {
        const overlay = document.getElementById('loginOverlay');
        const appContainer = document.getElementById('appContainer');
        const appFooter = document.getElementById('appFooter');

        if (overlay) overlay.classList.remove('hidden');
        if (appContainer) appContainer.classList.add('blurred');
        if (appFooter) appFooter.classList.add('blurred');
    },

    /**
     * Logout user
     */
    logout() {
        localStorage.removeItem('user_access_key');
        this.state.isLoggedIn = false;
        this.showLoginOverlay();
        const loginInput = document.getElementById('loginCodeInput');
        if (loginInput) loginInput.value = '';
    },

    /**
     * Cache DOM elements for performance
     */
    cacheElements() {
        this.elements = {
            // Step 1
            dnaInput: document.getElementById('dnaInput'),
            baseCount: document.getElementById('baseCount'),
            durationSlider: document.getElementById('durationSlider'),
            durationValue: document.getElementById('durationValue'),
            generateBtn: document.getElementById('generateBtn'),
            playOriginalBtn: document.getElementById('playOriginalBtn'),
            downloadOriginalBtn: document.getElementById('downloadOriginalBtn'),
            analysisResult: document.getElementById('analysisResult'),
            analysisContent: document.getElementById('analysisContent'),

            // Step 2
            step2Status: document.getElementById('step2Status'),
            moodOrbs: document.querySelectorAll('.orb-btn'),
            styleOrbs: document.querySelectorAll('.style-btn'),
            vocalOrbs: document.querySelectorAll('.vocal-btn'),
            promptPreview: document.getElementById('promptPreview'),
            createCoverBtn: document.getElementById('createCoverBtn'),
            cancelBtn: document.getElementById('cancelBtn'),
            playCoverBtn: document.getElementById('playCoverBtn'),
            downloadCoverBtn: document.getElementById('downloadCoverBtn'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText'),
            statusLog: document.getElementById('statusLog'),

            // Other
            fileInput: document.getElementById('fileInput'),
            settingsBtn: document.getElementById('settingsBtn'),
            settingsModal: document.getElementById('settingsModal'),
            userKeyInput: document.getElementById('userKeyInput'),
            saveSettingsBtn: document.getElementById('saveSettingsBtn'),
            closeSettingsBtn: document.getElementById('closeSettingsBtn'),
            toastContainer: document.getElementById('toastContainer'),
            particles: document.getElementById('particles')
        };
    },

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // DNA input
        this.elements.dnaInput.addEventListener('input', () => this.onDNAInput());

        // File buttons
        document.getElementById('loadFileBtn').addEventListener('click', () => this.loadFile());
        document.getElementById('randomBtn').addEventListener('click', () => this.generateRandomDNA());
        document.getElementById('saveBtn').addEventListener('click', () => this.saveSequence());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearSequence());

        // File input change
        this.elements.fileInput.addEventListener('change', (e) => this.onFileSelected(e));

        // Duration slider
        this.elements.durationSlider.addEventListener('input', () => this.onDurationChange());

        // Generate button
        this.elements.generateBtn.addEventListener('click', () => this.generateMusic());

        // Play original button
        this.elements.playOriginalBtn.addEventListener('click', () => this.togglePlayOriginal());

        // Download original button
        this.elements.downloadOriginalBtn.addEventListener('click', () => this.downloadOriginal());

        // Mood orbs
        this.elements.moodOrbs.forEach(orb => {
            orb.addEventListener('click', () => this.selectMood(orb.dataset.mood));
        });

        // Style orbs
        this.elements.styleOrbs.forEach(orb => {
            orb.addEventListener('click', () => this.selectStyle(orb.dataset.style));
        });

        // Vocal orbs
        this.elements.vocalOrbs.forEach(orb => {
            orb.addEventListener('click', () => this.selectVocal(orb.dataset.vocal));
        });

        // Cover buttons
        this.elements.createCoverBtn.addEventListener('click', () => this.createCover());
        this.elements.cancelBtn.addEventListener('click', () => this.cancelCover());
        this.elements.playCoverBtn.addEventListener('click', () => this.togglePlayCover());
        this.elements.downloadCoverBtn.addEventListener('click', () => this.downloadCover());

        // Settings
        this.elements.settingsBtn.addEventListener('click', () => this.showSettings());
        this.elements.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.elements.closeSettingsBtn.addEventListener('click', () => this.hideSettings());

        // Modal backdrop click
        this.elements.settingsModal.querySelector('.modal-backdrop').addEventListener('click', () => this.hideSettings());

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideSettings();
            }
        });
    },

    /**
     * Initialize modules
     */
    initModules() {
        // Initialize audio player
        AudioPlayer.init();
        AudioPlayer.setCallbacks({
            onOriginalStateChange: (playing) => {
                this.elements.playOriginalBtn.innerHTML = playing
                    ? '<span class="btn-emoji">⏹️</span> Stop'
                    : '<span class="btn-emoji">▶️</span> Play';
            },
            onCoverStateChange: (playing) => {
                this.elements.playCoverBtn.innerHTML = playing
                    ? '<span class="btn-emoji">⏹️</span> Stop'
                    : '<span class="btn-emoji">▶️</span> Play Cover';
            },
            onError: (type, error) => {
                this.showToast(`Playback error: ${error.message}`, 'error');
            }
        });
    },

    /**
     * Initialize particle animation
     */
    initParticles() {
        const canvas = this.elements.particles;
        const ctx = canvas.getContext('2d');

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        resize();
        window.addEventListener('resize', resize);

        const particles = [];
        const particleCount = 100;

        class Particle {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2 + 0.5;
                this.speedX = (Math.random() - 0.5) * 0.3;
                this.speedY = (Math.random() - 0.5) * 0.3;
                this.opacity = Math.random() * 0.4 + 0.1;
                this.twinkle = Math.random() * Math.PI * 2;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.twinkle += 0.02;

                if (this.x < 0 || this.x > canvas.width) this.speedX *= -1;
                if (this.y < 0 || this.y > canvas.height) this.speedY *= -1;
            }

            draw() {
                const opacity = this.opacity * (0.7 + Math.sin(this.twinkle) * 0.3);

                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(95, 179, 179, ${opacity})`;
                ctx.fill();
            }
        }

        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(p => {
                p.update();
                p.draw();
            });

            requestAnimationFrame(animate);
        };

        animate();
    },

    /**
     * Load settings from localStorage and configure API client
     */
    loadSettings() {
        const userKey = localStorage.getItem('user_access_key');
        if (userKey) {
            // Configure the API client with user key
            APIClient.setUserKey(userKey);
        }
        // Don't auto-show settings - user can open manually if needed
        // In dev mode (localhost), no key is required anyway
    },

    /**
     * Handle DNA input changes
     */
    onDNAInput() {
        const raw = this.elements.dnaInput.value;
        const cleaned = DNAEngine.cleanSequence(raw);
        this.elements.baseCount.textContent = cleaned.length;
    },

    /**
     * Handle duration slider changes
     */
    onDurationChange() {
        const value = this.elements.durationSlider.value;
        this.elements.durationValue.textContent = value;
    },

    /**
     * Load DNA from file
     */
    loadFile() {
        this.elements.fileInput.click();
    },

    /**
     * Handle file selection
     */
    onFileSelected(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            const sequence = DNAEngine.parseFasta(content);
            this.elements.dnaInput.value = sequence;
            this.onDNAInput();
            this.showToast(`Loaded ${sequence.length} bases from ${file.name}`, 'success');
        };
        reader.onerror = () => {
            this.showToast('Failed to read file', 'error');
        };
        reader.readAsText(file);

        // Reset input so same file can be loaded again
        event.target.value = '';
    },

    /**
     * Generate random realistic DNA sequence
     */
    generateRandomDNA() {
        // Random length between 120 and 300 bases (divisible by 3 for codons)
        const length = Math.floor(Math.random() * 60 + 40) * 3; // 120-300 bases
        const sequence = DNAEngine.generateRealisticDNA(length);
        this.elements.dnaInput.value = sequence;
        this.onDNAInput();

        // Show what makes this sequence interesting
        const analysis = DNAEngine.analyze(sequence);
        this.showToast(
            `Generated ${sequence.length} bases | GC: ${analysis.gcFormatted}% | Mode: ${analysis.modeName}`,
            'success'
        );
    },

    /**
     * Save current sequence to file
     */
    saveSequence() {
        const sequence = DNAEngine.cleanSequence(this.elements.dnaInput.value);
        if (!sequence) {
            this.showToast('No sequence to save', 'error');
            return;
        }

        const blob = new Blob([sequence], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dna_sequence.txt';
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Sequence saved', 'success');
    },

    /**
     * Clear sequence input
     */
    clearSequence() {
        this.elements.dnaInput.value = '';
        this.onDNAInput();
    },

    /**
     * Generate music from DNA
     */
    async generateMusic() {
        // IMPORTANT: Stop any playing audio first to prevent browser crash
        AudioPlayer.stopAll();

        const sequence = DNAEngine.cleanSequence(this.elements.dnaInput.value);
        const validation = DNAEngine.validate(sequence);

        if (!validation.valid) {
            this.showToast(validation.error, 'error');
            return;
        }

        const duration = parseInt(this.elements.durationSlider.value);

        // Update UI
        this.state.isGenerating = true;
        this.elements.generateBtn.disabled = true;
        this.elements.generateBtn.innerHTML = '<span class="btn-emoji">⏳</span> Generating...';
        this.elements.playOriginalBtn.disabled = true;

        try {
            const result = await APIClient.generateMusic(sequence, duration);

            if (result.success) {
                // Store file info
                this.state.mp3Path = result.mp3_path;
                this.state.mp3Filename = result.filename;
                AudioPlayer.setOriginalFile(result.filename);

                // Show analysis - now with Codon Harmony details
                const analysis = result.analysis;
                const modeDescriptions = {
                    'locrian': 'unstable, mysterious',
                    'phrygian': 'dark, exotic',
                    'aeolian': 'reflective, melancholic',
                    'dorian': 'jazzy, sophisticated',
                    'mixolydian': 'bluesy, relaxed',
                    'ionian': 'bright, happy',
                    'lydian': 'ethereal, dreamy'
                };
                const modeDesc = modeDescriptions[analysis.mode] || analysis.character || '';

                this.elements.analysisContent.innerHTML = `
                    <div class="analysis-grid">
                        <div class="analysis-item">
                            <span class="analysis-label">Key</span>
                            <span class="analysis-value">${analysis.key} ${analysis.mode}</span>
                        </div>
                        <div class="analysis-item">
                            <span class="analysis-label">Character</span>
                            <span class="analysis-value">${modeDesc}</span>
                        </div>
                        <div class="analysis-item">
                            <span class="analysis-label">Tempo</span>
                            <span class="analysis-value">${analysis.tempo} BPM</span>
                        </div>
                        <div class="analysis-item">
                            <span class="analysis-label">GC Content</span>
                            <span class="analysis-value">${analysis.gc}%</span>
                        </div>
                        <div class="analysis-item">
                            <span class="analysis-label">Codons</span>
                            <span class="analysis-value">${analysis.codon_count}</span>
                        </div>
                        <div class="analysis-item">
                            <span class="analysis-label">Motifs Found</span>
                            <span class="analysis-value">${analysis.motif_count}</span>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.65rem; opacity: 0.6;">Saved: ${result.mp3_path}</div>
                `;
                this.elements.analysisResult.classList.remove('hidden');

                // Enable buttons
                this.elements.playOriginalBtn.disabled = false;
                this.elements.downloadOriginalBtn.disabled = false;
                this.elements.createCoverBtn.disabled = false;

                // Update Step 2 status
                this.elements.step2Status.innerHTML = '<span class="status-icon">✓</span><span class="status-text">Ready for AI cover generation</span>';
                this.elements.step2Status.classList.remove('pending');
                this.elements.step2Status.classList.add('ready');

                this.showToast('Music generated successfully!', 'success');
            } else {
                throw new Error(result.error || 'Generation failed');
            }
        } catch (error) {
            this.showToast(`Generation failed: ${error.message}`, 'error');
        } finally {
            this.state.isGenerating = false;
            this.elements.generateBtn.disabled = false;
            this.elements.generateBtn.innerHTML = '<span class="btn-emoji">⚡</span> Generate Lifesong';
        }
    },

    /**
     * Toggle play/stop for original track
     */
    togglePlayOriginal() {
        AudioPlayer.toggleOriginal();
    },

    /**
     * Select mood
     */
    selectMood(mood) {
        this.state.mood = mood;

        // Update UI
        this.elements.moodOrbs.forEach(orb => {
            orb.classList.toggle('selected', orb.dataset.mood === mood);
        });

        this.updatePromptPreview();
    },

    /**
     * Select style
     */
    selectStyle(style) {
        this.state.style = style;

        // Update UI
        this.elements.styleOrbs.forEach(orb => {
            orb.classList.toggle('selected', orb.dataset.style === style);
        });

        this.updatePromptPreview();
    },

    /**
     * Select vocal type
     */
    selectVocal(vocalType) {
        this.state.vocalType = vocalType;

        // Update UI
        this.elements.vocalOrbs.forEach(orb => {
            orb.classList.toggle('selected', orb.dataset.vocal === vocalType);
        });

        this.updatePromptPreview();
    },

    /**
     * Update the prompt preview
     */
    updatePromptPreview() {
        const mood = this.state.mood;
        const style = this.state.style;
        const vocalType = this.state.vocalType;

        const moodTags = {
            'meditative': '[meditative, ambient, atmospheric, slow tempo, no drums]',
            'atmospheric': '[atmospheric, ambient, no drums, deep djembe, whale sounds, medium tempo]',
            'energetic': '[atmospheric, ambient, upbeat tempo, edm, deep djembe, whale sounds]'
        };

        const styleTags = {
            'electronic': '[electronic]',
            'folk': '[indie folk]',
            'classical': '[modern classical]'
        };

        let prompt = '';

        // Add style tag first if selected
        if (style) {
            prompt += styleTags[style] + ' ';
        }

        // Add mood tags
        prompt += moodTags[mood] || '';

        // Handle vocals based on selection
        if (vocalType === 'none') {
            // Strongly enforce instrumental - no vocals at all
            prompt += ' [instrumental, no vocals, no singing, no voice]';
        } else {
            // Vocal type selected - allow vocals
            prompt += ` [${vocalType} vocals, vocalise, wordless vocals]`;
        }

        this.elements.promptPreview.value = prompt;
    },

    /**
     * Create AI cover
     */
    async createCover() {
        if (!this.state.mp3Path) {
            this.showToast('Generate music first!', 'error');
            return;
        }

        // Update UI
        this.state.isCreatingCover = true;
        this.state.cancelRequested = false;
        this.elements.createCoverBtn.disabled = true;
        this.elements.createCoverBtn.innerHTML = '<span class="btn-emoji">⏳</span> Creating...';
        this.elements.cancelBtn.disabled = false;
        this.elements.statusLog.textContent = '';
        this.setProgress(0);

        const prompt = this.elements.promptPreview.value;
        const tags = 'ambient, electronic, ethereal, dna, organic, experimental';

        try {
            // Step 1: Upload
            this.log('📤 Uploading MP3...');
            this.setProgress(5);

            const uploadResult = await APIClient.uploadToMusicAPI(this.state.mp3Path);
            if (!uploadResult.success) throw new Error(uploadResult.error || 'Upload failed');

            if (this.state.cancelRequested) throw new Error('Cancelled');

            this.log('✅ Uploaded successfully');
            this.setProgress(15);

            // Step 2: Create cover
            this.log('🎨 Creating AI cover...');

            const createResult = await APIClient.createCover(uploadResult.clip_id, prompt, tags);
            if (!createResult.success) throw new Error(createResult.error || 'Cover creation failed');

            if (this.state.cancelRequested) throw new Error('Cancelled');

            this.log(`✅ Task started: ${createResult.task_id}`);

            // Step 3: Wait for completion
            this.log('⏳ Waiting for AI (2-3 minutes)...');

            const waitResult = await APIClient.waitForCover(
                createResult.task_id,
                (progress) => this.setProgress(progress),
                () => this.state.cancelRequested
            );

            if (!waitResult.audio_url) throw new Error('No audio URL received');

            // Step 4: Download
            this.log('⬇️ Downloading cover...');

            const downloadResult = await APIClient.downloadCover(waitResult.audio_url);
            if (!downloadResult.success) throw new Error(downloadResult.error || 'Download failed');

            // Success!
            this.state.coverPath = downloadResult.path;
            this.state.coverFilename = downloadResult.filename;
            AudioPlayer.setCoverFile(downloadResult.filename);

            this.log(`✅ Cover saved: ${downloadResult.path}`);
            this.setProgress(100);

            this.elements.playCoverBtn.disabled = false;
            this.elements.downloadCoverBtn.disabled = false;
            this.showToast('AI cover created successfully!', 'success');

        } catch (error) {
            if (error.message === 'Cancelled') {
                this.log('🛑 Cancelled by user');
            } else {
                this.log(`❌ Error: ${error.message}`);
                this.showToast(`Cover creation failed: ${error.message}`, 'error');
            }
        } finally {
            this.state.isCreatingCover = false;
            this.elements.createCoverBtn.disabled = false;
            this.elements.createCoverBtn.innerHTML = '<span class="btn-emoji">🎨</span> Create Cover';
            this.elements.cancelBtn.disabled = true;
        }
    },

    /**
     * Cancel cover creation
     */
    cancelCover() {
        this.state.cancelRequested = true;
        this.elements.cancelBtn.disabled = true;
        this.log('🛑 Cancelling...');
    },

    /**
     * Toggle play/stop for cover track
     */
    togglePlayCover() {
        AudioPlayer.toggleCover();
    },

    /**
     * Log message to status area
     */
    log(message) {
        this.elements.statusLog.textContent += message + '\n';
        this.elements.statusLog.scrollTop = this.elements.statusLog.scrollHeight;
    },

    /**
     * Set progress bar
     */
    setProgress(percent) {
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = percent > 0 ? `${Math.round(percent)}%` : '';
    },

    /**
     * Show settings modal
     */
    showSettings() {
        const currentKey = localStorage.getItem('user_access_key') || '';
        this.elements.userKeyInput.value = currentKey;
        this.elements.settingsModal.classList.remove('hidden');
    },

    /**
     * Hide settings modal
     */
    hideSettings() {
        this.elements.settingsModal.classList.add('hidden');
    },

    /**
     * Save settings
     */
    saveSettings() {
        const userKey = this.elements.userKeyInput.value.trim();
        if (!userKey) {
            this.showToast('Please enter an access key', 'error');
            return;
        }

        localStorage.setItem('user_access_key', userKey);
        APIClient.setUserKey(userKey);
        this.hideSettings();
        this.showToast('Settings saved!', 'success');
    },

    /**
     * Show a toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        this.elements.toastContainer.appendChild(toast);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    /**
     * Download original DNA music file
     */
    downloadOriginal() {
        if (!this.state.mp3Filename) {
            this.showToast('No music file to download', 'error');
            return;
        }

        // Create a download link
        const url = `/api/download-file/${encodeURIComponent(this.state.mp3Filename)}`;
        const a = document.createElement('a');
        a.href = url;
        a.download = this.state.mp3Filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        this.showToast('Downloading DNA music...', 'success');
    },

    /**
     * Download cover file
     */
    downloadCover() {
        if (!this.state.coverFilename) {
            this.showToast('No cover file to download', 'error');
            return;
        }

        // Create a download link
        const url = `/api/download-file/${encodeURIComponent(this.state.coverFilename)}`;
        const a = document.createElement('a');
        a.href = url;
        a.download = this.state.coverFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        this.showToast('Downloading cover...', 'success');
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

# DNA Lifesong Studio - PWA

A Progressive Web App that transforms DNA sequences into unique, personalized music.

## Features

- **DNA to Music**: Convert any DNA sequence into a MIDI melody
- **AI Cover Generation**: Use MusicAPI to create professional-sounding covers
- **PWA Support**: Install on any device (phone, tablet, desktop)
- **Offline Capable**: Core UI works offline
- **Beautiful UI**: Cosmic-themed design with particle effects

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip3 install flask flask-cors midiutil requests

# Audio conversion tools (macOS)
brew install timidity lame
```

### 2. Start the Server

```bash
cd backend
python3 server.py
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## Installing as an App

### On Phone (iOS/Android)
1. Open http://localhost:5000 in your browser
2. Tap the "Share" button (iOS) or menu (Android)
3. Select "Add to Home Screen"

### On Desktop (Chrome)
1. Open http://localhost:5000 in Chrome
2. Click the install icon in the address bar
3. Or: Menu → "Install DNA Lifesong Studio"

## PWA Icons

For full PWA support, you need app icons. Create PNG icons at these sizes and place in `frontend/assets/icons/`:

- icon-16.png
- icon-32.png
- icon-72.png
- icon-96.png
- icon-128.png
- icon-144.png
- icon-152.png
- icon-192.png
- icon-384.png
- icon-512.png

You can use an online tool like [PWA Asset Generator](https://progressier.com/pwa-icons-and-ios-splash-screen-generator) to create these from a single image.

## Project Structure

```
lifesong-pwa/
├── frontend/
│   ├── index.html          # Main HTML with PWA meta tags
│   ├── manifest.json       # PWA manifest
│   ├── service-worker.js   # Offline support
│   ├── css/
│   │   └── styles.css      # Cosmic-themed styles
│   ├── js/
│   │   ├── app.js          # Main application logic
│   │   ├── dna-engine.js   # DNA processing
│   │   ├── audio-player.js # Audio playback
│   │   └── api-client.js   # Server communication
│   └── assets/
│       ├── background.png  # Cosmic background
│       └── icons/          # PWA icons
├── backend/
│   ├── server.py           # Flask server
│   ├── dna_processor.py    # DNA → MIDI conversion
│   └── musicapi_client.py  # MusicAPI integration
└── README.md
```

## How It Works

### Stage 1: DNA → Music
1. Paste your DNA sequence (ATGC bases)
2. The app analyzes GC content to determine musical mode
3. Generates a 4-track MIDI file (melody, bass, chords, rhythm)
4. Converts to MP3 for playback

### Stage 2: AI Cover
1. Select a mood (Meditative, Atmospheric, Energetic)
2. Optionally add lyrics and choose vocal type
3. The app uploads to MusicAPI
4. AI generates a professional cover
5. Download and play the result

## API Key

You need a MusicAPI key for cover generation. Enter it in Settings (⚙️).

Get one at: https://musicapi.ai

## Deploying to Cloud

To make the app accessible from anywhere:

### Option 1: ngrok (temporary)
```bash
ngrok http 5000
```

### Option 2: Deploy to Railway/Render/Heroku
1. Create a `requirements.txt`:
```
flask
flask-cors
midiutil
requests
```

2. Set the start command: `python backend/server.py`

## Building Native Apps

### Android APK (using PWABuilder)
1. Deploy to a public URL with HTTPS
2. Go to https://pwabuilder.com
3. Enter your URL
4. Download the APK package

### iOS (using PWABuilder)
Same process, but requires Apple Developer account for App Store.

## License

MIT

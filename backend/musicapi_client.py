"""
DNA Lifesong Studio - MusicAPI Client
Handles communication with MusicAPI for AI cover generation
"""

import requests


class MusicAPIClient:
    """Client for MusicAPI AI music generation"""

    BASE_URL = "https://api.musicapi.ai/api/v1/sonic"
    CATBOX_URL = "https://catbox.moe/user/api.php"

    TIMEOUT_SHORT = 60   # For quick API calls
    TIMEOUT_LONG = 300   # For file uploads (5 minutes)

    def upload(self, file_path, api_key):
        """
        Upload audio file to Catbox and register with MusicAPI

        Args:
            file_path: Path to the audio file
            api_key: MusicAPI API key

        Returns:
            dict with clip_id on success, error on failure
        """
        try:
            # Step 1: Upload to Catbox (free file hosting)
            with open(file_path, 'rb') as f:
                response = requests.post(
                    self.CATBOX_URL,
                    data={'reqtype': 'fileupload'},
                    files={'fileToUpload': f},
                    timeout=self.TIMEOUT_LONG
                )

            if response.status_code != 200:
                return {'error': f'Catbox upload failed: HTTP {response.status_code}'}

            catbox_url = response.text.strip()

            if not catbox_url.startswith('http'):
                return {'error': f'Invalid Catbox response: {catbox_url[:100]}'}

            # Step 2: Register URL with MusicAPI
            response = requests.post(
                f'{self.BASE_URL}/upload',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={'url': catbox_url},
                timeout=self.TIMEOUT_SHORT
            )

            result = response.json()

            if result.get('clip_id'):
                return {'clip_id': result['clip_id']}
            else:
                error_msg = result.get('message', result.get('error', 'Unknown error'))
                return {'error': error_msg}

        except requests.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': str(e)}

    def create_cover(self, clip_id, prompt, tags, api_key):
        """
        Start AI cover generation

        Args:
            clip_id: Clip ID from upload
            prompt: AI generation prompt
            tags: Comma-separated tags
            api_key: MusicAPI API key

        Returns:
            dict with task_id on success, error on failure
        """
        try:
            response = requests.post(
                f'{self.BASE_URL}/create',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'task_type': 'cover_music',
                    'custom_mode': True,
                    'continue_clip_id': clip_id,
                    'prompt': prompt,
                    'title': 'DNA Lifesong Cover',
                    'tags': tags,
                    'mv': 'sonic-v5'
                },
                timeout=self.TIMEOUT_SHORT
            )

            result = response.json()

            if result.get('task_id'):
                return {'task_id': result['task_id']}
            else:
                error_msg = result.get('message', result.get('error', 'Unknown error'))
                return {'error': error_msg}

        except requests.RequestException as e:
            return {'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'error': str(e)}

    def check_status(self, task_id, api_key):
        """
        Check cover generation status

        Args:
            task_id: Task ID from create_cover
            api_key: MusicAPI API key

        Returns:
            dict with state and audio_url (if complete)
        """
        try:
            response = requests.get(
                f'{self.BASE_URL}/task/{task_id}',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=self.TIMEOUT_SHORT
            )

            result = response.json()

            if result.get('data') and len(result['data']) > 0:
                track = result['data'][0]
                state = track.get('state', 'unknown')

                if state == 'succeeded':
                    return {
                        'state': 'succeeded',
                        'audio_url': track.get('audio_url')
                    }
                elif state == 'failed':
                    return {
                        'state': 'failed',
                        'error': track.get('error', 'Generation failed')
                    }
                else:
                    return {'state': state}
            else:
                return {'state': 'unknown', 'error': 'No data in response'}

        except requests.RequestException as e:
            return {'state': 'error', 'error': f'Network error: {str(e)}'}
        except Exception as e:
            return {'state': 'error', 'error': str(e)}

    def download_audio(self, audio_url, output_path):
        """
        Download audio file from URL

        Args:
            audio_url: URL of the audio file
            output_path: Path to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(audio_url, stream=True, timeout=self.TIMEOUT_LONG)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True

        except Exception as e:
            print(f"Download error: {e}")
            return False

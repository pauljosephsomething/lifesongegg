"""
DNA Lifesong Studio - MusicAPI Client
Handles communication with MusicAPI for AI cover generation
"""

import os
import requests


class MusicAPIClient:
    """Client for MusicAPI AI music generation"""

    BASE_URL = "https://api.musicapi.ai/api/v1/sonic"
    FILE_IO_URL = "https://file.io"
    LITTERBOX_URL = "https://litterbox.catbox.moe/resources/internals/api.php"

    TIMEOUT_SHORT = 60   # For quick API calls
    TIMEOUT_LONG = 300   # For file uploads (5 minutes)

    def upload(self, file_path, api_key):
        """
        Upload audio file to file hosting and register with MusicAPI

        Args:
            file_path: Path to the audio file
            api_key: MusicAPI API key

        Returns:
            dict with clip_id on success, error on failure
        """
        try:
            # Try Litterbox first (temporary file hosting, 24h expiry)
            file_url = self._upload_to_litterbox(file_path)

            # If Litterbox fails, try file.io
            if not file_url:
                file_url = self._upload_to_fileio(file_path)

            if not file_url:
                return {'error': 'All file upload services failed'}

            if not file_url.startswith('http'):
                return {'error': f'Invalid upload response: {file_url[:100]}'}

            # Step 2: Register URL with MusicAPI
            response = requests.post(
                f'{self.BASE_URL}/upload',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={'url': file_url},
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

    def _upload_to_litterbox(self, file_path):
        """Upload to Litterbox (temporary hosting, 24h)"""
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    self.LITTERBOX_URL,
                    data={'reqtype': 'fileupload', 'time': '24h'},
                    files={'fileToUpload': (os.path.basename(file_path), f, 'audio/mpeg')},
                    timeout=self.TIMEOUT_LONG
                )
            if response.status_code == 200:
                url = response.text.strip()
                if url.startswith('http'):
                    return url
            return None
        except Exception as e:
            print(f"Litterbox upload failed: {e}")
            return None

    def _upload_to_fileio(self, file_path):
        """Upload to file.io (temporary hosting)"""
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    self.FILE_IO_URL,
                    files={'file': (os.path.basename(file_path), f, 'audio/mpeg')},
                    timeout=self.TIMEOUT_LONG
                )
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('link'):
                    return data['link']
            return None
        except Exception as e:
            print(f"file.io upload failed: {e}")
            return None

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

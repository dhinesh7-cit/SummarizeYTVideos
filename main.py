import os
import yt_dlp
import openai
import sys # Import sys to exit gracefully

# --- Set OpenAI API key ---
# Replace 'YOUR_API_KEY' securely (e.g., use environment variables)
API_KEY = ''

# Check if the placeholder API key is still there
if 'YOUR_API_KEY' in API_KEY:
     print("Error: Please replace 'YOUR_API_KEY' with your actual OpenAI API key in the script.")
     sys.exit(1) # Exit if the key hasn't been replaced

# --- Configure OpenAI library (for version 0.28.x) ---
try:
    openai.api_key = API_KEY
    # Verify connection by listing models (optional but good practice)
    openai.Model.list()
    print("OpenAI library configured successfully (v0.28).")
except openai.error.AuthenticationError:
    print(f"OpenAI Authentication Error: Invalid API key.")
    print("Please ensure your API key is correct.")
    sys.exit(1)
except Exception as e:
    print(f"Error configuring OpenAI or testing connection: {e}")
    sys.exit(1)


def download_audio(youtube_url, download_path):
    """
    Downloads the best audio using yt-dlp and returns the actual
    path to the downloaded file. Handles potential errors.
    """
    print(f"Attempting to download audio from: {youtube_url}")
    os.makedirs(download_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_path, '%(id)s.%(ext)s'),
        'quiet': False, # Set to False to see yt-dlp output
        'no_warnings': True,
        # 'max_filesize': '25M', # Uncomment to limit download size if needed for Whisper API
    }
    downloaded_file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting video info...")
            result = ydl.extract_info(youtube_url, download=True)
            file_id = result.get('id')
            print(f"Video ID: {file_id}")

            # Determine downloaded file path
            if result.get('requested_downloads') and result['requested_downloads'][0].get('filepath'):
                 downloaded_file_path = result['requested_downloads'][0]['filepath']
            elif result.get('filename'):
                 downloaded_file_path = result['filename']
            elif result.get('_filename'):
                 downloaded_file_path = result['_filename']
            elif file_id:
                 print("Filepath not found directly in result, attempting fallback...")
                 potential_exts = ['m4a', 'webm', 'mp3', 'opus', 'aac', 'ogg', 'wav']
                 for ext in potential_exts:
                     potential_path = os.path.join(download_path, f"{file_id}.{ext}")
                     if os.path.exists(potential_path):
                         downloaded_file_path = potential_path
                         print(f"Found file via fallback: {downloaded_file_path}")
                         break
                 if not downloaded_file_path:
                      print(f"Warning: Could not reliably determine downloaded file path for ID {file_id}")
                      return None
            else:
                 print("Warning: Could not determine downloaded file path (no ID found).")
                 return None

            # Final check if the determined path actually exists
            if downloaded_file_path and not os.path.exists(downloaded_file_path):
                print(f"Error: Determined path '{downloaded_file_path}' does not exist.")
                return None

    except yt_dlp.utils.DownloadError as e:
        print(f"Error during download (yt-dlp): {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        return None

    if downloaded_file_path:
        print(f"Successfully downloaded audio file: {downloaded_file_path}")
    else:
        print("Download process completed, but failed to determine file path.")

    return downloaded_file_path

def transcribe_audio(audio_file_path):
    """
    Transcribes the audio file using the OpenAI library (v0.28.x API).
    """
    if audio_file_path is None or not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found or path is invalid: {audio_file_path}")
        return None

    # Check file size (OpenAI has a 25MB limit for the standard Whisper API)
    try:
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        print(f"Audio file size: {file_size_mb:.2f} MB")
        if file_size_mb >= 25:
            print("Error: Audio file is larger than 25MB limit. Please use a smaller file or chunking.")
            return None
    except OSError as e:
        print(f"Error checking file size: {e}")
        return None

    print(f"Transcribing file: {audio_file_path}...")
    try:
        with open(audio_file_path, 'rb') as audio_data:
            # --- Use the openai 0.28 syntax ---
            transcript = openai.Audio.transcribe(
                model="whisper-1", # Correct model name for v0.28
                file=audio_data
            )
        # --- Access the result text correctly for v0.28 ---
        print("Transcription API call successful.")
        return transcript['text']
    except openai.error.APIConnectionError as e:
        print(f"OpenAI API Connection Error: {e}")
    except openai.error.RateLimitError as e:
        print(f"OpenAI API Rate Limit Error: {e}")
    except openai.error.APIError as e:
        print(f"OpenAI API Error: {e}")
    except Exception as e:
        print(f"Error during transcription: {e}")

    return None # Return None if any exception occurred

def summarize_text(text):
    """
    Summarizes the text using the OpenAI library (v0.28.x API)
    with the recommended legacy completions model.
    """
    if text is None:
        print("Error: No text provided for summarization.")
        return None

    prompt = f"Summarize the following text in a concise paragraph:\n\n{text}"
    print("Requesting summarization using gpt-3.5-turbo-instruct...")
    try:
        # --- Use the openai 0.28 syntax for completions ---
        # --- Use the recommended model for legacy completions endpoint ---
        response = openai.Completion.create(
          engine="gpt-3.5-turbo-instruct", # Use recommended replacement model
          prompt=prompt,
          max_tokens=200, # Increased slightly for potentially better summaries
          temperature=0.7, # You can adjust temperature for creativity vs determinism
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.0
        )
        # --- Access the result text correctly for v0.28 ---
        print("Summarization API call successful.")
        return response['choices'][0]['text'].strip()
    except openai.error.APIConnectionError as e:
        print(f"OpenAI API Connection Error during summarization: {e}")
    except openai.error.RateLimitError as e:
        print(f"OpenAI API Rate Limit Error during summarization: {e}")
    except openai.error.APIError as e:
        print(f"OpenAI API Error during summarization: {e}")
    except Exception as e:
        print(f"Error during summarization: {e}")

    return None # Return None if any exception occurred


def main(youtube_url, download_path):
    print("--- Starting YouTube Audio Transcription & Summarization ---")
    audio_file_path = download_audio(youtube_url, download_path)

    if audio_file_path:
        transcription = transcribe_audio(audio_file_path)

        if transcription:
            print("\n--- Transcription Complete ---")
            print(transcription)
            print("------------------------------")

            # Proceed to summarization
            print("\nSummarizing transcription...")
            summary = summarize_text(transcription)

            if summary:
                print("\n--- Summary Complete ---")
                print(summary)
                print("------------------------")
            else:
                print("\n--- Summarization Failed ---")
        else:
            print("\n--- Transcription Failed ---")
    else:
        print("\n--- Download Failed ---")

# --- Example usage ---
# Replace with a real YouTube video URL for testing
youtube_url = input("Enter the youtube URL: ") # Replace this placeholder
download_path = 'downloads/processed_audio' # Define where to save downloads

# Run the main function
main(youtube_url, download_path)
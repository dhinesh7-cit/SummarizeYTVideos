# YouTube Audio Transcription and Summarization Tool

This Python script allows you to:

- Download **audio** from a **YouTube** video.
- **Transcribe** the audio into **text** using **OpenAI's Whisper model**.
- **Summarize** the transcribed text using **GPT-3.5 Turbo Instruct**.

---

## Requirements

- Python 3.7 or higher
- [OpenAI API key](https://platform.openai.com/account/api-keys) (mandatory)
- Internet connection

---

## Installation

1. **Clone this repository** or copy the script.
2. **Install the required Python libraries**:

```bash
pip install yt-dlp openai

```
#Set your OpenAI API Key inside the script

Open the script and replace:

```python
API_KEY = 'YOUR_API_KEY'

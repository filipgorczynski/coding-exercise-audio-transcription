# Audio to Text - TransCribe

## Description

ASR (Automatic Speech Recognition) application that converts audio files into text transcriptions. The application consists of a Python backend using FastAPI and a frontend built with React and Vite.
The backend handles audio file uploads (or URL fetch), processes them using an ASR model (Whisper and PyAnnote-audio, at least for now), and returns the transcribed text to the frontend for display.

When uploading an audio file, the application performs the following steps:

1. Validates the file type.
2. Saves the file to a local storage (UPLOAD_DIR in .env ).
3. Transcribes the audio using Whisper model and pyannotate for speaker diarization.
4. Merges the transcription segments with speaker labels.
5. Saves the transcription result to a local storage (DATA_DIR in .env ).
6. Returns the transcribed text with speaker labels to the frontend.

## Pre-installation step

Create a Hugging Face account and get an access token with permissions to use the "pyannote/speaker-diarization-community-1" model.

0. Create .env files

```bash
λ cp app/.env.template app/.env
λ cp ui/.env.template ui/.env
```

1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Create new token with "Read" permissions
3. Copy the token and set it as an `HUGGINGFACE_ACCESS_TOKEN` environment variable in the `app/.env` file.
4. Accept Terms of Conditions for the model at: [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)

````

## Project start

```bash
# TODO(fgorczynski): make it better (cleaner)
λ docker-compose --env-file ./app/.env --env-file ./ui/.env  up --build --force-recreate
````

## Application access:

- [Full API Swagger](http://localhost:8000/docs)
- [API endpoints](http://localhost:8000/)
- [Web UI](http://localhost:5173/)

## Tests

```bash
# create virtualenv (Python 3.13+)
λ pip install -r requirements.txt -r requirements-dev.txt
λ pytest
```

## Problems / limitations / ideas

- During transcription there are 2 lists created (probably with different lengths) - so it should be treated as interval overlap problem.
  - Whisper gives N segments with [start_time, end_time].
  - Pyannote gives M Speaker(s) turns with [start, end] + speaker label.
  - Possibly N != M. We should merge by computing which speaker interval overlaps each Whisper segment the most (or split a Whisper segment if it spans multiple speaker turns).
- Pyannote can identify regions where multiple speakers are talking simultaneously (Could be handled)
- Replace dict output with Pydantic model
- Introduce new type TranscriptionSegmentWithSpeaker
- Extract overlap scanning into a small helper
- [Mastering Overlapping Interval Problems in Competitive Programming](https://www.rishabhxchoudhary.com/blog/overlapping-interval-problems)
- Add code quality tools (black, ruff, pre-commit, cyclomatic complexity checker, code coverage)
- Move processing (transcription & diarization) file to background task (Celery?)
- Provide more verbose Exception types
- database could be used instead of file storage
- ensure miliseconds are handled properly
- split React components into smaller ones
- cleanup requirements & requirements-dev files
- more tests with more edge cases and various files
<!-- - Add a SpeakerTimeline abstraction -->

## Plan

- [x] Create Python and frontend projects
- [x] Configure projects to start them with docker-compose
- [x] Prepare basic frontend layout
- [x] Create API endpoint for audio file upload
- [x] Connect frontend with backend API (TanStack Query)
- [x] Implement audio to text conversion logic
- [x] Display transcribed text in the frontend
- [x] Detect Speakers logic
- [x] Test the complete flow from audio upload to text display (pytest)

```

```

# Audio to Text - TransCribe

## Description

ASR (Automatic Speech Recognition) application that converts audio files into text transcriptions. The application consists of a Python backend using FastAPI and a frontend built with React and Vite.
The backend handles audio file uploads (or URL fetch), processes them using an ASR model (Whisper and PyAnnote-audio, at least for now), and returns the transcribed text to the frontend for display.

## Installation

```bash
λ docker-compose up --build
```

## Application access:

- [Full API Swagger](http://localhost:8000/docs)
- [API endpoints](http://localhost:8000/)
- [Web UI](http://localhost:5173/)

## Plan

- [x] Create Python and frontend projects
- [x] Configure projects to start them with docker-compose
- [x] Prepare basic frontend layout
- [x] Create API endpoint for audio file upload
- [x] Connect frontend with backend API (TanStack Query)
- [x] Implement audio to text conversion logic
- [x] Display transcribed text in the frontend
- [ ] Detect Speakers logic
- [ ] Test the complete flow from audio upload to text display (pytest)

```

```

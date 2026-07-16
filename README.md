# Cuepoint — RAG-based Video Q&A Assistant

Ask questions about your own video library in plain language, and get an answer that points you to the **exact video and timestamp** where it's discussed.

Built as an end-to-end Retrieval-Augmented Generation (RAG) pipeline — from raw video files to a searchable, chat-style web interface.

## How it works

```
Videos  →  Audio (mp3)  →  Transcript (Whisper)  →  Embeddings (bge-m3)
                                                          │
                                                          ▼
User question  →  Embedding  →  Cosine similarity search  →  Top matching chunks
                                                          │
                                                          ▼
                                        LLM (Llama 3.2)  →  Human-readable answer
                                        + video number & timestamp
```

1. **`video_to_mp3.py`** — extracts audio from each video file using FFmpeg
2. **`mp3_to_json.py`** — transcribes each audio file to text using OpenAI's Whisper (large-v2), producing timestamped chunks
3. **`preprocess_json.py`** — converts every text chunk into a vector embedding (via a local `bge-m3` model served through Ollama) and stores everything in a single dataframe
4. **`process_incoming.py`** — takes a user's question, embeds it, finds the most similar video chunks using cosine similarity, and asks a local LLM (`llama3.2`) to answer using only that retrieved context
5. **`webapp/`** — a Flask web app wrapping the same pipeline with a chat-style UI: type a question, get an answer with clickable timestamp chips that jump the embedded video player to that exact moment

## Tech stack

- **Whisper** — speech-to-text transcription
- **FFmpeg** — video → audio conversion
- **Ollama** — running embedding + LLM models locally
- **bge-m3** — embedding model
- **Llama 3.2** — answer generation
- **scikit-learn** — cosine similarity search
- **pandas / joblib** — storing and loading processed data
- **Flask** — web backend
- **HTML / CSS / JS** — frontend

## Setup

### 1. Install requirements
```bash
pip install -r requirements.txt
```
You'll also need [Ollama](https://ollama.com) installed, with these models pulled:
```bash
ollama pull bge-m3
ollama pull llama3.2
```
And [FFmpeg](https://ffmpeg.org/download.html) installed and available on your system PATH.

### 2. Add your videos
Place your video files inside a `videos/` folder in the project root.

### 3. Run the pipeline (in order)
```bash
python video_to_mp3.py       # videos -> audios/
python mp3_to_json.py        # audios -> jsons/ (transcripts)
python preprocess_json.py    # jsons -> embeddings.joblib
```

### 4. Ask questions

**Command line:**
```bash
python process_incoming.py
```

**Web app:**
```bash
cd webapp
python app.py
```
Then open `http://127.0.0.1:5000` in your browser.

## Limitations & possible improvements

- Currently tuned for Hindi-language videos translated to English (`language="hi"`, `task="translate"` in `mp3_to_json.py`) — easily changeable for other languages
- Embeddings are stored in a flat file (`joblib`), which won't scale well past a few thousand chunks — a proper vector database (e.g. FAISS, Pinecone, Chroma) would be the next step for larger libraries
- Runs entirely on local models via Ollama — no data leaves your machine, but response quality depends on the local LLM used
- No authentication on the web app — meant for local/personal use currently

## Project structure

```
.
├── video_to_mp3.py
├── mp3_to_json.py
├── preprocess_json.py
├── process_incoming.py
├── requirements.txt
├── webapp/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── style.css
│       └── script.js
├── videos/       (not included — add your own)
├── audios/       (generated)
└── jsons/        (generated)
```

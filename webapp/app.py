from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import joblib
import requests
import os
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ---------------------------------------------------------------
# Load the embeddings once when the server starts (not per-request)
# ---------------------------------------------------------------
df = joblib.load("embeddings.joblib")

VIDEOS_DIR = "videos"
video_files = sorted(os.listdir(VIDEOS_DIR)) if os.path.isdir(VIDEOS_DIR) else []


def get_video_title(video_number):
    """Builds a short title for the sidebar from the video's first spoken line."""
    rows = df[df["video_number"] == str(video_number)]
    if rows.empty:
        return f"Video {video_number}"
    first_text = rows.sort_values("start").iloc[0]["text"].strip()
    words = first_text.split()[:6]
    title = " ".join(words)
    if len(first_text.split()) > 6:
        title += "..."
    return title


def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })
    return r.json()["embeddings"]


def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    return r.json()["response"]


def format_timestamp(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


@app.route("/")
def home():
    video_numbers = sorted(df["video_number"].unique(), key=lambda x: int(x))
    videos = [{"number": v, "title": get_video_title(v)} for v in video_numbers]
    return render_template("index.html", videos=videos)


@app.route("/media/<int:number>")
def media(number):
    """Streams the actual video file so the browser <video> tag can play + seek it."""
    idx = number - 1
    if idx < 0 or idx >= len(video_files):
        return "Video not found", 404
    path = os.path.join(VIDEOS_DIR, video_files[idx])
    return send_file(path, conditional=True)


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please type a question."}), 400

    question_embedding = create_embedding([question])[0]
    similarities = cosine_similarity(np.vstack(df["embedding"]), [question_embedding]).flatten()

    top_results = 5
    max_indx = similarities.argsort()[::-1][0:top_results]
    new_df = df.loc[max_indx]

    prompt = f''' Here are video subtitle chunks containing video number, start time in seconds, end time in seconds, and the text spoken at that time:

{new_df[["video_number", "start", "end", "text"]].to_json(orient="records")}
-----------------------------------------
'{question}'
User asked this question related to the video chunks. Answer in a warm, human way in 2-4 sentences (dont mention the above format, its just for you). Clearly mention which video number the content is from. If the user asks something unrelated to the videos, tell them you can only answer questions about this video library.
'''

    answer = inference(prompt)

    sources = []
    for _, row in new_df.sort_values("start").iterrows():
        sources.append({
            "video_number": row["video_number"],
            "start": float(row["start"]),
            "end": float(row["end"]),
            "timestamp": format_timestamp(row["start"]),
            "text": row["text"].strip()
        })

    with open("prompt.txt", "w") as f:
        f.write(prompt)
    with open("response.txt", "w") as f:
        f.write(answer)

    return jsonify({"answer": answer, "sources": sources})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

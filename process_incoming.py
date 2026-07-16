import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import requests


def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json = {
        "model": "bge-m3",
        "input": text_list
    })


    embedding = r.json()["embeddings"]
    return embedding

def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json = {
        # "model": "deepseek-r1",
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })

    response = r.json()
    # print(response)
    return response

df = joblib.load("embeddings.joblib")

print(f"Loaded videos in database: {df['video_number'].unique()}")  

incoming_query = input("Ask a Question: ")
question_embedding = create_embedding([incoming_query])[0]

# Find similarities of question_embedding with other embeddings
similarities = cosine_similarity(np.vstack(df["embedding"]), [question_embedding]).flatten()
top_results = 5
max_indx = similarities.argsort()[::-1][0:top_results]
new_df = df.loc[max_indx]


prompt = f''' Here are video subtitle chunks containing video number, start time in seconds, end time in seconds, and the text spoken at that time:

{new_df[["video_number", "start", "end", "text"]].to_json(orient = "records")}
-----------------------------------------
'{incoming_query}'
User asked this question related to the video chunks. Answer in a human, friendly way (dont mention the above format, its just for you). In your answer clearly mention:
1. Which video number this content is from (e.g. "video 3")
2. The approximate timestamp (start time, converted to minutes:seconds format)
3. A short summary of what is taught there
Guide the user to go to that particular video and timestamp. If user asks unrelated question, tell him that you can only answer questions related to the video.
'''

with open("prompt.txt","w") as f:
    f.write(prompt)

response = inference(prompt)["response"]
print(response)  

with open("response.txt","w") as f:
    f.write(response)

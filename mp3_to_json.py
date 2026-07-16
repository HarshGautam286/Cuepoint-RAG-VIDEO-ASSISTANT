import whisper
import json
import os

model = whisper.load_model("large-v2")
audios = os.listdir("audios")
 
for audio in audios:
    # if("_" in audio):
    #     number = audio.split("_")[0]
    #     title = audio.split("_")[1][:-4]
    #     print(number, title)

    number = audio.split(".")[0]
    print(number)
    result = model.transcribe(audio = f"audios/{audio}",
                            language = "hi",
                            task = "translate",
                            word_timestamps= False)

    chunks = []
    for segment in result ["segments"]:
        chunks.append({"video_number": number,"start": segment["start"], "end": segment["end"], "text": segment["text"],})    

    chunks_with_metadata = {"chunks": chunks, "text": result["text"]}

    with open(f"jsons/{number}.json", "w") as f:
        json.dump(chunks_with_metadata, f)
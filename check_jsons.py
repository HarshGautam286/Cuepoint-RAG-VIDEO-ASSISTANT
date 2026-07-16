import json
import os

jsons_folder = "jsons"
files = sorted(os.listdir(jsons_folder), key=lambda x: int(x.split(".")[0]))

print(f"Total files found: {len(files)}\n")

for file in files:
    path = f"{jsons_folder}/{file}"
    try:
        with open(path, "r") as f:
            content = json.load(f)

        # Basic checks
        has_chunks = "chunks" in content
        has_text = "text" in content
        num_chunks = len(content["chunks"]) if has_chunks else 0
        text_length = len(content["text"]) if has_text else 0

        # Check video_number is present in chunks (our new field)
        has_video_number = num_chunks > 0 and "video_number" in content["chunks"][0]

        status = "OK" if (has_chunks and has_text and num_chunks > 0 and has_video_number) else "PROBLEM"

        print(f"{file:12} -> status: {status:8} | chunks: {num_chunks:4} | text_length: {text_length:6} | has_video_number: {has_video_number}")

    except json.JSONDecodeError:
        print(f"{file:12} -> CORRUPT FILE (incomplete/invalid JSON) - transcription was cut off!")
    except Exception as e:
        print(f"{file:12} -> ERROR: {e}")

print("\nDone checking. Agar koi file 'PROBLEM' ya 'CORRUPT' dikhaye, us audio ko dobara process karna hoga.")

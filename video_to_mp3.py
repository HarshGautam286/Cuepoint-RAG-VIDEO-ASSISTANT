# Converts the video to mp3
import os
import subprocess

files = sorted(os.listdir("videos"))
for index, file in enumerate(files, start= 1):
    print(file)

    subprocess.run(["ffmpeg", "-i", f"videos/{file}",
                    f"audios/{index}.mp3"])

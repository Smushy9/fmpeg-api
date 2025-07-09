import os, subprocess, uuid, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/create-video', methods=['POST'])
def create_video():
    data = request.get_json(force=True)
    image_url = data.get("image_url")
    audio_url = data.get("audio_url")
    duration = float(data.get("duration", 15))
    fade_in = float(data.get("fade_in", 1))

    uid = str(uuid.uuid4())
    image_path = f"{uid}.jpg"
    audio_path = f"{uid}.mp3"
    output_dir = "static"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{uid}.mp4"

    # Download media
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)

    # Build ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", f"fade=t=in:st=0:d={fade_in}",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)

    # Clean up inputs
    os.remove(image_path)
    os.remove(audio_path)

    video_url = request.host_url.rstrip('/') + '/' + output_path
    return jsonify({"video_url": video_url})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
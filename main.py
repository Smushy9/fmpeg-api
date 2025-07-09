from flask import Flask, request, send_file, jsonify
import subprocess, uuid, requests, os, re

app = Flask(__name__)

def normalize_dropbox(url: str) -> str:
    if "dropbox.com" not in url:
        return url

    m = re.match(r"https?://www\.dropbox\.com/s/([^/]+)/([^?]+)", url)
    if m:
        return f"https://dl.dropboxusercontent.com/s/{m.group(1)}/{m.group(2)}"

    if "dl=0" in url:
        return url.replace("dl=0", "dl=1")
    if "dl=1" in url:
        return url

    return url

@app.route("/")
def ping():
    return "FFmpeg-API 🚀"

@app.route("/create-video", methods=["POST"])
def create_video():
    data = request.get_json(force=True)
    image_url = data.get("image_url")
    audio_url = data.get("audio_url")

    if not image_url or not audio_url:
        return jsonify(error="image_url och audio_url krävs"), 400

    audio_url = normalize_dropbox(audio_url)

    uid = str(uuid.uuid4())
    img_path    = f"/tmp/{uid}.jpg"
    audio_path  = f"/tmp/{uid}.mp3"
    output_path = f"/tmp/{uid}.mp4"

    with open(img_path, "wb") as f:
        f.write(requests.get(image_url).content)
    with open(audio_path, "wb") as f:
        f.write(requests.get(audio_url).content)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)

    return send_file(output_path, mimetype="video/mp4")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

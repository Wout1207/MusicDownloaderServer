from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

def extract_audio_info(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        "cookies": "chromewebstore.google.com_cookies.txt"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Try direct URL first
        if 'url' in info:
            return {
                "title": info.get("title"),
                "audio_url": info.get("url")
            }

        # Otherwise find best audio format
        formats = info.get("formats", [])
        for f in formats:
            if f.get("acodec") != "none":
                return {
                    "title": info.get("title"),
                    "audio_url": f.get("url")
                }

    return None


@app.route("/audio", methods=["GET"])
def get_audio():
    url = request.args.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        data = extract_audio_info(url)

        if not data:
            return jsonify({"error": "No audio found"}), 404

        return jsonify({
            "success": True,
            "title": data["title"],
            "audio_url": data["audio_url"]
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
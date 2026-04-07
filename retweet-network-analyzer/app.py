from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from scraper import get_working_instance, get_tweet_info, get_retweeters, classify_users
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR)
CORS(app)

@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data not found"}), 400

    tweet_url = data.get("url", "").strip()
    if not tweet_url:
        return jsonify({"error": "URL cannot be empty"}), 400

    if "twitter.com" not in tweet_url and "x.com" not in tweet_url:
        return jsonify({"error": "Enter a valid Twitter/X link"}), 400

    instance = get_working_instance()

    tweet_info, err = get_tweet_info(tweet_url, instance)
    if err:
        return jsonify({"error": f"Could not fetch tweet info: {err}"}), 400

    retweeters, err = get_retweeters(tweet_url, instance, max_pages=5)
    if err:
        return jsonify({"error": f"Could not fetch retweeters: {err}"}), 400

    if not retweeters:
        return jsonify({"error": "No retweeters found. Is the tweet public?"}), 404

    classified = classify_users(retweeters)

    groups = {}
    for u in classified:
        g = u["group"]
        groups.setdefault(g, []).append({
            "username": u["username"],
            "name": u["name"],
            "created_at": u.get("created_at", ""),
            "followers_count": u.get("followers_count", 0),
            "statuses_count": u.get("statuses_count", 0),
            "verified": u.get("verified", False),
        })

    tweet_info["rt_count"] = len(retweeters)

    return jsonify({
        "tweet": tweet_info,
        "users": classified,
        "groups": groups,
        "total": len(retweeters),
        "instance_used": instance
    })

if __name__ == "__main__":
    print("=" * 45)
    print("  Social Graph Tool backend starting...")
    print("  Open http://localhost:5000")
    print("=" * 45)
    app.run(debug=True, port=5000, host="0.0.0.0")

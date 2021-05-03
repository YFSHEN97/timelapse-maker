from flask import Flask, request, send_file
from flask_cors import CORS
import cv2
import numpy as np
import json
import urllib
import base64
import subprocess

import video_maker as VideoMaker
from age_predictor import AgePredictor


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)


# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# everything uses the same age predictor, avoid reinitializing every time
AGE_PREDICTOR = AgePredictor()


# helper function to convert URL to actual image that is read by opencv
def url2image(url, color=True):
    if url == "":
        return None
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    if color: # by default read the images as colored images
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    else: # if optional argument color is given as False, then read as black-and-white image
        image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)
    return image


# request handler for age estimation of a SINGLE image
@app.route("/estimate_age", methods=["POST"])
def estimate_age():
    img = url2image(request.form.get("image_url"))
    age, _, _ = AGE_PREDICTOR.predict_age(img)
    return json.dumps({"success": True, "age": age}), 200, {"ContentType": "application/json"}


# request handler for age estimation of multiple images
@app.route("/estimate_age_all", methods=["POST"])
def estimate_age_all():
    unestimated = json.loads(request.form.get("unestimated"))
    results = []
    for datum in unestimated:
        img = url2image(datum["src"])
        age, _, _ = AGE_PREDICTOR.predict_age(img)
        results.append({"key": datum["key"], "age": age})
    return json.dumps({"success": True, "results": results}), 200, {"ContentType": "application/json"}


# request handler for rendering a video and sending it back to JavaScript
@app.route("/render_video", methods=["POST"])
def render_video():
    mode = request.form.get("mode")
    pause = float(request.form.get("pause"))
    fps = int(request.form.get("fps"))
    if mode == "cross-fading":
        duration = float(request.form.get("duration"))
    image_urls = list(map(lambda i: i["src"], json.loads(request.form.get("list"))))
    images = list(map(lambda url: url2image(url), image_urls))
    images = VideoMaker.align_faces(images)
    if mode == "cross-fading":
        VideoMaker.make_video(images, "./data/out.mp4", interval=duration, pause=pause, fps=fps)
    else:
        VideoMaker.make_video_nomorph(images, "./data/out.mp4", pause=pause, fps=fps)
    # convert video codec to h264
    subprocess.run(["ffmpeg", "-i", "./data/out.mp4", "-vcodec", "h264", "./data/out_h264.mp4"])
    # prepare response by sending the mp4
    response = send_file("./data/out_h264.mp4", mimetype="text/plain; charset=x-user-defined", as_attachment=True)
    # forcefully remove the "charset=utf-8" designation
    response.headers["content-type"] = "text/plain; charset=x-user-defined"
    # clean up
    subprocess.run(["rm", "./data/out.mp4", "./data/out_h264.mp4"])
    return response
    # return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True, threaded=True)

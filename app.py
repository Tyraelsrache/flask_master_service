import os
from flask import Flask, request, Response, flash, redirect, url_for, jsonify, abort, render_template, send_file
from flask_cors import CORS
import random
import sys


# create and configure the app
app = Flask(__name__)
CORS(app)

image_var = ''           # variable um das aktuelle Bild zu puffern

# -----------  Healthcheck
from healthcheck import HealthCheck, EnvironmentDump

# Testfälle definieren

def redis_available():
    client = _redis_client()
    info = client.info()
    return True, "redis ok"
health = HealthCheck()
envdump = EnvironmentDump()
health.add_check(redis_available)

# add your own data to the environment dump
def application_data():
    return {"maintainer": "Luis Fernando Gomes",
            "git_repo": "https://github.com/ateliedocodigo/py-healthcheck"}

envdump.add_section("application", application_data)

# Add a flask route to expose information
app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
app.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())

#--------------- Healthcheck


#--------------- Monitoring

#import flask_monitoringdashboard as dashboard
#dashboard.bind(app)

#--------------- Monitoring


@app.after_request
def after_request(response):
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/')
def landing_page():

    return 'Hello to my API'

#----------------Post Route für das Bild Tutorial   https://jdhao.github.io/2020/04/12/build_webapi_with_flask_s2/

import base64
import io
from PIL import Image  # pip install pillow (image library)


@app.route('/post_pic', methods=['POST'])
def post_pic():
    global image_var
    try:
        # getting image
        payload = request.form.to_dict(flat=False)
        im_b64 = payload['image'][0]  # remember that now each key corresponds to list.
        # see https://jdhao.github.io/2020/03/17/base64_opencv_pil_image_conversion/
        # for more info on how to convert base64 image to PIL Image object.
        im_binary = base64.b64decode(im_b64)
        buf = io.BytesIO(im_binary)
        img = Image.open(buf)
        image_var = im_binary
        
        # getting metadata
        payload_meta = request.form
        print(payload_meta.get("type"), file=sys.stderr)
        return jsonify({'msg': 'success', 'size': [img.width, img.height], 'type': payload_meta.get("type")})

    except:

        return jsonify({'msg': 'false; did not work'})

# ---------------- Debug Route ( download the actual pic )

@app.route('/pic')
def debug_pic():
    global image_var

    return send_file(
        io.BytesIO(image_var),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='debug.jpg')



#--------------------


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

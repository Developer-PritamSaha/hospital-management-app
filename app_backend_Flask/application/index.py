from flask import current_app as app
from flask import send_from_directory, jsonify

@app.route("/")
def home():
    try:
      # return send_from_directory(app.static_folder, "index.html")
      return jsonify({'msg': "Hospital Management Api is Running."}), 200
    except Exception as e:
      app.logger.exception(f'Failed to load the application frontend: {e}')


# Handle Vue router (SPA) routes
@app.route("/<path:path>")
def catch_all(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, "index.html")
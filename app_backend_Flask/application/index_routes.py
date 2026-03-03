from flask import current_app as app
from flask import send_from_directory, jsonify

@app.route("/")
def home():
    try:
      return send_from_directory(app.static_folder, "index.html")
    except Exception as e:
      app.logger.exception(f'Failed to load the application frontend: {e}')
      return jsonify({'message': 'Frontend loading falied'}), 500

@app.route("/api", methods=["GET", "POST"])
def root_api():
    try:
      return jsonify({'message': "Hospital Management System Api is Running."}), 200
    except Exception as e:
      app.logger.exception(f'Failed to fullfill the request: {e}')
      return jsonify({'message': 'The server faced an error'}), 500


# Handle Vue router (SPA) routes
@app.route("/<path:path>")
def catch_all(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, "index.html")
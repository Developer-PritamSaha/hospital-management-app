from flask import current_app as app
from flask import send_from_directory, jsonify
import os, subprocess, time

def build_frontend_dist(dir:str="./app_frontend_VUE", rebuild:bool=False): 
    '''This function creates the frontend distbution for serving by spwaning "npm" subprocesses for the build'''
    dist_dir = os.path.join(dir, "dist") 
    if rebuild or not os.path.exists(dist_dir):
        app.logger.info("Frontend distribution dir not available. Starting the subprocess for building.")
        print(">> Frontend dist directory not found. Building dist...")
        
        try:
            start_timer = time.time()
            subprocess.check_call("npm install", shell=True, cwd=dir)
            subprocess.check_call("npm run build", shell=True, cwd=dir)
            stop_timer = time.time()
            time_taken = stop_timer - start_timer
            app.logger.info("Frontend dist build completed successfully")
            print(f">> Frontend dist build completed successfully within {time_taken:.3f} sec.")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Frontend dist build failed: {e}")
    else:
        print(">> Frontend initialized successfully...")
        app.logger.info("Frontend distribution already exists. Skipping build.")

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
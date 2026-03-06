from flask import current_app as app
import os, subprocess, time
from redis import Redis, ConnectionError, TimeoutError

def build_frontend_dist(dir:str="./app_frontend_VUE", rebuild:bool=False, build:bool=True): 
    '''This function creates the frontend distbution for serving by spwaning "npm" subprocesses for the build'''

    if not build:
        print(">> Frontend dist build skipped...")
    else:
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
                print("\n[!] Frontend dist build failed..")
                raise Exception(f"Frontend dist build failed: {e}")
            except FileNotFoundError:
                print("\n[!] Frontend dist build failed..")
                raise Exception("'npm' subprocess execution failed. 'NodeJs' and 'npm' not installed properly.")

        else:
            print(">> Frontend initialized successfully...")
            app.logger.info("Frontend distribution already exists. Skipping build.")

def is_redis_active(host="localhost", port="6379"):
    '''This function checks for the redis server is active or not'''
    try:
        r = Redis(host=host, port=port, socket_connect_timeout=1)
        return r.ping()  # Returns True if it gets a PONG
    except (ConnectionError,TimeoutError):
        return False

def start_celery_workers_beats():
    '''This function starts the celery workers and beats subprocesses for the background services'''
    if not is_redis_active():
        print("\n[!] Redis server is not running..")
        raise Exception('Celery services needs redis server to be running.')
    else:
        try:
            subprocess.Popen([
                'celery', '-A', 'app.celery', 'worker', 
                '--loglevel=info', 
                '--logfile=logs/celery_worker.log'
            ],
            stdout=subprocess.DEVNULL) # sink the initial startup banner

            subprocess.Popen([
                'celery', '-A', 'app.celery', 'beat', 
                '--loglevel=info', 
                '--logfile=logs/celery_beat.log',
                '--schedule=logs/celerybeat-schedule'
            ],
            stdout=subprocess.DEVNULL)


        except Exception as e:
            raise Exception(f'Celery service subprocess creation failed: {e}')
        else:
            print(">> Celery Worker & Beat services started succesfully...")

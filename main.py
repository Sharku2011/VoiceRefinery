# app.py
from flask import Flask, request, render_template, Response
import sqlite3
import os
import gzip
import zlib

app = Flask(__name__)

UPLOAD_FOLDER = 'records'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DB_CONNECTIONS'] = dict()
app.config['CURRENT_DB'] = ""

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect',  methods=['POST'])
def connect_db():
    if len(request.get_json()) <= 0:
        return Response("Invalid request", status=400)
    db_name = request.get_json()['id']
    if len(db_name) <= 0:
        return Response("Invalid database name", status=400)

    connections = app.config['DB_CONNECTIONS']
    
    try:
        if db_name == app.config['CURRENT_DB'] and app.config['CURRENT_DB'] is not None:
            cur_db_name = db_name
        else:
            conn = sqlite3.connect(f"{db_name}.db", check_same_thread=False)
            app.config['CURRENT_DB'] = db_name
        connections[db_name] = conn
        return Response(f"Connected to db {db_name}", status=200)
    except Exception as e:
        return Response(f"{e}", status=400)
    
@app.route('/disconnect', methods=['POST'])
def disconnect_db():
    if len(request.get_json()) <= 0:
        return Response("Invalid request", status=400)
    db_name = request.get_json()['id']
    if len(db_name) <= 0:
        if app.config['CURRENT_DB'] in app.config['DB_CONNECTIONS'].keys():
            conn = app.config['DB_CONNECTIONS'].pop(app.config['CURRENT_DB'])
            conn.close()
            app.config['CURRENT_DB'] = ""
            return Response(f"Disconnect to database [{app.config['CURRENT_DB']}] successfully", status=200)
        else:
            return Response("Failed to remove latest database connection", status=400)
    
    conn = app.config['DB_CONNECTIONS'].pop(db_name)
    if conn is None:
        return Response("No valid connection to database. Ignore request...", status=200)
    conn.close()
    if db_name == app.config['CURRENT_DB']:
        app.config['CURRENT_DB'] = ""
    return Response(f"Disconnect to database [{db_name}] successfully", status=200)

@app.route('/audio', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return Response('Invalid File data', status=400)
    
    file = request.files['file']
    
    if file.filename == '':
        return Response('Invalid file name', status=400)
    
    if file:
        db_name = app.config['CURRENT_DB']
        conn = app.config['DB_CONNECTIONS'][db_name]
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS RECORDS (
                                filename TEXT PRIMARY KEY,
                                content BLOB NOT NULL
                                );''')

        compressed = gzip.compress(file.read())
        cursor.execute(f"INSERT INTO RECORDS VALUES ('{file.filename}',{compressed});")
        cursor.commit()
        return Response('File successfully uploaded', status=200)

if __name__ == '__main__':
    app.run(port=5000)
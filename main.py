# app.py
from flask import Flask, request, render_template, Response
import sqlite3
import os
import gzip
import zlib

app = Flask(__name__)

UPLOAD_FOLDER = 'records'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DB_CONNECTION'] = None

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

    conn = app.config['DB_CONNECTION']
    if conn is not None:
        print("Close previous connection to database")
        conn.close()

    try:
        sqlite3.connect(f"{db_name}.db")
        return Response(f"Connected to db {db_name}", status=201)
    except Exception as e:
        return Response(f"{e}", status=400)
    
@app.route('/disconnect', methods=['GET','POST'])
def disconnect_db():
    conn = app.config['DB_CONNECTION']
    if conn is None:
        return Response("No valid connection to database. Ignore request...", status=200)
    conn.close()
    return Response("Disconnect to database successfully", status=200)

@app.route('/audio', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return Response('Invalid File data', status=400)
    
    file = request.files['file']
    
    if file.filename == '':
        return Response('Invalid file name', status=400)
    
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return Response('File successfully uploaded', status=200)

if __name__ == '__main__':
    app.run(port=5000)
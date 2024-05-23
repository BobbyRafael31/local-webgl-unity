from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, abort
from flask_compress import Compress
from werkzeug.utils import secure_filename, safe_join
import os
import zipfile
import shutil

STATIC_FOLDER = 'webgl_static'  
ALLOWED_EXTENSIONS = {'zip'}

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
Compress(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_file():
    return render_template_string('''
    <!DOCTYPE html>
<html>
<head>
    <title>Upload Webgl ZipFile</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 500px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
        }
        form {
            text-align: center;
        }
        input[type="file"] {
            margin-top: 20px;
        }
        input[type="submit"] {
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
        .caution {
            margin-top: 20px;
            font-size: 14px;
            color: red;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload new ZIP File</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Run">
        </form>
        <div class="caution">
            <p>Please ensure the ZIP file does not contain nested folders.</p>
        </div>
    </div>
</body>
</html>

    ''')

@app.route('/', methods=['POST'])
def upload_file_post():
    # Clear static folder if it exists
    if os.path.exists(app.static_folder):
        shutil.rmtree(app.static_folder)
    os.makedirs(app.static_folder)

    # check if the post request has the file part
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.static_folder, filename)
        file.save(file_path)
        
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(app.static_folder)
        
        os.remove(file_path)
        return redirect(url_for('serve_index'))
    return redirect(request.url)

@app.route('/index.html')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    try:
        full_path = safe_join(app.static_folder, path)
        if os.path.isfile(full_path):
            return send_from_directory(app.static_folder, path)

        full_path = safe_join(app.static_folder, 'Build', path)
        if os.path.isfile(full_path):
            return send_from_directory(safe_join(app.static_folder, 'Build'), path)

        full_path = safe_join(app.static_folder, 'TemplateData', path)
        if os.path.isfile(full_path):
            return send_from_directory(safe_join(app.static_folder, 'TemplateData'), path)

        abort(404)
    except Exception as e:
        abort(404)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')

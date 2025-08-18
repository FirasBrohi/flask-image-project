from flask import Flask, request, jsonify, send_from_directory
import boto3, botocore
from actions import bp as actionsbp
from filters import bp as filtersbp
from android import bp as androidbp
from helpers import get_secure_filename_filepath, IS_ALLOWED_EXTENSIONS, upload_to_s3
import os




UPLPOAD_FOLDER = 'uploads/'
DWONLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__)

app.secret_key = 'ghx6868--CH134_jsl'

app.config['S3_BUCKET'] = 'my-bucketoffiras'
app.config['S3_LOCATOIN'] = 'https://my-bucketoffiras.s3.eu-north-1.amazonaws.com/uploads/'
app.config['S3_SECRET'] = os.environ.get('MY_SECRET')
app.config['S3_KEY']

app.config['UPLOAD_FOLDER'] = UPLPOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DWONLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.register_blueprint(actionsbp)
app.register_blueprint(filtersbp)
app.register_blueprint(androidbp)


@app.route('/image', methods=['GET','POST'])
def image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'no file was selected'}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400
        
        if not IS_ALLOWED_EXTENSIONS(file.filename):
            return jsonify({"error": 'The Extension Is Not Supported'}), 400
        
        #filename, filepath = get_secure_filename_filepath(file.filename)
        output = upload_to_s3(file, app.config['S3_BUCKET'])
        return jsonify({
            'message' : 'File successfully uploaded',
            'filename' : output
        }), 200
    
    images = []
    s3_resource = boto3.resource('s3', aws_access_key_id=app.config['S3_KEY'], aws_secret_access_key=app.config['S3_SECRET'])
    s3_bucket = s3_resource.Bucket(app.config['S3_BUCKET'])
    for obj in s3_bucket.objects.filter(Prefix='uploads/'):
        if obj.key == 'uploads/':
            continue
        images.append(obj.key)
    return jsonify({ 'data': images  })

@app.route('/downloads/<name>')
def download_file(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], name)


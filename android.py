import shutil
from flask import Blueprint, request, current_app, redirect, url_for
from PIL import Image
from helpers import get_secure_filename_filepath, download_from_s3
from zipfile import ZipFile
from datetime import datetime
import os

bp = Blueprint('android', __name__ )

@bp.route('/android', methods=['POST'])
def create_images():
    ICON_SIZES = [ 29, 40, 57, 58, 60, 80, 87, 114, 120, 180, 1024]

    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    tempfolder = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'temp')
    os.makedirs(tempfolder)

    
    for size in ICON_SIZES:
        file_stream = download_from_s3(filename)
        outfile = os.path.join(tempfolder, f'{size}.png')
        image = Image.open(file_stream)
        out = image.resize((size, size))
        out.save(outfile, 'PNG')

    now = datetime.now()
    timestamp = str(datetime.timestamp(now)).rsplit('.')[0]
    zipfilename = f'{timestamp}.zip'
    zipfilepath = os.path.join(current_app.config['DOWNLOAD_FOLDER'], zipfilename)

    with ZipFile(zipfilepath, 'w') as zipobj:
        for foldername, subfolders, filenames, in os.walk(tempfolder):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipobj.write(filepath, os.path.basename(filepath))
        shutil.rmtree(tempfolder)
        return redirect(url_for('download_file',name=zipfilename))
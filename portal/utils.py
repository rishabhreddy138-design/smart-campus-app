import os
import secrets
from werkzeug.utils import secure_filename
from flask import current_app

def save_file(form_file):
    """Saves an uploaded file to the filesystem with a secure, random name."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    picture_fn = random_hex + secure_filename(f_ext)
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_fn)
    form_file.save(picture_path)
    return picture_fn

def save_avatar(form_file):
    """Saves an uploaded avatar image with a secure, random name."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_file.filename)
    file_name = random_hex + secure_filename(f_ext)
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)
    form_file.save(picture_path)
    return file_name
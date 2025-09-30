# netlify_handler.py
from serverless_wsgi import handle
from run import app  # Imports the 'app' object from your run.py file

def handler(event, context):
    return handle(app, event, context)
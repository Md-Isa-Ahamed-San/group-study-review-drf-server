# myproject/firebase_config.py
import firebase_admin
from firebase_admin import credentials
import os
from django.conf import settings

def initialize_firebase_admin():
    # Best practice: Load credentials from environment variables or a secure path
    # For local development, you can point to the file path directly.
    cred_path = os.path.join(settings.BASE_DIR, './src/group-study-review-drf-server/firebase/serviceAccountKey.json')
    cred = credentials.Certificate(cred_path)

    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)

# Call the function to ensure it's initialized on startup
initialize_firebase_admin()
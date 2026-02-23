import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
import json

if not firebase_admin._apps:
    firebase_key = json.loads(os.environ["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_key)

    firebase_admin.initialize_app(cred, {
        'storageBucket': os.environ["FIREBASE_STORAGE_BUCKET"]
    })

db = firestore.client()
bucket = storage.bucket()

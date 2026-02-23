import uuid
from datetime import datetime

def generate_filename():
    return f"{uuid.uuid4()}.jpg"

def get_current_date():
    return datetime.now().strftime("%d.%m.%Y")

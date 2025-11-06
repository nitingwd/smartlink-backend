import string, random

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def get_unique_short_url(db, model, length=6):
    while True:
        short = generate_short_url(length)
        exists = db.query(model).filter(model.short_url == short).first()
        if not exists:
            return short

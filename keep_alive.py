from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 أنا شغّال يا غالي"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

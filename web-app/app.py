from flask import Flask
from db import get_history_collection

app = Flask(__name__)

@app.route("/")
def index():
    return "Web app running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
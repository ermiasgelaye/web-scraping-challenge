"""Mission to Mars: Flask app that scrapes Mars data into MongoDB and displays it.

Run with:  python app.py   (requires MongoDB at MONGO_URI, default localhost:27017)
"""
import os

from flask import Flask, redirect, render_template
from flask_pymongo import PyMongo

import scrape_mars

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/mars")
mongo = PyMongo(app)


@app.route("/")
def index():
    marspage = mongo.db.marspages.find_one() or {}
    return render_template("index.html", marspage=marspage)


@app.route("/scrape")
def scrape():
    marspage = scrape_mars.scrape()
    mongo.db.marspages.replace_one({}, marspage, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

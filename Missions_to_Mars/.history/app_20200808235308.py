from flask import Flask, render_template, redirect
import flask
import scrape_mars
import pymongo

app = Flask(__name__)

conn = 'mongodb://localhost:27017'

client = pymongo.MongoClient(conn)

db = client.mars


@app.route('/')
def index():
    mars = list(db.data.find())
    print(mars)

    return render_template('index.html', mars=mars)

@app.route('/scrape')
def scrapes():
    mars_data = scrape_mars.scrape()

    db.data.drop()
    db.data.insert_one(mars_data)

    return redirect('/')
    
if __name__ == "__main__":
    app.run(debug=True)
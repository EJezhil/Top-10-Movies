import datetime
import json

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Update, Delete
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)
app.app_context().push()

API_KEY = os.getenv('API_KEY')

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)


db.create_all()



@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating))
    movies_obj = movies.scalars().all()
    for i in range(len(movies_obj)):
        movies_obj[i].ranking = len(movies_obj) - i
    db.session.commit()
    return render_template("index.html", movies_objj=movies_obj)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_id = request.args.get('id')
    movies = db.session.execute(db.select(Movie).where(Movie.id == movie_id))
    movies_obj = movies.scalar()

    if request.method == "POST":
        movie_id = request.args.get('id')
        movie_rating = request.form["movie_rating"]
        movie_review = request.form["movie_review"]
        print(movie_review, movie_rating, movie_id)
        # insert into db table

        db.session.execute(Update(Movie).where(Movie.id == movie_id).values(rating=movie_rating, review=movie_review))
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("edit.html", movies_obj=movies_obj)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    db.session.execute(Delete(Movie).where(Movie.id == movie_id))
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        movie_search = request.form["search"]
        data = {
            "query": movie_search
        }
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=data, headers=headers)
        result = response.json()
        movie_result = result["results"]
        print(movie_result)

        return render_template("select.html", movies_list=movie_result)
    else:
        return render_template("add.html")


@app.route("/select", methods=["GET", "POST"])
def select():
    movie_id = request.args.get('id')
    movies_dict = eval(movie_id)
    print(movies_dict)
    year = movies_dict['release_date'].split("-")[0]
    movie_add = Movie(
        title=movies_dict['original_title'],
        year=year,
        description=movies_dict['overview'],
        rating=0,
        ranking=1,
        review="",
        img_url=f"https://www.themoviedb.org/t/p/original/{movies_dict['poster_path']}"
    )
    db.session.add(movie_add)
    db.session.commit()

    return redirect(url_for('edit',id=movie_add.id))


if __name__ == '__main__':
    app.run(debug=True)

movie_path = "https://www.themoviedb.org/t/p/original/"

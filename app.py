import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_exercices")
def get_exercices():
    exercices = list(mongo.db.exercices.find())
    return render_template("exercices.html", exercices=exercices)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    exercices = list(mongo.db.exercices.find({"$text": {"$search": query}}))
    return render_template("exercices.html", exercices=exercices)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
        
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

	
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_exercice", methods=["GET", "POST"])
def add_exercice():
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    if request.method == "POST":
        exercice_comment = ""
        is_done = "no"
        exercice = {
            "program_name": request.form.get("program_name"),
            "exercice_name": request.form.get("exercice_name"),
            "exercice_link": request.form.get("exercice_link"),
            "is_done": is_done,
            "exercice_comment": exercice_comment,
            "exercice_date_added": timestamp,
            "created_by": session["user"]
        }
        mongo.db.exercices.insert_one(exercice)
        flash("Exercice Successfully Added")
        return redirect(url_for("get_exercices"))
        
    programs = mongo.db.programs.find().sort("program_name", 1)
    return render_template("add_exercice.html", programs=programs)


@app.route("/edit_exercice/<exercice_id>", methods=["GET", "POST"])
def edit_exercice(exercice_id):
    if request.method == "POST":
        is_done = "yes" if request.form.get("is_done") else "no"
        submit = {
            "program_name": request.form.get("program_name"),
            "exercice_name": request.form.get("exercice_name"),
            "exercice_link": request.form.get("exercice_link"),
            "is_done": is_done,
            "exercice_comment": request.form.get("exercice_comment"),
            "created_by": session["user"]
        }
        mongo.db.exercices.update({"_id": ObjectId(exercice_id)}, submit)
        flash("Exercice Successfully Updated")
        return redirect(url_for("get_exercices"))

    exercice = mongo.db.exercices.find_one({"_id": ObjectId(exercice_id)})
    programs = mongo.db.programs.find().sort("program_name", 1)
    return render_template("edit_exercice.html", exercice=exercice, programs=programs)


@app.route("/delete_exercice/<exercice_id>")
def delete_exercice(exercice_id):
    mongo.db.exercices.remove({"_id": ObjectId(exercice_id)})
    flash("Exercice Successfully Deleted")
    return redirect(url_for("get_exercices"))


@app.route("/get_programs")
def get_programs():
    programs = list(mongo.db.programs.find().sort("program_name", 1))
    return render_template("programs.html", programs=programs)


@app.route("/add_program", methods=["GET", "POST"])
def add_program():
    if request.method == "POST":
        program = {
            "program_name": request.form.get("program_name")
        }
        mongo.db.programs.insert_one(program)
        flash("New Program Added")
        return redirect("get_programs")

    return render_template("add_program.html")


@app.route("/edit_program/<program_id>", methods=["GET", "POST"])
def edit_program(program_id):
    if request.method == "POST":
        submit = {
            "program_name": request.form.get("program_name")
        }
        mongo.db.programs.update({"_id": ObjectId(program_id)}, submit)
        flash("Program Successfully Updated")
        return redirect(url_for("get_programs"))

    program = mongo.db.programs.find_one({"_id": ObjectId(program_id)})
    return render_template("edit_program.html", program=program)


@app.route("/delete_program/<program_id>")
def delete_program(program_id):
    mongo.db.programs.remove({"_id": ObjectId(program_id)})
    flash("Program Successfully Deleted")
    return redirect(url_for("get_programs"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

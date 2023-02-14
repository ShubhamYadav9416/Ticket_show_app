from flask import request, render_template, url_for, redirect, flash, session
from sqlalchemy import delete
from datetime import datetime

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import current_app as app
from application.models import *

bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
 
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        page = "login"
        submit_name="Sign In"
        return render_template("login.html",page=page, submit_name = submit_name)
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
        else:
            flash("You are not registerd")
            return redirect("/login")



@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        page = "register"
        submit_name="Register"
        return render_template("login.html",page=page, submit_name=submit_name)
    if request.method == "POST":
        email = request.form["email"]
        existing_email = User.query.filter_by(email = email).first()
        if existing_email:
            flash("email already register")
            return redirect("/login")
        else:
            password = request.form["password"]
            hashed_password = bcrypt.generate_password_hash(password)
            new_user= User(email=email,password = hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("You are now registered, Please Login.")
            return redirect("/login")



@app.route("/forget_password",methods=["GET","POST"])
def forget_password():
    if request.method == "GET":
        page = "forget_password"
        submit_name="Submit"
        return render_template("login.html",page=page, submit_name=submit_name)

@app.route("/", methods=["GET","POST"])
@login_required
def home():
    if request.method== "GET":
        email = current_user.email
        user = email.split("@")[0]
        shows = Show.query.all()
        shows_place_locations = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Venu.place).all()
        shows_place_tags = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Show.show_tag).all()
        return render_template("home.html",filter_by_location = "True",filter_by_tag="True",user=user,shows = shows,shows_place_tags=shows_place_tags ,shows_place_locations = shows_place_locations, heading1= "Recently Added")
    
@app.route('/ticket_booking/<int:id>')
@login_required
def ticket_booking(id):
    show=Show.query.filter_by(show_id = id).first()
    venu_name = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Venu.venu_name).all()
    venu_place = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Venu.place).all()
    no_show=False
    venu_with_places=[]
    if len(venu_name)>0:
        for i in range(len(venu_name)):
            venu_with_places.append(venu_name[i][1] + " (" + venu_place[i][1] + ")")
    else:
        no_show=True
    # print(venu_with_places)
    email = current_user.email
    user = email.split("@")[0]
    return render_template("show_page.html",show = show,user=user,venu_with_places=venu_with_places,no_show=no_show)

@app.route("/filter_by_location/<place>")
@login_required
def filter_by_location(place):
    show_ids = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).filter(Venu.place == place).add_columns(Show_venu.show_id).all()
    shows=[]
    for show_id in show_ids:
        shows.append(Show.query.filter_by(show_id=show_id[1]).first())
    heading1= str("Shows in ") + place
    return render_template("home.html", filter_by_location = "False",filter_by_tag = "False", shows=shows,heading1=heading1)

@app.route("/filter_by_tag/<tag>")
@login_required
def filter_by_tag(tag):
    show_ids = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).filter(Show.show_tag == tag).add_columns(Show_venu.show_id).all()
    shows=[]
    for show_id in show_ids:
        shows.append(Show.query.filter_by(show_id=show_id[1]).first())
    heading1 = tag + str(" Genere Shows")
    return render_template("home.html", filter_by_location = "False", filter_by_tag="False",shows=shows, heading1 = heading1)

@app.route("/book_ticket")
@login_required
def book_ticket():
    return ("hello")

@app.route("/add_rating/<int:id>",methods=["POST"])
@login_required
def add_rating(id):
    show_venu_id = id
    show_venu = Show_venu.query.filter_by(show_venu_id=show_venu_id).first()
    show_id = show_venu["show_id"]
    rating = request.form[""]

@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


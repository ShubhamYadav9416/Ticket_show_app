from flask import request, render_template, url_for, redirect, flash, session
from sqlalchemy import delete
from datetime import datetime
from decimal import Decimal

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
                flash("Wrong Password")
                return redirect("/login")
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
        shows_not_unique_locations = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Venu.place).all()
        shows_not_unique_tags = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Show.show_tag).all()
        shows_locations = unique(shows_not_unique_locations)
        shows_tags = unique(shows_not_unique_tags)

        return render_template("home.html",filter_result = False, filter_by_location = "True",filter_by_tag="True",user=user,shows = shows,shows_tags=shows_tags ,shows_locations = shows_locations, heading1= "Recently Added")

def unique(dict): #to select unique tags and places for filter in home page
    list = []  
    for object in dict:
        list.append(object[1])
    set_list = set(list)
    unique_list = (set_list)
    return unique_list
        
@app.route('/ticket_booking/<int:id>')
@login_required
def ticket_booking(id):
    show=Show.query.filter_by(show_id = id).first()
    show_venu = Show_venu.query.join(Show, Venu).filter(Show_venu.show_id == id).filter(Show_venu.venu_id== Venu.venu_id).add_columns(Venu.venu_name,Venu.place,Show_venu.show_venu_id,Venu.capacity,Show_venu.show_price,Show_venu.show_timing).all()
    no_show=False
    total_venu_of_show = len(show_venu)
    print(total_venu_of_show)
    venu_with_places={}
    if total_venu_of_show>0:
        for i in range(len(show_venu)):
            venu_with_places[i]= show_venu[i][1] + " (" + show_venu[i][2] + ")"
    else:
        no_show=True
    
    email = current_user.email
    user = email.split("@")[0]
    show_rating = Show_rating.query.filter_by(show_id= id).first()
    if show_rating != None:
        rating_avg = show_rating.rating / show_rating.no_of_rating
        rate_template = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
    else:
        rate_template = "None"
    
    show_venu_id_with_current_price = {}
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = i+1).first()
        if dynamic == None:
            update_id = i+1
            seat_left = show_venu[i][4]
            current_price = show_venu[i][5]
            record = Dynamic(update_id,seat_left,current_price)
            db.session.add(record)
            db.session.commit()
            show_venu_id_with_current_price[i] = current_price
    
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = i+1).first()
        print(show_venu[i][6])
        update_price = calculate_dynamic_cost(dynamic.seat_left, dynamic.current_price,show_venu[i][6])
        dynamic.current_price = update_price
        db.session.commit()
        show_venu_id_with_current_price[i] = update_price
    return render_template("show_page.html",show = show,user=user,venu_with_places=venu_with_places,no_show=no_show,rate_template=rate_template,show_venu_id_with_current_price=show_venu_id_with_current_price, total_venu_of_show = total_venu_of_show)


def calculate_dynamic_cost(num_seats_left, current_price, show_start_time):
    if num_seats_left == 0:
        return None  # No tickets available

    # Calculate the price multiplier based on the number of seats left
    price_multiplier = 1.0
    if num_seats_left < 10:
        price_multiplier += 0.5
    elif num_seats_left < 15:
        price_multiplier += 0.3
    elif num_seats_left < 25:
        price_multiplier += 0.2
    elif num_seats_left < 50:
        price_multiplier += 0.1

    show_start_time = datetime.strptime(str(show_start_time), '%Y-%m-%d %H:%M:%S')  # Convert the show start time string to a datetime object
    time_left = show_start_time - datetime.now()
    time_multiplier = 1.0
    if time_left.days == 0 and time_left.seconds < 3600:  # Less than 1 hour left
        time_multiplier += 0.75
    elif time_left.days == 0 and time_left.seconds < 7200: # Less than 2 hours left
        time_multiplier += 0.5
    elif time_left.days == 1 and time_left.seconds < 3600:  # Less than 1 day 1 hour left
        time_multiplier += 0.4
    elif time_left.days == 2 and time_left.seconds < 3600:  # Less than 2 days 1 hours left
        time_multiplier += 0.25
    elif time_left.days == 3 and time_left.seconds < 3600:  # Less than 3 days 1 hours left
        time_multiplier += 0.15

    # Calculate the dynamic cost of the ticket
    dynamic_cost = current_price * price_multiplier * time_multiplier
    return dynamic_cost


@app.route("/filter_by_location/<place>")
@login_required
def filter_by_location(place):
    email = current_user.email
    user = email.split("@")[0]
    show_ids = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).filter(Venu.place == place).add_columns(Show_venu.show_id).all()
    shows=[]
    for show_id in show_ids:
        shows.append(Show.query.filter_by(show_id=show_id[1]).first())
    heading1= str("Shows in ") + place
    return render_template("home.html",filter_result=True, user=user, filter_by_location = "False",filter_by_tag = "False", shows=shows,heading1=heading1)

@app.route("/filter_by_tag/<tag>")
@login_required
def filter_by_tag(tag):
    email = current_user.email
    user = email.split("@")[0]
    show_ids = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).filter(Show.show_tag == tag).add_columns(Show_venu.show_id).all()
    shows=[]
    for show_id in show_ids:
        shows.append(Show.query.filter_by(show_id=show_id[1]).first())
    heading1 = tag + str(" Genere Shows")
    return render_template("home.html",filter_result=True,user = user, filter_by_location = "False", filter_by_tag="False",shows=shows, heading1 = heading1)

@app.route("/book_ticket",methods=["POST"])
@login_required
def book_ticket():
    user_id = current_user.id
    show_venu_id = request.form["show_venu_id"]
    number_of_ticket_booked = request.form["no_of_ticket"]
    cost_at_the_time_of_ticket_booking = request.form["price"]
    time_of_ticket_booked = datetime.now()
    record = Ticket_booked(user_id,show_venu_id,number_of_ticket_booked,cost_at_the_time_of_ticket_booking,time_of_ticket_booked)
    db.session.add(record)
    db.session.commit()
    return ("hello")

@app.route("/add_rating/<int:id>",methods=["POST"])
@login_required
def add_rating(id):
    show_id = id
    rating = request.form["rating"]
    show_rating = Show_rating.query.filter_by(show_id = show_id).first()
    if show_rating == None:
        no_of_rating = 1
        record = Show_rating(show_id, rating,no_of_rating)
        db.session.add(record)
        db.session.commit()
        return redirect(url_for("ticket_booking", id = show_id))
    else:
        show_rating.rating += int(rating)
        show_rating.no_of_rating += 1
        db.session.commit()
        return redirect(url_for("ticket_booking", id = show_id))
    


@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


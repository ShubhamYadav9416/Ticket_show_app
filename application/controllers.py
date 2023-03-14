from flask import request, render_template, url_for, redirect, flash, session
from sqlalchemy import delete
from datetime import datetime
from decimal import Decimal

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import current_app as app
from application.models import *
from application.functions import *

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

        show_rating_templates ={}
        for show in shows:
            show_rating = Show_rating.query.filter_by(show_id= show.show_id).first()
            if show_rating != None:
                rating_avg = show_rating.rating / show_rating.no_of_rating
                show_rating_templates[show.show_id] = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
            else:
                show_rating_templates[show.show_id] = "None"
        return render_template("home.html",filter_result = False,show_rating_templates=show_rating_templates, filter_by_location = "True",filter_by_tag="True",user=user,shows = shows,shows_tags=shows_tags ,shows_locations = shows_locations, heading1= "Recently Added")


        

@app.route('/profile')
@login_required
def profile():
    user_email=current_user.email
    user_name = user_email.split("@")[0]
    user_id = current_user.id
    tickets_booked_by_user = Ticket_booked.query.filter_by(user_id=user_id).all()
    ticket_details=[]
    no_ticket_booked=False
    if tickets_booked_by_user == []:
        no_ticket_booked = True 
    elif tickets_booked_by_user != []:
        for ticket_booked_by_user in tickets_booked_by_user:
            dict={}
            show_venu_id=ticket_booked_by_user.show_venu_id
            show_venu = Show_venu.query.join(Show, Venu).filter(Show_venu.show_venu_id==show_venu_id).filter(Show_venu.venu_id== Venu.venu_id).filter(Show_venu.show_id == Show.show_id).add_columns(Show.show_name,Show.show_lang,Venu.venu_name,Venu.place,Venu.location,Show_venu.show_timing,Show.show_image_path).first()
            dict["booking_id"] = ticket_booked_by_user.booking_id
            dict["show"]  = str(show_venu[1]) + "(" + str(show_venu[2]) + ")" #show name with show language
            dict["venu"] = str(show_venu[3]) + " " + str(show_venu[4])  #venu name with venu place
            dict["venu_location"] = show_venu[5]   #venu location
            dict["show_timming"] = str(show_venu[6])[11:16] + "pm |" + str(show_venu[6])[:10]
            dict["image_path"] = show_venu[7]
            dict["quantity"] = ticket_booked_by_user.number_of_ticket_booked
            dict["ticket_price"] = ticket_booked_by_user.cost_at_the_time_ticket_booking
            ticket_details.append(dict)
    return render_template("profile.html",no_ticket_booked=no_ticket_booked, user_email=user_email,user_name=user_name,ticket_details=ticket_details)


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

    show_rating_templates ={}
    for show in shows:
        show_rating = Show_rating.query.filter_by(show_id= show.show_id).first()
        if show_rating != None:
            rating_avg = show_rating.rating / show_rating.no_of_rating
            show_rating_templates[show.show_id] = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
        else:
            show_rating_templates[show.show_id] = "None"
    return render_template("home.html",filter_result=True,show_rating_templates=show_rating_templates, user=user, filter_by_location = "False",filter_by_tag = "False", shows=shows,heading1=heading1)

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

    show_rating_templates ={}
    for show in shows:
        show_rating = Show_rating.query.filter_by(show_id= show.show_id).first()
        if show_rating != None:
            rating_avg = show_rating.rating / show_rating.no_of_rating
            show_rating_templates[show.show_id] = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
        else:
            show_rating_templates[show.show_id] = "None"
    return render_template("home.html",show_rating_templates=show_rating_templates, filter_result=True,user = user, filter_by_location = "False", filter_by_tag="False",shows=shows, heading1 = heading1)

@app.route('/ticket_booking/<int:id>')
@login_required
def ticket_booking(id):
    show=Show.query.filter_by(show_id = id).first()
    show_venu = Show_venu.query.join(Show, Venu).filter(Show_venu.show_id == id).filter(Show_venu.venu_id== Venu.venu_id).add_columns(Venu.venu_name,Venu.place,Show_venu.show_venu_id,Venu.capacity,Show_venu.show_price,Show_venu.show_timing,Show_venu.show_price).all()
    no_show=False
    check_availablity= True
    total_venu_of_show = len(show_venu)


    #attaching venu name with venu placing and making dictionary
    venu_with_places={}
    if total_venu_of_show>0:
        for i in range(len(show_venu)):
            venu_with_places[show_venu[i][3]]= show_venu[i][1] + " (" + show_venu[i][2] + ")"
    else:
        no_show=True
    
    email = current_user.email
    user = email.split("@")[0]

    #show raing in wite format
    show_rating = Show_rating.query.filter_by(show_id= id).first()
    if show_rating != None:
        rating_avg = show_rating.rating / show_rating.no_of_rating
        rate_template = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
    else:
        rate_template = "None"
    
    show_venu_id_with_current_price = {}
    # initiallize dynamic database
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
        if dynamic == None:
            update_id = show_venu[i][3]
            seat_left = show_venu[i][4]
            current_price = show_venu[i][5]
            record = Dynamic(update_id,seat_left,current_price)
            db.session.add(record)
            db.session.commit()
            show_venu_id_with_current_price[i] = current_price
    
    #calculating and collecting dynamic price
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
        starting_price_of_ticket =show_venu[i][7]
        show_start_time = show_venu[i][6]
        total_seats= show_venu[i][4]
        update_price = calculate_dynamic_cost(dynamic.seat_left,total_seats,starting_price_of_ticket,show_start_time)
        dynamic.current_price = update_price
        db.session.commit()
        show_venu_id_with_current_price[i] = update_price

    # Stop taking booking when time of show pass
    show_start_time = Show_venu

    # stop taking more booking in case of house full and ristricting booking more ticket than available
    seat_restriction={}
    for i in range(total_venu_of_show):
        dict={}
        dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
        max_ticket_at_once=9
        if dynamic.seat_left <9:
            max_ticket_at_once = dynamic.seat_left
        dict["max"]= max_ticket_at_once
        dict["no_of_seats_left"] = dynamic.seat_left
        seat_restriction[i] = dict



    return render_template("show_page.html",show_id = id,show = show,user=user,check_availablity=check_availablity,venu_with_places=venu_with_places,no_show=no_show,rate_template=rate_template,show_venu_id_with_current_price=show_venu_id_with_current_price, total_venu_of_show = total_venu_of_show,seat_restriction=seat_restriction)

@app.route("/check_availablity/<int:id>",methods=["POST"])
def check_availablity(id):
    show_venu_id = int(request.form["show_venu_id"])
    take_booking =True

    show=Show.query.filter_by(show_id = id).first()
    show_venu = Show_venu.query.join(Show, Venu).filter(Show_venu.show_id == id).filter(Show_venu.venu_id== Venu.venu_id).add_columns(Venu.venu_name,Venu.place,Show_venu.show_venu_id,Venu.capacity,Show_venu.show_price,Show_venu.show_timing,Show_venu.show_price).all()
    no_show=False
    total_venu_of_show = len(show_venu)

    #attaching venu name with venu placing and making dictionary
    venu_with_places={}
    if total_venu_of_show>0:
        for i in range(len(show_venu)):
            venu_with_places[i]= show_venu[i][1] + " (" + show_venu[i][2] + ")"
    else:
        no_show=True
    
    email = current_user.email
    user = email.split("@")[0]

    #show raing in wite format
    show_rating = Show_rating.query.filter_by(show_id= id).first()
    if show_rating != None:
        rating_avg = show_rating.rating / show_rating.no_of_rating
        rate_template = str(Decimal(rating_avg).quantize(Decimal("1.0")))+"/"+"5"+"  "+ str(show_rating.no_of_rating)+" votes"
    else:
        rate_template = "None"
    
    show_venu_id_with_current_price = {}
    # initiallize dynamic database
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
        if dynamic == None:
            update_id = show_venu[i][3]
            seat_left = show_venu[i][4]
            current_price = show_venu[i][5]
            record = Dynamic(update_id,seat_left,current_price)
            db.session.add(record)
            db.session.commit()
            show_venu_id_with_current_price[i] = current_price
    
    #calculating and collecting dynamic price
    for i in range(total_venu_of_show):
        dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
        starting_price_of_ticket =show_venu[i][7]
        show_start_time = show_venu[i][6]
        total_seats= show_venu[i][4]
        update_price = calculate_dynamic_cost(dynamic.seat_left,total_seats,starting_price_of_ticket,show_start_time)
        dynamic.current_price = update_price
        db.session.commit()
        show_venu_id_with_current_price[i] = update_price

    # stop taking more booking in case of house full and ristricting booking more ticket than available
    dynamic = Dynamic.query.filter_by(update_id = show_venu[i][3]).first()
    max_ticket_at_once=9
    if dynamic.seat_left <9:
        max_ticket_at_once = dynamic.seat_left
    max= max_ticket_at_once
    no_of_seats_left = dynamic.seat_left
    cost_per_ticket = dynamic.current_price

    return render_template("show_page.html",show = show,user=user,max=max,cost_per_ticket=cost_per_ticket ,no_of_seats_left=no_of_seats_left, take_booking=take_booking,show_venu_id=show_venu_id,venu_with_places=venu_with_places,no_show=no_show,rate_template=rate_template,show_venu_id_with_current_price=show_venu_id_with_current_price, total_venu_of_show = total_venu_of_show) 

@app.route("/book_ticket/<int:id>",methods=["POST"])
@login_required
def book_ticket(id):
    user_id = current_user.id
    show_venu_id = id
    number_of_ticket_booked = request.form["no_of_ticket"]
    dynamic = Dynamic.query.filter_by(update_id = show_venu_id).first()
    dynamic.seat_left = int(dynamic.seat_left) - int(number_of_ticket_booked)
    cost_at_the_time_of_ticket_booking = dynamic.current_price
    time_of_ticket_booked = datetime.now()
    record = Ticket_booked(user_id,show_venu_id,number_of_ticket_booked,cost_at_the_time_of_ticket_booking,time_of_ticket_booked)
    db.session.add(record)
    db.session.commit()
    return redirect("/profile")

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
    

@app.route("/remove_booked_ticket/<int:booking_id>")
@login_required
def remove_booked_ticket(booking_id):
    ticket_book = Ticket_booked.query.filter_by(booking_id=booking_id).first()
    db.session.delete(ticket_book)
    db.session.commit()
    return redirect('/profile')

@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect("/login")


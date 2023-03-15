from flask import request, render_template, url_for, redirect, flash, session
from sqlalchemy import delete
from datetime import datetime
from matplotlib import pyplot as plt

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import current_app as app
from application.models import *

@app.route("/admin_login", methods=["GET","POST"])
def admin_login():
    if request.method == "GET":
        submit_name="Sign In"
        return render_template("login.html",admin="True" , submit_name=submit_name)
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if (email == "admin_user@gmail.com" and password=="1234"):
            session['email'] = email
            return redirect('/admin')

@app.route("/admin_logout")
def admin_logout():
    session.pop('email',None)
    return redirect('/login')

@app.route("/admin")
def admin():
    if ('email' in session):
        dashboard=True

        # find total sale and total  ticket booked.
        tickets = Ticket_booked.query.all()
        total_ticket_booked = 0
        total_sale = 0
        for ticket in tickets:
            total_ticket_booked += ticket.number_of_ticket_booked 
            total_sale += ticket.cost_at_the_time_ticket_booking * ticket.number_of_ticket_booked 
        # find top rating of any show and top 3 rated show
        shows_ratings = Show_rating.query.select_from(Show).filter(Show_rating.show_id == Show.show_id).add_columns(Show.show_name,Show_rating.show_id,Show_rating.rating,Show_rating.no_of_rating).all()
        rating_with_show_id = {}
        for show_rating in shows_ratings:
            rating_with_show_id[show_rating.show_id] = show_rating.rating / show_rating.no_of_rating
        sorted_dict_rating_with_show_id = sorted(rating_with_show_id.items(),key=lambda x: x[1]) #sorted with values
        low_to_high_show_rating_show_id = [item[0] for item in sorted_dict_rating_with_show_id]
        top_rated_show_rating = "{0:.1f}".format(sorted_dict_rating_with_show_id[-1][1])
        top_3_rated_shows = []
        rank=1
        for i in range(-1,-4,-1):
            for show_rating in shows_ratings:
                if (low_to_high_show_rating_show_id[i] == show_rating.show_id):
                    show = (rank,show_rating.show_name[0:8],show_rating.no_of_rating,"{0:.1f}".format(show_rating.rating / show_rating.no_of_rating))
                    top_3_rated_shows.append(show)
                    rank = rank +1

        #find total user
        users = User.query.all()
        total_user =0
        for user in users:
            total_user = total_user+1

        #find no of shows booking running in any venu
        show_venus = Show_venu.query.all()
        shows_booking_running = 0
        for  show_venu in show_venus:
            show_start_time = datetime.strptime(str(show_venu.show_timing), '%Y-%m-%d %H:%M:%S')  # Convert the show start time string to a datetime object
            if (show_start_time > datetime.now()):
                shows_booking_running = shows_booking_running +1
        
        # find top 3 revenue generating shows
        # find show name with ticket booked for that show
        shows = Show.query.all()
        show_ids =[]
        for show in shows:
            show_ids.append(show.show_id)
        show_ids_with_show_venu_ids = {}
        for show_id in show_ids:
            show_venu_ids = []
            show_venus = Show_venu.query.filter_by(show_id = show_id).all()
            for show_venu in show_venus:
                show_venu_ids.append(show_venu.show_venu_id)
            show_ids_with_show_venu_ids[show_id] = show_venu_ids
        tickets=Ticket_booked.query.all()
        show_id_with_collection={}
        show_id_with_ticket_booked ={}
        for show_id in show_ids:
            show_id_with_collection[show_id] = 0
            show_id_with_ticket_booked[show_id] = 0
        for show_id in show_ids:
            ticket_booked_of_each_show_id =0
            collection_of_each_show_id = 0
            for show_venu_id in show_ids_with_show_venu_ids[show_id]:
                ticket_booked_of_each_show_venu_id =0
                collection_of_each_show_venu_id = 0
                for ticket in tickets:
                    if ticket.show_venu_id == show_venu_id:
                        collection_of_each_show_venu_id += ticket.number_of_ticket_booked * ticket.cost_at_the_time_ticket_booking
                        ticket_booked_of_each_show_venu_id += ticket.number_of_ticket_booked
                collection_of_each_show_id += collection_of_each_show_venu_id
                ticket_booked_of_each_show_id += ticket_booked_of_each_show_venu_id
            show_id_with_collection[show_id] += collection_of_each_show_id
            show_id_with_ticket_booked[show_id] += ticket_booked_of_each_show_id
        
        sorted_dict_revenue_with_show_id = sorted(show_id_with_collection.items(),key=lambda x: x[1]) #sorted with values
        low_to_high_show_revenue_show_id = [item[0] for item in sorted_dict_revenue_with_show_id]
       
        top_3_revenue_shows =[]
        rank =1
        for i in range(-1,-4,-1):
            for show in shows:
                if show.show_id == low_to_high_show_revenue_show_id[i]:
                    show_name_with_revenue = (rank,(show.show_name)[0:8],show_id_with_collection[low_to_high_show_revenue_show_id[i]])
                    top_3_revenue_shows.append(show_name_with_revenue)
                    rank =rank +1
        
        # plot bar chart save it in static
        x=[]
        y=[]
        for show in shows:
            x.append(show.show_name[0:8])
            y.append(show_id_with_ticket_booked[show.show_id])
        plt.bar(x,y)
        plt.xlabel("Shows")
        plt.ylabel("Ticket booked")
        plt.title("Shows with ticket booked")
        plt.savefig('./static/image/show_ticket_booked_bar.png')

        return render_template('admin.html',dashboard=dashboard,total_sale=total_sale,total_ticket_booked=total_ticket_booked,top_rated_show_rating=top_rated_show_rating,top_3_rated_shows=top_3_rated_shows,total_user=total_user,shows_booking_running=shows_booking_running,top_3_revenue_shows=top_3_revenue_shows)
    else:
        return ("You are not allowed to access admin page")

@app.route('/venu_admin', methods=["GET","POST"])
def venu():
        if ('email' in session):
            venus = Venu.query.all()
            heading = "All Venus"
            main_contents = venus
            heads = ["No.", "Venu Name", "Capacity", "Place", "Location", "Action"]
            box_contents = ["venu_id" , "venu_name" , "capacity" , "location", "place"]
            url1 = "edit_venu" 
            url2 = "delete_venu"
            id = "venu_id"
            button_url ="add_venu"
            button = "Add Venu"
            return render_template('admin.html',display_table = "True", take_input = "False", edit_delete = "True" ,input_button="True", heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents, button_url = button_url, button_name = button, url1 = url1, url2 = url2, id = id)
        else:
            return ("You are not allowed to access admin page")
        

@app.route('/add_venu',methods=["GET","POST"])
def add_venu():
    if ('email' in session):
        if request.method == "GET":
            heading = "Add Venus"
            form_conditions = [{"type": "text", "name": "venu_name", "placeholder" : "venu", "required": "True"}, {"type": "number", "name": "capacity", "placeholder" : "capacity", "required": "True"}, {"type": "text", "name": "place", "placeholder" : "place", "required": "True"}, {"type": "text", "name": "location", "placeholder" : "location", "required": "True"}]
            return render_template("admin.html", take_input="True",special_form="False", display_table = "False", heading=heading, form_conditions=form_conditions)
        if request.method == "POST":
            venu_name = request.form['venu_name']
            capacity = request.form['capacity']
            place = request.form['place']
            location = request.form['location']
            record=Venu(venu_name ,capacity,place,location )
            db.session.add(record)
            db.session.commit()
            return redirect('/venu_admin')
    else:
        return ("You are not allowed to access admin page")
    
@app.route('/edit_venu/<int:id>',methods=["POST","GET"])
def edit_venu(id):
    if ('email' in session):
        content=Venu.query.filter_by(venu_id=id).first()
        return render_template('edit_venu.html', content=content)
    else:
        return ("You are not allowed to access admin page")

@app.route('/update_venu/<int:id>',methods=["GET","POST"])
def update_venu(id):
    if ('email' in session):
        if request.method=="POST":
            content = Venu.query.filter_by(venu_id=id).first()
            content.venu_name = request.form['venu_name']
            content.capacity = request.form['capacity']
            content.place = request.form['place']
            content.location = request.form['location']
            # db.session.add(content)
            db.session.commit()
            return redirect('/venu_admin')
    else:
        return ("You are not allowed to access admin page")

@app.route("/delete_venu/<int:id>")
def delete_venu(id):
    if ('email' in session):
        content=Venu.query.filter_by(venu_id=id).first()
        db.session.delete(content)
        db.session.commit()
        content_linked = delete(Show_venu).where(Show_venu.venu_id == id)
        db.session.execute(content_linked)
        db.session.commit()
        return redirect('/venu_admin')
    else:
        return ("You are not allowed to access admin page")

        
@app.route('/show_admin', methods=["GET","POST"])
def show():
    if ('email' in session):
        shows = Show.query.all()
        heading = "All Show"
        main_contents = shows
        heads = ["No.", "Show Name", "Tags","Language","Duration", "Discription", "Poster", "Action"]
        box_contents = ["show_id" , "show_name" , "show_tag","show_lang", "show_duration", "show_discription"]
        additional1 = ["show_image_path"]
        url1 = "edit_show" 
        url2 = "delete_show"
        id = "show_id"
        button_url ="add_show"
        button = "Add Show"
        return render_template('admin.html',display_table = "True", take_input = "False", edit_delete = "True" ,input_button="True",heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents, additional1 = additional1, button_url = button_url, button_name = button, url1 = url1, url2 = url2, id = id)
    else:
        return ("You are not allowed to access admin page")


@app.route('/add_show',methods=["GET","POST"])
def add_show():
    if ('email' in session):
        if request.method == "GET":
            heading = "Add Show"
            form_conditions=[{"type":"text" ,"name":"show_name", "placeholder":"show" ,"required":"True"},
                             {"type":"text", "name":"show_tag", "placeholder":"tag(required)", "required":"True"},
                             {"type":"text", "name":"show_lang","placeholder":"language of show","required":"True"},
                             {"type":"text","name":"show_duration","placeholder":"duration(hh:mm:ss)","required":"True"},
                             {"type":"text" ,"name":"show_discription", "placeholder":"About Show", "required":"False"},
                             {"type":"file" ,"name":"file" ,"placeholder":"upload poster",  "required":"True"}]
            return (render_template("admin.html", take_input="True",special_form="False", display_table = "False", heading=heading, form_conditions=form_conditions))
        if request.method == "POST":
            show_name = request.form['show_name']
            show_tag = request.form['show_tag']
            show_discription = request.form['show_discription']
            show_lang = request.form['show_lang']
            show_duration = request.form['show_duration']
            f=request.files['file']
            f.save('static/image/poster/'+f.filename)
            show_image_path = str('static/image/poster/'+f.filename)
            record=Show(show_name ,show_tag, show_discription,show_lang,show_duration, show_image_path )
            db.session.add(record)
            db.session.commit()
            return redirect('/show_admin')
    else:
        return ("You are not allowed to access admin page")

@app.route('/edit_show/<int:id>',methods=["POST","GET"])
def edit_show(id):
    if ('email' in session):
        content=Show.query.filter_by(show_id=id).first()
        return render_template('edit_show.html', content=content)
    else:
        return ("You are not allowed to access admin page")

@app.route('/update_show/<int:id>',methods=["GET","POST"])
def update_show(id):
    if ('email' in session):
        if request.method=="POST":
            content=Show.query.filter_by(show_id=id).first()
            content.show_name = request.form['show_name']
            # content.show_tag = request.form['show_tag']
            content.show_discription = request.form['show_discription']
            content.show_duration = request.form['show_duration']
            # f=request.files['show_image_name']
            # f.save('static/image/poster'+f.filename)
            # content.show_image_path = 'static/image/poster'+f.filename
            # db.session.add(content)
            db.session.commit()
            return redirect('/show_admin')
    else:
        return ("You are not allowed to access admin page")

@app.route("/delete_show/<int:id>")
def delete_show(id):
    if ('email' in session):
        content=Show.query.filter_by(show_id=id).first()
        db.session.delete(content)
        db.session.commit()
        return redirect('/show_admin')
    else:
        return ("You are not allowed to access admin page")

@app.route('/show_venu_admin', methods=["GET","POST"])
def show_venu():
    if ('email' in session):
        show_venus = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Show_venu.show_venu_id,Venu.venu_name, Show.show_name, Show_venu.show_price, Show_venu.show_timing ,Show_venu.show_added_timing).all()
        heading = "Shows with Booking Online"
        show_venu_of_running_shows=[]
        show_venu_of_past_shows = []
        for  show_venu in show_venus:
            show_start_time = datetime.strptime(str(show_venu["show_timing"]), '%Y-%m-%d %H:%M:%S')  # Convert the show start time string to a datetime object
            if (show_start_time < datetime.now()):
                show_venu_of_past_shows.append(show_venu)
            else:
                show_venu_of_running_shows.append(show_venu)
        main_contents = show_venu_of_running_shows
        past_show = True
        main_contents_past_shows = show_venu_of_past_shows
        heads = ["Show Venu Id", "Show Name", "Venu Name", "Price Of Ticket", "Show Timing", "Show Added Timing"]
        box_contents = ["show_venu_id" , "show_name" , "venu_name" , "show_price", "show_timing", "show_added_timing"]
        button = "Book Show Venu"
        button_url = "book_show_venu"
        return render_template('admin.html' ,display_table = "True", take_input = "False", edit_delete = "False" ,input_button="True", heading=heading, main_contents = main_contents,past_show = past_show ,main_contents_past_shows=main_contents_past_shows, heads = heads, box_contents = box_contents, button_name = button, button_url = button_url)
    else:
        return ("You are not allowed to access admin page")

@app.route("/book_show_venu",methods=["GET","POST"])
def book_show_venu():
    if ('email' in session):
        if request.method == "GET":
            venu=Venu.query.all()
            show=Show.query.all()
            heading = "Book Show Venu"
            return render_template("admin.html", take_input="True",special_form="True", display_table = "False", heading=heading, venus = venu, shows=show)
        if request.method == "POST":
            venu=request.form['venu_name']
            show=request.form['show_name']
            price=request.form['price']
            show_time=request.form['showtime']
            show_time = datetime.strptime(show_time,"%Y-%m-%dT%H:%M")
            show_added_timing = datetime.now()
            venu_full = Venu.query.filter_by(venu_name=venu).first()
            show_full = Show.query.filter_by(show_name=show).first()
            record = Show_venu(show = show_full,venu = venu_full, show_price = price ,show_timing = show_time, show_added_timing= show_added_timing)
            db.session.add(record)
            db.session.commit()
            return redirect('/show_venu_admin')
    else:
        return ("You are not allowed to access admin page")
    
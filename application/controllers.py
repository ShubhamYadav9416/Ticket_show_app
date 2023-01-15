from flask import Flask, request,redirect, session, render_template
from flask import current_app as app
from application.models import *
from sqlalchemy import delete
from datetime import datetime

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if (username == "admin_user@gmail.com" and password=="1234"):
            session['email'] = username
            return redirect('/admin')
        else:
            return ("invalid credentials")

@app.route("/admin_logout")
def admin_logout():
    session.pop('email',None)
    return redirect('/login')

@app.route("/admin")
def admin():
    if ('email' in session):
        return render_template('admin.html')
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
            ids = ["venu_id"]
            button_url ="add_venu"
            buttons = ["Add Venu"]
            return render_template('admin.html', heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents, button_url = button_url, buttons = buttons, url1 = url1, url2 = url2, ids = ids)
        else:
            return ("You are not allowed to access admin page")
        

@app.route('/add_venu',methods=["GET","POST"])
def add_venu():
    if ('email' in session):
        if request.method == "GET":
            return (render_template("add_venu.html"))
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
        heads = ["No.", "Show Name", "Rating", "Tags", "Poster", "Action"]
        box_contents = ["show_id" , "show_name" , "show_rating" , "show_tag1"]
        additional1 = ["show_image_path"]
        url1 = "edit_show" 
        url2 = "delete_show"
        ids = ["show_id"]
        button_url ="add_show"
        buttons = ["Add Show"]
        return render_template('admin.html', heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents, additional1 = additional1, button_url = button_url, buttons = buttons, url1 = url1, url2 = url2, ids = ids)
    else:
        return ("You are not allowed to access admin page")


@app.route('/add_show',methods=["GET","POST"])
def add_show():
    if ('email' in session):
        if request.method == "GET":
            return (render_template("add_show.html"))
        if request.method == "POST":
            show_name = request.form['show_name']
            show_tag1 = request.form['show_tag1']
            show_tag2 = request.form['show_tag2']
            show_tag3 = request.form['show_tag3']
            f=request.files['file']
            f.save('static/image/poster'+f.filename)
            show_image_path = str('static/image/poster'+f.filename)
            record=Show(show_name ,show_tag1, show_tag2, show_tag3, show_image_path )
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
            content.show_tag1 = request.form['show_tag1']
            content.show_tag2 = request.form['show_tag2']
            content.show_tag3 = request.form['show_tag3']
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
        heading = "All Show"
        main_contents = show_venus
        heads = ["Show _ Venu Id", "Show Name", "Venu Name", "Price Of Ticket", "Show Timing", "Show Added Timing"]
        box_contents = ["show_venu_id" , "show_name" , "venu_name" , "show_price", "show_timing", "show_added_timing"]
        return render_template('admin.html', heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents)
    else:
        return ("You are not allowed to access admin page")

@app.route("/book_show_venu",methods=["GET","POST"])
def book_show_venu():
    if ('email' in session):
        if request.method == "GET":
            venu=Venu.query.all()
            show=Show.query.all()
            return render_template("book_show_venu.html", venus = venu, shows=show)
        if request.method == "POST":
            venu=request.form['venu_name']
            show=request.form['show_name']
            price=request.form['price']
            show_time=request.form['showtime']
            show_time = datetime.strptime(show_time,"%Y-%m-%dT%H:%M")
            show_added_timming = datetime.now()
            venu_full = Venu.query.filter_by(venu_name=venu).first()
            show_full = Show.query.filter_by(show_name=show).first()
            record = Show_venu(show = show_full,venu = venu_full, show_price = price ,show_timming = show_time, show_added_timming= show_added_timming)
            db.session.add(record)
            db.session.commit()
            return redirect('/show_venu_admin')
    else:
        return ("You are not allowed to access admin page")
    
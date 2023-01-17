from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete
from datetime import datetime

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__,template_folder="Templates")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabom.sqlite3" 
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
app.secret_key="123456789"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Show_venu(db.Model):
    __tablename__ = 'show_venu'
    show_venu_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    venu_id = db.Column(db.Integer, db.ForeignKey("venu.venu_id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.show_id"))
    show_price = db.Column(db.Float, nullable = False)
    show_timing = db.Column(db.DateTime)
    show_added_timing = db.Column(db.DateTime)

    show = db.relationship('Show', back_populates="venus")
    venu = db.relationship('Venu', back_populates="shows")

    def __init__(self, show_price, show ,venu, show_timing, show_added_timing): #show_timming, show_added_timming):
        self.show_price = show_price
        self.show = show
        self.venu= venu
        self.show_timing = show_timing
        self.show_added_timing = show_added_timing

class Show(db.Model):
    __tablename__ ='show'
    show_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    show_name = db.Column(db.String(25), nullable= False)
    show_rating = db.Column(db.Float, nullable=True)
    show_tag1 = db.Column(db.String(10), nullable=False)
    show_tag2 = db.Column(db.String(10), nullable = True)
    show_tag3 = db.Column(db.String(10), nullable = True)
    show_discription = db.Column(db.String(1000))
    show_image_path = db.Column(db.String, nullable= False)

    venus = db.relationship('Show_venu', back_populates='show')

    def __repr__(self):
         return f'<Show "{self.name}">'
    
    def __init__(self,show_name,show_tag1,show_tag2,show_tag3,show_discription,show_image_path):
        self.show_name= show_name
        # self.show_rating= show_rating
        self.show_tag1= show_tag1
        self.show_tag2= show_tag2
        self.show_tag3= show_tag3
        self.show_image_path = show_image_path
        self.show_discription = show_discription

class Venu(db.Model):
    __tablename__ = 'venu'
    venu_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    venu_name = db.Column(db.String, nullable= False)
    capacity = db.Column(db.Integer, nullable=False)
    place = db.Column(db.String(75), nullable = False)
    location = db.Column(db.String(75), nullable = False)
    
    shows = db.relationship('Show_venu' , back_populates="venu")

    def __repr__(self):
         return f'<Venu "{self.name}">'
    
    def __init__(self,venu_name,capacity,place,location):
        self.venu_name= venu_name
        self.capacity = capacity
        self.location = location
        self.place = place





class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(20), unique=True ,nullable = False)
    password = db.Column(db.String(80), nullable = False)



class Ticket_booked(db.Model):
    __tablename__ = 'ticket_booked'
    booking_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), primary_key= True,nullable = False)
    show_venu_id = db.Column(db.Integer, db.ForeignKey("show_venu.show_venu_id"), primary_key= True, nullable= False)
    number_of_ticket_booked = db.Column(db.Integer, nullable = False)
    cost_of_booked_tickets = db.Column(db.Float, nullable = False)


@login_manager.user_loader
def load_user(user):
    return User.get(user)
 
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if (email == "admin_user@gmail.com" and password=="1234"):
            session['email'] = email
            return redirect('/admin')
        if user:
            if Bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            
@app.route("/", methods=["GET","POST"])
@login_required
def user_interface():
    if request.method== "GET":
        return render_template("home.html")
            
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
        heads = ["No.", "Show Name", "Rating", "Tags", "Discription", "Poster", "Action"]
        box_contents = ["show_id" , "show_name" , "show_rating" , "show_tag1", "show_discription"]
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
            form_conditions=[{"type":"text" ,"name":"show_name", "placeholder":"show" ,"required":"True"}, {"type":"text", "name":"show_tag1", "placeholder":"tag (required)"," required":"True"}, {"type":"text", "name":"show_tag2", "placeholder":"tag (not required)", "required":"False"} ,{"type":"text", "name":"show_tag3", "placeholder":"tag (not required)" , "required":"False"}, {"type":"text" ,"name":"show_discription", "placeholder":"About Show", "required":"False"},{"type":"file" ,"name":"file" ,"placeholder":"upload poster",  "required":"True"}]
            return (render_template("admin.html", take_input="True",special_form="False", display_table = "False", heading=heading, form_conditions=form_conditions))
        if request.method == "POST":
            show_name = request.form['show_name']
            show_tag1 = request.form['show_tag1']
            show_tag2 = request.form['show_tag2']
            show_tag3 = request.form['show_tag3']
            show_discription = request.form['show_discription']
            f=request.files['file']
            f.save('static/image/poster'+f.filename)
            show_image_path = str('static/image/poster'+f.filename)
            record=Show(show_name ,show_tag1, show_tag2, show_tag3, show_discription, show_image_path )
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
        button = "Book Show Venu"
        button_url = "book_show_venu"
        return render_template('admin.html' ,display_table = "True", take_input = "False", edit_delete = "False" ,input_button="True", heading=heading, main_contents = main_contents, heads = heads, box_contents = box_contents, button_name = button, button_url = button_url)
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
    

if __name__ == '__main__':
    app.debug=True
    app.run()
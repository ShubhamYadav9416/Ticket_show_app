from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete

app = Flask(__name__,template_folder="Templates")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabom.sqlite3" 
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()
app.secret_key="123456789"

class Show_venu(db.Model):
    __tablename__ = 'show_venu'
    show_venu_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    venu_id = db.Column(db.Integer, db.ForeignKey("venu.venu_id"))
    show_id = db.Column(db.Integer, db.ForeignKey("show.show_id"))
    show_price = db.Column(db.Float, nullable = False)

    show = db.relationship('Show', back_populates="venus")
    venu = db.relationship('Venu', back_populates="shows")

    def __init__(self, show_price, show_id, venu_id):
        self.show_price = show_price
        self.show_id =  show_id
        self.venu_id = venu_id

class Show(db.Model):
    __tablename__ ='show'
    show_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    show_name = db.Column(db.String(25), nullable= False)
    show_rating = db.Column(db.Float, nullable=True)
    show_tag1 = db.Column(db.String(10), nullable=False)
    show_tag2 = db.Column(db.String(10), nullable = True)
    show_tag3 = db.Column(db.String(10), nullable = True)
    show_image_path = db.Column(db.String, nullable= False)

    venus = db.relationship('Show_venu', back_populates='show')

    def __repr__(self):
         return f'<Show "{self.name}">'
    
    def __init__(self,show_name,show_tag1,show_tag2,show_tag3,show_image_path):
        self.show_name= show_name
        # self.show_rating= show_rating
        self.show_tag1= show_tag1
        self.show_tag2= show_tag2
        self.show_tag3= show_tag3
        self.show_image_path = show_image_path

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
    
    def __init__(self,venu_name,capacity,location,place):
        self.venu_name= venu_name
        self.capacity = capacity
        self.location = location
        self.place = place





class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True ,nullable = False)
    password = db.Column(db.String, nullable = False)


class Ticket_booked(db.Model):
    __tablename__ = 'ticket_booked'
    booking_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), primary_key= True,nullable = False)
    show_venu_id = db.Column(db.Integer, db.ForeignKey("show_venu.show_venu_id"), primary_key= True, nullable= False)
    number_of_ticket_booked = db.Column(db.Integer, nullable = False)
    cost_of_booked_tickets = db.Column(db.Float, nullable = False)


 
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
            return render_template('admin_display_venu.html', venus=venus)
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
        return render_template('admin_display_show.html', shows=shows)
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
        show_venus = Show_venu.query.join(Show,  Venu).filter(Show_venu.show_id == Show.show_id).filter(Show_venu.venu_id == Venu.venu_id).add_columns(Show_venu.show_venu_id,Venu.venu_name, Show.show_name, Show_venu.show_price ).all()
        return render_template('admin_display_show_venu.html',show_venus=show_venus)
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
            venu_full = Venu.query.filter_by(venu_name=venu).first()
            show_full = Show.query.filter_by(show_name=show).first()
            record = Show_venu(show=show_full,venu=venu_full, show_price = price)
            db.session.add(record)
            db.session.commit()
            return redirect('/show_venu_admin')
    else:
        return ("You are not allowed to access admin page")
    

if __name__ == '__main__':
    app.debug=True
    app.run()
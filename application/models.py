from .database import db
from flask_login import UserMixin

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
    no_of_rating = db.Column(db.Integer)
    show_tag = db.Column(db.String(10), nullable=False)
    show_lang = db.Column(db.String(10),nullable = False)
    show_duration = db.Column(db.String(10),nullable=False)
    show_discription = db.Column(db.String(1000))
    show_image_path = db.Column(db.String, nullable= False)

    venus = db.relationship('Show_venu', back_populates='show')


    
    def __init__(self,show_name,show_tag,show_discription,show_lang,show_duration,show_image_path):
        self.show_name= show_name
        # self.show_rating= show_rating
        self.show_tag = show_tag
        self.show_discription = show_discription
        self.show_lang = show_lang
        self.show_duration = show_duration
        self.show_image_path = show_image_path

class Venu(db.Model):
    __tablename__ = 'venu'
    venu_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    venu_name = db.Column(db.String, nullable= False)
    capacity = db.Column(db.Integer, nullable=False)
    place = db.Column(db.String(75), nullable = False)
    location = db.Column(db.String(75), nullable = False)
    
    shows = db.relationship('Show_venu' , back_populates="venu")

    
    def __init__(self,venu_name,capacity,place,location):
        self.venu_name= venu_name
        self.capacity = capacity
        self.location = location
        self.place = place





class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(20), unique=True ,nullable = False)
    password = db.Column(db.String(80), nullable = False)

    def __init__(self,email,password):
        self.email=email
        self.password = password
    
    def  get_id(self):
        return (self.id)


class Ticket_booked(db.Model):
    __tablename__ = 'ticket_booked'
    booking_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key= True,nullable = False)
    show_venu_id = db.Column(db.Integer, db.ForeignKey("show_venu.show_venu_id"), primary_key= True, nullable= False)
    number_of_ticket_booked = db.Column(db.Integer, nullable = False)
    cost_of_booked_tickets = db.Column(db.Float, nullable = False)
    time_of_ticket_booked = db.Column(db.DateTime)


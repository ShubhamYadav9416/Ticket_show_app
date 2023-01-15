from .database import db

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

db.create_all()
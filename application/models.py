from .database import db

class Venu(db.Model):
    __tablename__ = 'venu'
    venu_id = db.Column(db.Integer, autoincrement = True, primary_key=True)
    venu_name = db.Column(db.String, nullable= False)
    location = db.Column(db.Strin(15), nullable = False)
    address = db.Column(db.String(75), nullable = False)

class Show(db.Model):
    __tablename__ ='show'
    show_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    show_name = db.Column(db.String(25), nullable= False)
    show_rating = db.Column(db.Float, nullable=True)
    show_tag1 = db.Column(db.String(10), nullable=False)
    show_tag2 = db.Column(db.String(10), nullable = True)
    show_tag3 = db.Column(db.string(10), nullable = True)



class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String, unique=True ,nullable = False)
    password = db.Column(db.String, nullable = False)

class Show_venu(db.Model):
    __tablename__ = 'show_venu'
    show_venu_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    venu_id = db.Column(db.Integer, db.ForeignKey("venu.venu_id"), primary_key = True, nullable = False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.show_id"), primary_key = True, nullable = False)
    show_price = db.Column(db.Float, nullable = False)

class Ticket_booked(db.Model):
    __tablename__ = 'ticket_booked'
    booking_id = db.Column(db.Integer, autoincrement= True, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), primary_key= True,nullable = False)
    show_venu_id = db.Column(db.Integer, db.ForeignKey("show_venu.show_venu_id"), primary_key= True, nullable= False)
    number_of_ticket_booked = db.Column(db.Integer, nullable = False)
    cost_of_booked_tickets = db.Column(db.Float, nullable = False)

    
# class Article(db.Model):
#     __tablename__ = 'article'
#     article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String)
#     content = db.Column(db.String)
#     authors = db.relationship("User", secondary="article_authors")

# class ArticleAuthors(db.Model):
#     __tablename__ = 'article_authors'
#     user_id = db.Column(db.Integer,   db.ForeignKey("user.user_id"), primary_key=True, nullable=False)
#     article_id = db.Column(db.Integer,  db.ForeignKey("article.article_id"), primary_key=True, nullable=False) 

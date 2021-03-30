from Files import db
from flask_login import UserMixin

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100))
    user=db.relationship('News', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username



class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_image=db.Column(db.String(500))
    news_title=db.Column(db.String(500))
    news_text=db.Column(db.String(1000))
    news_topic=db.Column(db.String(100))
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20),unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    bookings = db.relationship('Booking', backref='room')


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    bookings = db.relationship('Booking', backref='guest')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    check_in = db.Column(db.String(20))
    check_out = db.Column(db.String(20))

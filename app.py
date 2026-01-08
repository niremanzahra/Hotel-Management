from flask import Flask, render_template, request, redirect, url_for
from models import db, Room, Guest, Booking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)



# ---------- ROOMS ----------
@app.route('/')
def rooms():
    rooms = Room.query.all()                # READ
    return render_template('rooms.html', rooms=rooms)


@app.route('/add-room', methods=['GET', 'POST'])
def add_room():

    if request.method == 'POST':

        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price = request.form['price']

        # 🔴 CHECK: room already exists?
        existing_room = Room.query.filter_by(room_number=room_number).first()

        if existing_room:
            return "Room already exists!"

        room = Room(
            room_number=room_number,
            room_type=room_type,
            price=price
        )

        db.session.add(room)
        db.session.commit()
        return redirect(url_for('rooms'))

    return render_template('add_room.html')


# ---------- GUESTS ----------
@app.route('/guests')
def guests():
    guests = Guest.query.all()              # READ
    return render_template('guests.html', guests=guests)


@app.route('/add-guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        guest = Guest(
            name=request.form['name'],
            email=request.form['email']
        )
        db.session.add(guest)               # CREATE
        db.session.commit()
        return redirect('/guests')
    return render_template('add_guest.html')


# ---------- BOOKINGS ----------
@app.route('/bookings')
def bookings():
    search = request.args.get('search')

    if search:
        bookings = Booking.query.join(Guest)\
            .filter(Guest.name.ilike(f"%{search}%"))\
            .all()
    else:
        bookings = Booking.query.all()

    return render_template('bookings.html', bookings=bookings)

@app.route('/add-booking', methods=['GET', 'POST'])
def add_booking():

    booking_id = request.args.get('id')
    booking = None

    if booking_id:
        booking = Booking.query.get(booking_id)

    guests = Guest.query.all()
    rooms = Room.query.all()

    if request.method == 'POST':

        guest_id = request.form['guest_id']
        room_id = request.form['room_id']
        check_in = request.form['check_in']
        check_out = request.form['check_out']

        # 🔴 BASIC DATE CHECK
        if check_out <= check_in:
            return "Check-out must be after check-in"

        # 🔴 OVERLAP CHECK (IMPORTANT PART)
        conflict = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.check_in < check_out,
            Booking.check_out > check_in
        )

        # ✏️ EDIT case: apni hi booking ko ignore karo
        if booking:
            conflict = conflict.filter(Booking.id != booking.id)

        conflict = conflict.first()

        if conflict:
            return "Room already booked for selected dates"

        # 💾 SAVE DATA
        if booking:
            # UPDATE
            booking.guest_id = guest_id
            booking.room_id = room_id
            booking.check_in = check_in
            booking.check_out = check_out
        else:
            # ADD
            booking = Booking(
                guest_id=guest_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out
            )
            db.session.add(booking)

        db.session.commit()
        return redirect('/bookings')

    return render_template(
        'add_booking.html',
        booking=booking,
        guests=guests,
        rooms=rooms
    )

@app.route('/delete-booking/<int:id>')
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect('/bookings')




if __name__ == '__main__':
    
 with app.app_context():
    db.create_all()
    app.run(debug=True)

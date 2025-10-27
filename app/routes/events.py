from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Event, User
from datetime import datetime
from flask_mail import Message
from app import mail
from icalendar import Calendar, Event as ICalEvent
from flask import Response
from pytz import UTC
import os
from werkzeug.utils import secure_filename
import uuid


events_bp = Blueprint('events', __name__)


@events_bp.route("/events")
@login_required
def list_events():
    sport = request.args.get('sport')
    date = request.args.get('date')
    now = datetime.now()

    events_to_update = Event.query.filter(Event.datetime < now, Event.status == 'planned', Event.deleted == False).all()
    for event in events_to_update:
        event.status = 'completed'
    if events_to_update:
        db.session.commit()

    events = Event.query.filter_by(deleted=False)
    sport_types = [row[0] for row in db.session.query(Event.sport_type).filter_by(deleted=False).distinct()]

    if sport:
        events = events.filter(Event.sport_type.ilike(f"%{sport}%"))
    if date:
        events = events.filter(db.func.date(Event.datetime) == date)

    events = events.order_by(Event.datetime.asc()).all()

      # Mark if the current user is signed up
    for event in events:
        event.user_signed_up = current_user in event.participants
        event.is_full = len(event.participants) >= event.max_participants

    return render_template("events.html", events=events, sport_types=sport_types)

@events_bp.route('/events/<int:event_id>/status', methods=['POST'])
@login_required
def update_status(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user != event.creator and current_user.role != 'admin':
        flash("Only the creator or an admin can update the status.", "danger")
        return redirect(url_for('events.event_detail', event_id=event_id))

    new_status = request.form.get('status')
    if new_status in ['planned', 'completed', 'cancelled']:
        event.status = new_status
        db.session.commit()
        flash("Event status updated.", "success")

        #Email Notification
        if new_status == 'cancelled' and current_app.config.get("MAIL_ENABLED", False):
            for user in event.participants:
                msg = Message(
                    subject=f"Event Cancelled: {event.title}",
                    recipients=[user.email]
                )
                msg.body = (
                    f"Hi {user.name},\n\n"
                    f"We regret to inform you that the event '{event.title}' has been cancelled.\n\n"
                    f"Redlight Team"
                )
                mail.send(msg)
    else:
        flash("Invalid status.", "danger")

    return redirect(url_for('events.event_detail', event_id=event_id))



@events_bp.route('/events/create', methods=['POST', 'GET'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        sport_type = request.form['sport_type']
        max_participants = int(request.form['max_participants'])
        datetime_str = request.form['datetime']

        try:
            event_time = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid date/time format")
            return redirect(url_for('events.create_event'))

        photos = request.files.getlist('photos')
        saved_filenames = []

        upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        for photo in photos:
            if photo and '.' in photo.filename:
                ext = photo.filename.rsplit('.', 1)[1].lower()
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    original_filename = secure_filename(photo.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
                    save_path = os.path.join(upload_folder, unique_filename)
                    photo.save(save_path)
                    if not os.path.exists(save_path):
                        print(f"❌ Save failed for: {save_path}")
                    else:
                        print(f"✅ Saved to: {save_path}")
                    saved_filenames.append(unique_filename)

        event = Event(
            title=title,
            description=description,
            location=location,
            sport_type=sport_type,
            max_participants=max_participants,
            datetime=event_time,
            creator=current_user,
            photos=",".join(saved_filenames)
        )

        print(saved_filenames)
        print(event.photos)

        db.session.add(event)
        print("Final filenames to be saved in DB:")
        for filename in saved_filenames:
            print(" →", filename)
        print("Upload folder is:", upload_folder)
        db.session.commit()
        current_app.logger.info(f"Event created: {event.title} by {current_user.email}")
        flash("Event created.")
        return redirect(url_for('events.list_events'))

    return render_template('create_event.html')


@events_bp.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    if event.deleted:
        abort(404)
    
    #Only showing selectable users if user is admin or the creator of the event
    selectable_users = []
    if current_user == event.creator or current_user.role == 'admin':
        selectable_users = User.query.all()
    
    return render_template('event_detail.html', event=event, selectable_users = selectable_users)


@events_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.deleted:
        abort(404)

    if current_user != event.creator and current_user.role != 'admin':
        flash("You don't have permission to edit this event.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    if request.method == 'POST':
        old_location = event.location
        old_datetime = event.datetime

        event.title = request.form['title']
        event.description = request.form['description']
        event.location = request.form['location']
        event.sport_type = request.form['sport_type']
        event.max_participants = int(request.form['max_participants'])

        try:
            event.datetime = datetime.strptime(request.form['datetime'], "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid date/time format.")
            return redirect(url_for('events.edit_event', event_id=event.id))
        
        photos = request.files.getlist('photos')
        new_filenames = []

        upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
        os.makedirs(upload_folder, exist_ok=True)

        for photo in photos:
            if photo and '.' in photo.filename:
                ext = photo.filename.rsplit('.', 1)[1].lower()
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    filename = secure_filename(photo.filename)
                    save_path = os.path.join(upload_folder, filename)
                    photo.save(save_path)
                    new_filenames.append(filename)

        if new_filenames:
            existing_photos = event.photos.split(',') if event.photos else []
            event.photos = ",".join(existing_photos + new_filenames)

        db.session.commit()
        flash("Event updated.")

        if current_app.config.get("MAIL_ENABLED", False):
            if old_location != event.location or old_datetime != event.datetime:
                for user in event.participants:
                    msg = Message(
                        subject=f"Update: {event.title}",
                        recipients=[user.email]
                    )
                    msg.body = (
                        f"Hi {user.name},\n\n"
                        f"The event '{event.title}' has been updated.\n\n"
                        f"New Date & Time: {event.datetime}\n"
                        f"New Location: {event.location}\n\n"
                        f"Redlight Team"
                    )
                    mail.send(msg)

        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('edit_event.html', event=event)

@events_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.deleted:
        abort(404)
    # Only the creator or admin can delete
    if current_user != event.creator and current_user.role != 'admin':
        flash("You don't have permission to delete this event.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    event.deleted = True
    db.session.commit()
    flash("Event deleted.")
    return redirect(url_for('events.list_events'))

@events_bp.route('/events/<int:event_id>/register', methods=['POST'])
@login_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.deleted:
        abort(404)

    # Prevent duplicates
    if current_user in event.participants:
        flash("You're already registered for this event.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    # Prevent overbooking
    if len(event.participants) >= event.max_participants:
        flash("This event is full.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    event.participants.append(current_user)
    db.session.commit()

    #Email Notification
    if current_app.config.get("MAIL_ENABLED", False):
        msg = Message(
            subject="Event Registration Confirmation",
            recipients=[current_user.email]
        )
        msg.body = f"Hi {current_user.name},\n\nYou have successfully registered for the event: {event.title}.\n\nDate & Time: {event.datetime}\nLocation: {event.location}\n\nRedlight Team"
        mail.send(msg)

    flash("You have registered for the event.")
    return redirect(url_for('events.event_detail', event_id=event.id))


@events_bp.route('/events/<int:event_id>/add_participant', methods=['POST'])
@login_required
def add_participant(event_id):
    event = Event.query.get_or_404(event_id)
    if event.deleted:
        abort(404)

    if current_user != event.creator and current_user.role != 'admin':
        flash("You can't add participants to this event.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    user_id = request.form['user_id']
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    if user in event.participants:
        flash("User already registered.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    if len(event.participants) >= event.max_participants:
        flash("Event is full.")
        return redirect(url_for('events.event_detail', event_id=event.id))

    event.participants.append(user)
    db.session.commit()

    #Email notification
    if current_app.config.get("MAIL_ENABLED", False):
        msg = Message(
            subject="You've been added to an event",
            recipients=[user.email]
        )
        msg.body = f"Hi {user.name},\n\nYou've been added to the event: {event.title}.\n\nDate & Time: {event.datetime}\nLocation: {event.location}\n\nRedlight Team"
        mail.send(msg)

    flash(f"{user.name} has been added.")
    return redirect(url_for('events.event_detail', event_id=event.id))

@events_bp.route('/events/<int:event_id>/export')
@login_required
def export_event(event_id):
    event = Event.query.get_or_404(event_id)

    cal = Calendar()
    ical_event = ICalEvent()
    ical_event.add('summary', event.title)
    ical_event.add('dtstart', event.datetime.replace(tzinfo=UTC))
    ical_event.add('dtend', event.datetime.replace(tzinfo=UTC))
    ical_event.add('location', event.location)
    ical_event.add('description', event.description)
    cal.add_component(ical_event)

    return Response(
        cal.to_ical(),
        mimetype='text/calendar',
        headers={'Content-Disposition': f'attachment; filename=event_{event.id}.ics'}
    )
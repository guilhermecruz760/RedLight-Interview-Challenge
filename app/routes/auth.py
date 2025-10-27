from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db, login_manager, mail
from app.models import User
from flask_mail import Message
from app.models import Event
import urllib.parse
import os
from werkzeug.utils import secure_filename
import time


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Load carousel images dynamically
    carousel_path = os.path.join(current_app.static_folder, current_app.config['CAROUSSEL'])
    images = sorted([
        f'website/caroussel/{img}'
        for img in os.listdir(carousel_path)
        if img.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ])

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('auth.register'))

        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                upload_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_path, exist_ok=True)
                photo.save(os.path.join(upload_path, filename))
                photo_filename = filename

        code = generate_password_hash(password)
        user = User(name=name, email=email, password=code, photo=photo_filename)
        db.session.add(user)
        db.session.commit()

        # Email notification
        if current_app.config.get("MAIL_ENABLED", False):
            msg = Message("Welcome to Redlight!", recipients=[email])
            msg.body = f"Hi {name},\n\nYour account was successfully created. You can now log in and join events!\n\nRedlight Team"
            mail.send(msg)

        flash("Account created. Please Login")
        return redirect(url_for('auth.login'))

    return render_template('register.html', images=images)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Load carousel images dynamically
    carousel_path = os.path.join(current_app.static_folder, current_app.config['CAROUSSEL'])
    images = sorted([
        f'website/caroussel/{img}'
        for img in os.listdir(carousel_path)
        if img.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ])
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials.")
            return redirect(url_for('auth.login'))

        login_user(user)
        current_app.logger.info("User logged in sucessfully: %s", current_user.email)
        return redirect(url_for('main.home'))

    return render_template('login.html', images=images)

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info("User logged out: %s", current_user.email)
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.age = request.form.get('age') or None

        role = request.form.get('role')
        if role in ['admin', 'participant']:
            current_user.role = role

        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and allowed_file(photo.filename):
                ext = photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{int(time.time() * 1000)}.{ext}"
                upload_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_path, exist_ok=True)

                # Delete old photo
                if current_user.photo:
                    old_path = os.path.join(upload_path, current_user.photo)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                photo_path = os.path.join(upload_path, filename)
                photo.save(photo_path)
                current_user.photo = filename

                # ✅ Debug prints
                print("Photo uploaded:", photo.filename)
                print("Saved new photo to:", photo_path)
                print("Filename saved in DB:", filename)

        db.session.add(current_user)
        db.session.commit()
        current_app.logger.info("Profile updated successfully for user: %s", current_user.email)
        return redirect(url_for('auth.profile'))

    events = Event.query.filter_by(user_id=current_user.id).all()
    event_titles = [e.title for e in events]
    return render_template('profile.html', user=current_user, events_to_delete=event_titles, time=time)

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = db.session.get(User, current_user.id) 
    # Delete user's events first
    Event.query.filter_by(user_id=user.id).delete()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    current_app.logger.info(f"Profile deleted successfully for user: {user.email}")
    return redirect(url_for('auth.login'))
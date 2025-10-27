# Redlight Sports Events Platform – Project Documentation

This documentation provides an overview of the Redlight Sports Events Platform, a web application built using the Flask framework. The platform enables users to register, create, manage, and participate in sports events. It includes features such as user authentication, event status management, photo uploads, participant tracking, and calendar export functionality.

Each file and module in the project is documented below, including descriptions, file paths, and explanations of any non-trivial components used.


## Project Structure

The Redlight Sports Events Platform is organized into logical folders and modules for scalability and clarity. Below is an overview of the directory structure and its purpose:

    .
    ├── init.py -> Application factory initializer
    ├── models.py -> SQLAlchemy models (User, Event, etc.)
    ├── routes/ -> Flask Blueprints (auth, events, main, participants)
    │   ├── auth.py -> Authentication routes (login, register, logout)
    │   ├── events.py -> Event-related routes and logic
    │   ├── main.py -> Homepage and general routes
    │   └── participants.py -> Participant handling routes
    ├── static/ -> Static assets (CSS, images, uploads)
    │   ├── styles.css -> Main stylesheet
    │   ├── uploads/ -> Uploaded profile pictures and event photos
    │   └── website/ -> Design assets (logos, carousel)
    ├── templates/ -> Jinja2 templates for frontend pages
    │   ├── header.html -> Base header template with nav
    │   ├── home.html -> Landing page
    │   ├── login.html -> Login form
    │   ├── register.html -> Registration form
    │   ├── profile.html -> User profile
    │   ├── events.html -> Event list view
    │   ├── create_event.html -> Create event form
    │   ├── edit_event.html -> Edit event form
    │   └── event_detail.html -> Event details with participant interaction

---

## Application Entry Point – `run.py`

This file serves as the main entry point for launching the Redlight Sports Events Platform. It initializes the Flask application using the factory function defined in the `app` package and starts the development server if run directly.

### File Path
[`run.py`](run.py)

###  Purpose
- Initializes the Flask app instance from the factory method `create_app()`
- Starts the Flask development server when executed directly


---
## models.py

### File Path

[View models.py](./app/models.py)

### Purpose

This file defines the core database schema of the platform. It contains SQLAlchemy models representing users and events, as well as their relationships. The design enables users to register, create, and join events, with role-based access and flexible status handling.

### Association Table: event_participants

This is a many-to-many association table that links users and events. It allows tracking of which users have registered for which events.


` event_participants = db.Table('event_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
) `

### User Model

Represents a platform user. Inherits from UserMixin to integrate with Flask-Login. The model includes fields for user credentials, profile data, and relationships to events.

Fields:
- id: Integer (Primary key)
- name: String(100) – Full name of the user
- email: String(120) – Unique email for login
- password: String(200) – Encrypted password
- role: Enum('participant', 'admin') – Role assigned
- age: Integer – Optional age
- photo: String(120) – Path to uploaded profile picture
- events_created: One-to-many relationship (events the user created)
- events_joined: Many-to-many relationship (events the user joined)

Note: `role` uses a named enum `user_roles` to enforce valid values.

---

## Event Model

Represents a sporting event created by a user. Supports soft deletion, participant tracking, and photo storage.

Fields:
- id: Integer (Primary key)
- title: String(100) – Title of the event
- description: Text – Optional description
- location: String(100) – Event location
- datetime: DateTime – Date and time of the event
- sport_type: String(50) – Type of sport
- max_participants: Integer – Participant limit
- status: Enum('planned', 'completed', 'cancelled') – Event status
- deleted: Boolean – Soft deletion flag
- user_id: Integer – Foreign key to User.id
- photos: Text – Comma-separated image filenames

Note: `status` uses a named enum `event_status` for validation.

### Key Features

- Soft Deletion: Events are not removed but flagged with `deleted = True`.
- Named Enums: Enums enforce valid string values for roles and statuses.
- Dual Relationships: Users can both create and join events.

---
## App Factory (`__init__.py`)

This module initializes the Flask application for the Redlight Sports Events Platform. It configures the core extensions (SQLAlchemy, Flask-Login, and Flask-Mail), registers the blueprints for different routes, and sets up application-level logging.

### File Path
[View \_\_init\_\_.py](./app/\_\_init\_\_.py)



### Overview

The app factory pattern is implemented through the `create_app` function, which ensures modularity and easier testing. Configuration settings are loaded from the `Config` object in `config.py`.

#### Core Extensions
- **SQLAlchemy**: For database ORM (Object-Relational Mapping) (`db`)
- **Flask-Login**: For user session and authentication management (`login_manager`)
- **Flask-Mail**: For sending notification emails (`mail`)

---

### Key Function

#### `create_app()`
Initializes and configures the Flask app.

---
## Event Routes (`events.py`)

This module defines all event-related routes, including creation, editing, deletion, registration, email notifications, and calendar export functionalities. It uses `Blueprint` to modularize the event features in the Redlight platform.

### File Path
[View events.py](./app/routes/events.py)


### Overview

This file:
- Handles event CRUD operations
- Sends email notifications when events are created, cancelled, or updated
- Prevents overbooking
- Allows users to register themselves or be added manually
- Supports filtering and exporting events in iCalendar format (`.ics`)


### Routes

#### `@events_bp.route("/events")`
**List Events**

- Filters events by sport or date (if provided via query parameters)
- Automatically updates past events' status to `completed`
- Renders the `events.html` template with available and filtered events

#### `@events_bp.route("/events/create")`
**Create Event**

- Allows authenticated users to create a new event
- Accepts form data including title, location, type, time, photos
- Saves uploaded images securely with UUID filenames
- Sends success flash messages and logs creation

#### `@events_bp.route("/events/<int:event_id>")`
**Event Details**

- Renders `event_detail.html`
- Allows admin or event creator to see a list of selectable users for management

#### `@events_bp.route("/events/<int:event_id>/edit")`
**Edit Event**

- Allows only the event creator or an admin to edit event details
- Supports photo uploads and merging with existing images
- Sends update emails to participants if location or datetime changes

#### `@events_bp.route("/events/<int:event_id>/delete")`
**Soft Delete Event**

- Marks the event as deleted instead of fully removing it from the DB
- Only the creator or an admin can delete the event

#### `@events_bp.route("/events/<int:event_id>/status", methods=['POST'])`
**Update Event Status**

- Updates the event's status (e.g., from `planned` to `completed` or `cancelled`)
- Notifies all participants by email if cancelled

#### `@events_bp.route("/events/<int:event_id>/register", methods=['POST'])`
**Register for Event**

- Adds the current user to the event's participant list
- Prevents duplicate registrations and overbooking
- Sends a registration confirmation email if enabled

#### `@events_bp.route("/events/<int:event_id>/add_participant", methods=['POST'])`
**Manually Add a Participant**

- Only the event creator or an admin can add participants
- Prevents adding the same user or exceeding the max participant limit
- Sends an email notification to the added participant

#### `@events_bp.route("/events/<int:event_id>/export")`
**Export Event as iCalendar**

- Generates a `.ics` calendar file for the given event
- Adds fields such as title, datetime, description, and location
- Returns a downloadable response



### Email Notifications

- Emails are sent when:
  - An event is **cancelled**
  - A user is **registered or added**
  - An event is **updated** (time or location)
- Controlled by the `MAIL_ENABLED` flag in the config


### File Upload Handling

- Event photos are stored in a configured `UPLOAD_FOLDER`
- Filenames are secured and made unique with UUID
- On edit, new photos are appended to existing ones



### Notes

- Uses `pytz.UTC` to ensure exported calendar events have a timezone
- Makes use of `secure_filename` from Werkzeug to prevent path injection
- Events are "soft deleted" using a `deleted` flag instead of permanent removal

---

## main.py

This file defines the main blueprint of the application and sets up the root route (`'/'`) to render the home page.

**Path:** `app/routes/main.py`

### Overview

The `main.py` module serves as the entry point for authenticated users accessing the root (`/`) route of the web application. It uses Flask's `Blueprint` system to modularize routes, allowing clean separation of concerns.

### Code Breakdown

```python
from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)
```

- `Blueprint`: Used to organize a group of related views and other code.
- `login_required`: Ensures that only authenticated users can access the route.
- `current_user`: Provides access to the current authenticated user object.

```python
@main_bp.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)
```

- This route renders the `home.html` template and passes the current user object to it for dynamic content rendering.

### Notes

- The `home()` view is protected by `@login_required`, meaning unauthenticated users will be redirected to the login page.
- `user=current_user` allows the Jinja template to display personalized content, like `{{ user.name }}`.

---

## Authentication Routes (`auth.py`)

This module handles user authentication and profile management in the Redlight platform. It provides routes for login, registration, logout, profile editing, and account deletion. It also supports user photo uploads and email notifications upon registration.

### File Path
[View auth.py](./app/routes/auth.py)


### Overview

The `auth.py` module:
- Defines the user authentication system
- Sends welcome emails if enabled
- Loads dynamic images for login/register carousel
- Allows role switching between `admin` and `participant`
- Supports secure photo uploads for user profiles


### Routes

#### `@auth_bp.route('/register', methods=['GET', 'POST'])`
**User Registration**

- Accepts `name`, `email`, `password`, and optional `photo`
- Secures uploaded photos and saves them
- Sends a welcome email if `MAIL_ENABLED` is `True`
- Renders `register.html` with carousel images

#### `@auth_bp.route('/login', methods=['GET', 'POST'])`
**User Login**

- Accepts `email` and `password`
- Verifies credentials using hashed passwords
- Logs the user in and redirects to the home page
- Renders `login.html` with carousel images

#### `@auth_bp.route('/logout')`
**User Logout**

- Logs the current user out
- Redirects back to the login page
- Logs the logout activity

#### `@auth_bp.route('/profile', methods=['GET', 'POST'])`
**Edit Profile**

- Lets authenticated users update their `name`, `age`, `role`, and `photo`
- Uploaded photo is stored securely and the previous one is removed if present
- Fetches user's events to optionally display/delete them
- Renders `profile.html` with the current user and their events

#### `@auth_bp.route('/delete_account', methods=['POST'])`
**Delete Account**

- Deletes the current user and all their associated events
- Automatically logs the user out
- Logs the deletion action


### Helper Function

#### `allowed_file(filename)`
Checks whether the uploaded file has an allowed extension defined in the config.


### Carousel Image Loading

- Carousel images are dynamically loaded from the folder defined in the config (`CAROUSSEL`)
- Applies to both login and registration templates


### Email Notifications

- Welcome email is sent after account creation
- Email functionality is controlled via `MAIL_ENABLED` configuration


### Security and Upload Handling

- All uploaded photos are saved using `secure_filename` and timestamp-based names
- Uploads are only allowed for extensions specified in `ALLOWED_EXTENSIONS`
- Old profile photos are deleted when updated to prevent storage clutter


---
## HTML Templates and CSS Styling

The frontend of the Redlight Sports Events Platform is built using HTML templates rendered with Jinja2 (Flask's templating engine), and styled primarily with a custom CSS file along with Bootstrap 5 for responsive layout and components.

### Templates Overview

Each HTML template is tailored to a specific route or functionality, such as user authentication, event management, or displaying user profiles. The templates extend a base layout defined in `header.html`, ensuring consistent header content and user session management across all pages. Reusable design classes and consistent structural patterns are maintained using Bootstrap's grid system and utility classes.

Jinja2 syntax is used throughout to inject dynamic content, conditionally render elements (e.g., based on user roles or authentication status), and manage control flow within templates.

The templates work in conjunction with Flask routes, passing context variables (such as `user`, `event`, or `selectable_users`) to render the appropriate view with user-specific content.

### Styling with CSS

Custom styling is managed via a single `styles.css` file, located under the `static/` directory. This file defines consistent visual theming, custom button designs, layout adjustments, animation effects, and responsive behavior. The file is organized to support authentication pages, home/dashboard layout, profile picture uploads, event carousels, and various interactive elements like dropdowns and hover effects.

Noteworthy features:
- Header remains fixed and transparent for clean UX.
- Buttons are styled with `.redlight-btn` class, including hover states.
- Use of animations for page transitions and button entrances.
- Carousel integration with Swiper.js for event image display.

### File Paths

**HTML Templates:**
- [View create_event.html](./app/templates/create_event.html)
- [View edit_event.html](./app/templates/edit_event.html)
- [View event_detail.html](./app/templates/event_detail.html)
- [View events.html](./app/templates/events.html)
- [View header.html](./app/templates/header.html)
- [View home.html](./app/templates/home.html)
- [View login.html](./app/templates/login.html)
- [View profile.html](./app/templates/profile.html)
- [View register.html](./app/templates/register.html)

**CSS:**
- [View styles.css](./app/static/styles.css)
---

This file is being updated as soon as any other modification is made.

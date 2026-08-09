# Trekking Management Application

**Student Name: Aarusha Vivek Patil**  
**Roll Number: 25f2006483**  
**Course: Modern Application Development I - Project** 

A role-based web application for managing trekking activities, built as part of the MAD-1 project at IIT Madras.

The application allows three types of users — Admin, Trek Staff, and Trekkers — to interact with the system through separate role-based dashboards. The admin manages the entire platform, staff manages assigned treks, and trekkers browse and book treks.

## Tech Stack

 - Backend - Flask 
 - Templating - Jinja2 
 - Database - SQLite via SQLAlchemy 
 - Frontend - HTML, Bootstrap 5 
 - Styling - CSS, Google Fonts 
 - Form Handling - Flask-WTF, WTForms 
 - Password Security - Werkzeug 


## Roles & Features

### Admin
- Dashboard with counts of treks, users, staff, and bookings
- Create, edit, and delete treks
- Approve or blacklist trek staff
- Assign staff to treks
- Blacklist or activate users
- View all bookings
- Search treks, staff, and users

### Trek Staff
- Self-register and login (requires admin approval)
- View assigned treks and participant count
- Update trek slots and status
- View and manage participant list
- Mark trek as started or completed

### User (Trekker)
- Self-register and login
- Browse available treks with search and filters
- Book treks
- View booking status and history
- Edit profile


## Core Business Rules

- Only open treks can be booked
- Overbooking is prevented
- Duplicate bookings are not allowed
- Only assigned staff can manage a trek
- Staff must be approved by admin before accessing dashboard
- Admin is pre-created and cannot be registered


## Default Admin Login

Username: admin
Password: admin123


## Project Structure

```

trekking-management-app/
│
├── app.py              # Main Flask app, all routes
├── database.py         # SQLAlchemy models
├── forms.py            # Flask-WTF form definitions
├── requirements.txt    # Python dependencies
│
├── templates/
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   │
│   ├── admin/
│   │   ├── dashboard.html      # Admin dashboard with stats
│   │   ├── treks.html          # Manage all treks
│   │   ├── add_trek.html       # Add / edit trek form
│   │   ├── assign_staff.html   # Assign staff to trek
│   │   ├── staff.html          # Manage staff approvals
│   │   ├── users.html          # Manage users
│   │   ├── bookings.html       # View all bookings
│   │   └── search.html         # Search users, staff, treks
│   │
│   ├── staff/
│   │   ├── dashboard.html      # Staff dashboard with assigned treks
│   │   └── manage_trek.html    # Manage trek slots, status, participants
│   │
│   └── user/
│       ├── dashboard.html      # Browse treks and booked treks
│       ├── trek_detail.html    # Trek details and booking
│       ├── my_bookings.html    # View active bookings
│       ├── history.html        # Trekking history
│       └── profile.html        # Edit profile
│
└── static/
    └── style.css       # Custom stylesheet

```

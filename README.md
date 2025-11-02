# IT Service Request Tracking System

## Overview
A modern, web-based application designed to automate internal IT service request management for enterprises. This system replaces email-based request handling with a structured, trackable process for submitting and managing IT service requests with role-based access control.

## 🌟 Key Features

### For Employees
- **Easy Request Submission**: Intuitive web form for submitting IT service requests
- **Request Tracking**: Real-time status updates and progress tracking
- **User-Friendly Interface**: Modern, responsive design accessible on all devices

### For Administrators
- **Request Management**: Comprehensive dashboard for tracking and updating request status
- **Advanced Analytics**: Visual charts and statistics for request patterns
- **Role-Based Access**: Secure admin authentication system
- **Bulk Operations**: Manage multiple requests efficiently

### System Features
- **External API Integration**: Email notifications via Mailgun API
- **Automation**: Automatic status assignment and timestamp tracking
- **RESTful API**: JSON endpoints for programmatic access and integration
- **Responsive Design**: Mobile-first approach works on all screen sizes

## 🛠 Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
- **Styling**: Modern CSS with Glassmorphism design
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Inter (Google Fonts)
- **Authentication**: Session-based with role management
- **External APIs**: Mailgun (email notifications)
- **Version Control**: Git


# 🧰 IT Service Request Tracking System

A modern, web-based application designed to automate internal IT service request management for enterprises.  
This system replaces email-based request handling with a structured, trackable process for submitting and managing IT service requests — complete with role-based access control and analytics.

---

## 🌟 Key Features

### 👨‍💼 For Employees
- **Easy Request Submission** – Intuitive web form for creating IT service requests  
- **Real-Time Tracking** – View progress and status updates instantly  
- **Responsive UI** – Works seamlessly across all screen sizes

### 🧑‍💻 For Administrators
- **Centralized Dashboard** – Manage, update, and prioritize requests efficiently  
- **Advanced Analytics** – Visual charts for workload and request trends  
- **Role-Based Access** – Secure login and session-based authentication  
- **Bulk Management** – Streamlined request handling for large organizations

### ⚙️ System Features
- **Mailgun Integration** – Automated email notifications for request events  
- **Timestamp Tracking** – Automatic creation and update timestamps  
- **RESTful API** – Provides JSON endpoints for external integrations  
- **Scalable Design** – Works with both SQLite (dev) and PostgreSQL (production)

---

## 🏗 Technology Stack

- **Backend:** Flask (Python) + SQLAlchemy ORM  
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2  
- **Database:** SQLite (dev) / PostgreSQL (prod)  
- **Styling:** Glassmorphism + CSS variables  
- **Icons:** Font Awesome 6.4.0  
- **Fonts:** Inter (Google Fonts)  
- **Auth:** Session-based role management  
- **Email API:** Mailgun  
- **Version Control:** Git  

---

## 🖼️ UI Previews

### 🔐 Admin Login  
![Admin Login](https://drive.google.com/uc?export=view&id=1JahhiZ5LbyhdK-ITvnSsOcWTZeG1eCTp)

### 🏠 Homepage  
![Homepage](https://drive.google.com/uc?export=view&id=1MCIp6LtZo-ZC6IWY0T3y5xoXt1sb0RRm)

### 📊 Dashboard  
![Dashboard](https://drive.google.com/uc?export=view&id=1XHO4UXsgP_U3rAkEWYdRTB3JzTVFpTnX)

### 📝 Requests Page  
![Requests](https://drive.google.com/uc?export=view&id=1UamiQz0bo5IYZcsqOvItx-K_8ZMCHaY0)

---

## 📋 Prerequisites

- Python **3.8+**  
- Git  
- Virtualenv  
- Modern web browser (Chrome / Firefox / Edge)

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/IT-service-tracker.git
cd IT-service-tracker



## 📋 Prerequisites

- **Python 3.8+**
- **Git**
- **Virtualenv** (recommended)
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/IT-service-tracker.git
cd IT-service-tracker

2. SETUP VIRTUAL ENVIRONMENT
# Deactivate current environment
deactivate

# Remove the broken virtual environment
rm -rf venv

# Create a new virtual environment with pip included
python3 -m venv venv --prompt="it-service" --upgrade-deps

# Activate the new virtual environment
source venv/bin/activate

3. INSTALL DEPENDENCIES
pip install -r requirements.txt

4. Configure Environment
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env

Example .env
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=sqlite:///service_requests.db
MAILGUN_DOMAIN=your-mailgun-domain
MAILGUN_API_KEY=your-mailgun-api-key
ADMIN_EMAIL=admin@yourcompany.com

5. initial the database
python app.py

The system will automatically:

    Create all necessary database tables

    Set up a default admin account

    Start the development server

6. Access the Application

    Main Application: http://127.0.0.1:5000

    Admin Login: http://127.0.0.1:5000/admin/login

🔐 Default Admin Credentials

On first run, the system creates a default admin account:

    Username: admin

    Password: admin123

⚠️ Security Note: Change these credentials immediately after first login in production environments.


📁 Project Structure

IT-service-tracker/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── config.py            # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── README.md           # Project documentation
├── service_requests.db  # SQLite database (created automatically)
└── templates/           # Jinja2 templates
    ├── base.html        # Base template with navigation
    ├── index.html       # Homepage
    ├── submit_request.html  # Request submission form
    ├── submission_success.html  # Success confirmation
    ├── view_requests.html      # Admin request management
    ├── dashboard.html          # Admin analytics dashboard
    └── admin_login.html        # Admin authentication


🎯 User Roles & Permissions
👥 Regular Users (Employees)

    ✅ View homepage

    ✅ Submit service requests

    ✅ View submission confirmation

👨💼 Administrators (IT Staff)

    ✅ All regular user permissions

    ✅ View all service requests

    ✅ Update request status

    ✅ Access analytics dashboard

    ✅ Export request data

    ✅ Manage system settings

🧪 Testing
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest


🔧 API Endpoints

Public Endpoints

    GET /api/requests - Retrieve all service requests (JSON)

    GET /api/requests/<id> - Get specific request details

    POST /submit - Submit new service request

Admin Endpoints (Authentication Required)

    PUT /api/requests/<id>/status - Update request status

    GET /dashboard - Access analytics dashboard

    GET /requests - View all requests with filteringPublic Endpoints

    GET /api/requests - Retrieve all service requests (JSON)

    GET /api/requests/<id> - Get specific request details

    POST /submit - Submit new service request

Admin Endpoints (Authentication Required)

    PUT /api/requests/<id>/status - Update request status

    GET /dashboard - Access analytics dashboard

    GET /requests - View all requests with filtering


🎨 Customization
Changing Brand Colors

Edit CSS variables in base.html:

:root {
    --primary: #0052cc;      /* Main brand color */
    --primary-dark: #0747a6; /* Darker shade */
    --accent: #6554c0;       /* Accent color */
    /* ... other variables */
}

Adding New Request Categories

Modify the categories list in app.py:

categories = ['Password Reset', 'Hardware Issue', 'Software Installation', 
              'Network Problem', 'Printer Issue', 'Other', 'Your New Category']


Configuring Email Notifications

Update Mailgun settings in config.py:
MAILGUN_DOMAIN = 'your-domain.com'
MAILGUN_API_KEY = 'your-api-key'
ADMIN_EMAIL = 'it-support@yourcompany.com'

🚀 Production Deployment
Using Gunicorn & Nginx

Install production WSGI server:

pip install gunicorn

Create production configuration:
# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4
threads = 2
timeout = 120

Run with Gunicorn:
gunicorn -c gunicorn_config.py app:app

Set up Nginx reverse proxy (recommended):
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

Manual Testing Checklist

    Submit a new service request

    Verify email notifications (if configured)

    Admin login functionality

    Request status updates

    Dashboard analytics

    Mobile responsiveness

    API endpoints

🔒 Security Considerations

    Change default admin credentials

    Use strong SECRET_KEY in production

    Enable HTTPS in production

    Regularly update dependencies

    Implement rate limiting for API endpoints

    Sanitize user inputs

    Use environment variables for sensitive data

📞 Support
Getting Help

    Check the Issues page

    Review the Wiki for documentation

    Contact: it-support@yourcompany.com

Common Issues

    Database connection errors: Ensure SQLite file is writable

    Template not found: Verify templates directory exists

    Admin login fails: Check if default admin was created

    Email notifications not working: Verify Mailgun credentials

🤝 Contributing

    Fork the repository

    Create a feature branch (git checkout -b feature/AmazingFeature)

    Commit your changes (git commit -m 'Add some AmazingFeature')

    Push to the branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
🚀 Future Enhancements

    User registration and authentication

    Email notifications for request updates

    File attachment support

    Advanced reporting and analytics

    SLA management

    Mobile app

    Integration with popular chat platforms (Slack, Teams)

    Knowledge base integration

    Automated ticket routing

🎯 Quick Start Commands Summary
# Clone and setup
git clone https://github.com/yourusername/IT-service-tracker.git
cd IT-service-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

# Access the application
# Main site: http://127.0.0.1:5000
# Admin login: http://127.0.0.1:5000/admin/login
# Default admin: admin / admin123



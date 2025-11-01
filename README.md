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
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

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





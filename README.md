# IT Service Request Tracking System

## Overview
A web-based application designed to automate internal IT service request management. This system replaces email-based request handling with a structured, trackable process for submitting and managing IT service requests.

## Features
- **Service Request Submission**: Staff can submit IT requests through a web form
- **Request Management**: Admin view for tracking and updating request status
- **External API Integration**: Email notifications via Mailgun API
- **Automation**: Automatic status assignment and timestamp tracking
- **RESTful API**: JSON endpoints for programmatic access
- **Dashboard**: Administrative dashboard with statistics and metrics

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, Jinja2 Templates
- **External APIs**: Mailgun (email notifications)
- **Version Control**: Git

## Installation & Setup

### Prerequisites
- Python 3.8+
- Git
- Virtualenv (recommended)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/IT-service-tracker.git
   cd IT-service-tracker

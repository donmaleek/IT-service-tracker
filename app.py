"""
IT Service Request Tracking System - Main Application Module
A Flask-based web application for managing internal IT service requests.
Provides interfaces for submitting, viewing, and managing service requests.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, ServiceRequest
from config import config
from datetime import datetime
import requests
import os

def create_app(config_name='default'):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_name (str): Configuration environment ('development', 'production', 'default')
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize database with app
    db.init_app(app)
    
    return app

app = create_app()

# Create database tables
with app.app_context():
    db.create_all()

def send_email_notification(requester_name, department, category, request_id):
    """
    Send email notification using Mailgun API when a new request is submitted.
    This function integrates with external email service for notifications.
    
    Args:
        requester_name (str): Name of the person who submitted the request
        department (str): Department of the requester
        category (str): Category of the service request
        request_id (int): Unique identifier of the created request
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    mailgun_domain = app.config['MAILGUN_DOMAIN']
    mailgun_api_key = app.config['MAILGUN_API_KEY']
    admin_email = app.config['ADMIN_EMAIL']
    
    if not mailgun_domain or not mailgun_api_key:
        print("Mailgun configuration missing - skipping email notification")
        return False
    
    # Prepare email data for Mailgun API
    email_data = {
        'from': f'IT Service Desk <it-services@{mailgun_domain}>',
        'to': [admin_email],
        'subject': f'New IT Service Request #{request_id}',
        'text': f"""
        New IT Service Request Submitted:
        
        Request ID: #{request_id}
        Requester: {requester_name}
        Department: {department}
        Category: {category}
        
        Please check the IT Service Request System for details.
        """
    }
    
    try:
        # Send email via Mailgun API
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data=email_data
        )
        
        if response.status_code == 200:
            print(f"Email notification sent successfully for request #{request_id}")
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")
        return False

def get_departments_from_api():
    """
    Fetch department list from external JSON endpoint.
    This demonstrates systems integration with external APIs.
    
    Returns:
        list: List of department names or default list if API fails
    """
    try:
        # Example external API endpoint - replace with actual department API
        response = requests.get('https://api.example.com/departments', timeout=5)
        
        if response.status_code == 200:
            departments_data = response.json()
            return [dept['name'] for dept in departments_data.get('departments', [])]
        else:
            raise Exception(f"API returned status code: {response.status_code}")
            
    except Exception as e:
        print(f"Failed to fetch departments from API: {str(e)}")
        # Return default departments if API fails
        return ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales']

@app.route('/')
def index():
    """
    Render the application homepage with navigation options.
    
    Returns:
        Response: Rendered HTML template for the homepage
    """
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    """
    Handle service request submission.
    GET: Display the request submission form
    POST: Process form data and create new service request
    
    Returns:
        Response: Form template or redirect to success page
    """
    departments = get_departments_from_api()
    categories = ['Password Reset', 'Hardware Issue', 'Software Installation', 
                 'Network Problem', 'Printer Issue', 'Other']
    
    if request.method == 'POST':
        try:
            # Extract form data
            requester_name = request.form.get('requester_name', '').strip()
            department = request.form.get('department', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            
            # Validate required fields
            if not all([requester_name, department, category, description]):
                return render_template('submit_request.html', 
                                    departments=departments, 
                                    categories=categories,
                                    error='All fields are required')
            
            # Create new service request - automation sets default status to "Pending"
            new_request = ServiceRequest(
                requester_name=requester_name,
                department=department,
                category=category,
                description=description
                # Status automatically set to 'Pending' by default
            )
            
            # Save to database
            db.session.add(new_request)
            db.session.commit()
            
            # Send email notification via external API
            send_email_notification(requester_name, department, category, new_request.id)
            
            return redirect(url_for('submission_success', request_id=new_request.id))
            
        except Exception as e:
            db.session.rollback()
            return render_template('submit_request.html', 
                                departments=departments, 
                                categories=categories,
                                error=f'Error submitting request: {str(e)}')
    
    return render_template('submit_request.html', 
                         departments=departments, 
                         categories=categories)

@app.route('/submission-success/<int:request_id>')
def submission_success(request_id):
    """
    Display success page after request submission.
    
    Args:
        request_id (int): ID of the successfully submitted request
    
    Returns:
        Response: Rendered HTML template showing submission success
    """
    return render_template('submission_success.html', request_id=request_id)

@app.route('/requests')
def view_requests():
    """
    Display all service requests for admin/IT staff view.
    Includes filtering and search functionality.
    
    Returns:
        Response: Rendered HTML template with list of requests
    """
    # Get filter parameters from query string
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    department_filter = request.args.get('department', '')
    
    # Build query with filters
    query = ServiceRequest.query
    
    if status_filter:
        query = query.filter(ServiceRequest.status == status_filter)
    if category_filter:
        query = query.filter(ServiceRequest.category == category_filter)
    if department_filter:
        query = query.filter(ServiceRequest.department == department_filter)
    
    # Get all requests ordered by creation date (newest first)
    requests = query.order_by(ServiceRequest.created_at.desc()).all()
    
    # Get unique values for filter dropdowns
    departments = db.session.query(ServiceRequest.department).distinct().all()
    categories = db.session.query(ServiceRequest.category).distinct().all()
    statuses = db.session.query(ServiceRequest.status).distinct().all()
    
    return render_template('view_requests.html', 
                         requests=requests,
                         departments=[dept[0] for dept in departments],
                         categories=[cat[0] for cat in categories],
                         statuses=[status[0] for status in statuses],
                         current_filters={
                             'status': status_filter,
                             'category': category_filter,
                             'department': department_filter
                         })

@app.route('/api/requests', methods=['GET'])
def api_get_requests():
    """
    REST API endpoint to retrieve service requests in JSON format.
    Supports filtering via query parameters.
    
    Returns:
        JSON: List of service requests with full details
    """
    # Build query with filters from request parameters
    query = ServiceRequest.query
    
    if request.args.get('status'):
        query = query.filter(ServiceRequest.status == request.args.get('status'))
    if request.args.get('category'):
        query = query.filter(ServiceRequest.category == request.args.get('category'))
    if request.args.get('department'):
        query = query.filter(ServiceRequest.department == request.args.get('department'))
    
    requests = query.order_by(ServiceRequest.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'count': len(requests),
        'requests': [req.to_dict() for req in requests]
    })

@app.route('/api/requests/<int:request_id>/status', methods=['PUT'])
def api_update_status(request_id):
    """
    REST API endpoint to update the status of a service request.
    Demonstrates automation by automatically setting timestamps.
    
    Args:
        request_id (int): ID of the request to update
    
    Returns:
        JSON: Success status and updated request data
    """
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        # Find request and update status
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.status = new_status
        # updated_at is automatically set by database onupdate
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request #{request_id} status updated to {new_status}',
            'request': service_request.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """
    Display administrative dashboard with request statistics and metrics.
    
    Returns:
        Response: Rendered HTML template with dashboard data
    """
    # Calculate statistics for dashboard
    total_requests = ServiceRequest.query.count()
    pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
    resolved_requests = ServiceRequest.query.filter_by(status='Resolved').count()
    
    # Get requests by category
    category_stats = db.session.query(
        ServiceRequest.category,
        db.func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.category).all()
    
    # Get requests by department
    department_stats = db.session.query(
        ServiceRequest.department,
        db.func.count(ServiceRequest.id)
    ).group_by(ServiceRequest.department).all()
    
    # Get recent requests
    recent_requests = ServiceRequest.query.order_by(
        ServiceRequest.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         total_requests=total_requests,
                         pending_requests=pending_requests,
                         resolved_requests=resolved_requests,
                         category_stats=category_stats,
                         department_stats=department_stats,
                         recent_requests=recent_requests)

@app.route('/update-status/<int:request_id>', methods=['POST'])
def update_status(request_id):
    """
    Update request status from web interface with automation features.
    
    Args:
        request_id (int): ID of the request to update
    
    Returns:
        Response: Redirect back to requests view with success message
    """
    try:
        new_status = request.form.get('status')
        service_request = ServiceRequest.query.get_or_404(request_id)
        
        # Automation: Validate status transition
        valid_statuses = ['Pending', 'In Progress', 'Resolved']
        if new_status not in valid_statuses:
            return redirect(url_for('view_requests', error='Invalid status'))
        
        service_request.status = new_status
        db.session.commit()
        
        return redirect(url_for('view_requests', 
                              success=f'Request #{request_id} status updated to {new_status}'))
        
    except Exception as e:
        db.session.rollback()
        return redirect(url_for('view_requests', error=str(e)))

if __name__ == '__main__':
    """
    Main entry point for running the Flask application.
    """
    app.run(debug=True, host='0.0.0.0', port=5000)

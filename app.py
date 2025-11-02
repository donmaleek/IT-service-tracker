"""
================================================================================
IT SERVICE REQUEST TRACKING SYSTEM WITH ADMIN AUTHENTICATION
System: Demulla IT Service Desk
Author: Engineer Mathias Alfred
Version: 3.1.2
Description: Enterprise-grade IT service request tracking system with secure
             admin authentication, comprehensive request management, and
             real-time analytics.
Features:
  - Secure admin authentication with session management
  - Comprehensive service request tracking
  - Real-time dashboard with analytics
  - RESTful API for external integrations
  - Role-based access control
  - Database security and input validation
  - File attachment support for service requests
================================================================================
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
import os
import hashlib
import secrets
import re
import json
from functools import wraps
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename
from sqlalchemy import text, inspect

# Create Flask application instance
app = Flask(__name__)

# ==============================================================================
# APPLICATION CONFIGURATION
# Secure configuration with environment-based settings
# ==============================================================================
class Config:
    """Application configuration with security best practices"""
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///service_requests.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-this-in-production')
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'log'}
    
    # Application settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

app.config.from_object(Config)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==============================================================================
# DATABASE INITIALIZATION
# SQLAlchemy ORM configuration with connection pooling
# ==============================================================================
db = SQLAlchemy(app)

# ==============================================================================
# DATA MODELS
# SQLAlchemy ORM models with validation and business logic
# ==============================================================================
class ServiceRequest(db.Model):
    """
    Service Request Model
    Tracks IT service requests with comprehensive status management
    """
    __tablename__ = 'service_requests'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='Medium', nullable=False)
    contact_preference = db.Column(db.String(20), default='email')
    
    # Status tracking
    status = db.Column(db.String(20), default='Pending', nullable=False)
    assigned_to = db.Column(db.String(100), nullable=True)
    
    # File attachments - FIXED: Changed from Text to String with proper length
    attachments = db.Column(db.String(1000), nullable=True)  # Store filenames as JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_status', 'status'),
        db.Index('idx_department', 'department'),
        db.Index('idx_category', 'category'),
        db.Index('idx_created_at', 'created_at'),
    )
    
    def __init__(self, **kwargs):
        """Initialize with validation"""
        # Set default values if not provided
        if 'status' not in kwargs:
            kwargs['status'] = 'Pending'
        if 'priority' not in kwargs:
            kwargs['priority'] = 'Medium'
        if 'contact_preference' not in kwargs:
            kwargs['contact_preference'] = 'email'
            
        # Convert priority to proper case before validation
        if 'priority' in kwargs:
            priority = kwargs['priority']
            if priority and priority.lower() in ['low', 'medium', 'high', 'critical']:
                kwargs['priority'] = priority.capitalize()
        
        super().__init__(**kwargs)
        self.validate()
    
    def validate(self):
        """Validate model data before saving"""
        valid_statuses = ['Pending', 'In Progress', 'Resolved', 'Closed']
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        valid_contact_prefs = ['email', 'phone', 'teams']
        
        # Ensure status is set and valid
        if not self.status or self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {', '.join(valid_statuses)}")
        
        if self.priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of: {', '.join(valid_priorities)}")
        
        if self.contact_preference not in valid_contact_prefs:
            raise ValueError(f"Invalid contact preference: {self.contact_preference}. Must be one of: {', '.join(valid_contact_prefs)}")
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValueError("Invalid email format")
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'requester_name': self.requester_name,
            'email': self.email,
            'department': self.department,
            'category': self.category,
            'description': self.description,
            'priority': self.priority,
            'contact_preference': self.contact_preference,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'attachments': self.get_attachments_list(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    def get_attachments_list(self):
        """Get list of attachments"""
        if self.attachments:
            try:
                return json.loads(self.attachments)
            except:
                return []
        return []
    
    def add_attachment(self, filename):
        """Add attachment filename to the request"""
        attachments = self.get_attachments_list()
        attachments.append(filename)
        self.attachments = json.dumps(attachments)
    
    def has_attachments(self):
        """Check if request has attachments"""
        return bool(self.get_attachments_list())
    
    def update_status(self, new_status, assigned_to=None):
        """Update request status with business logic"""
        old_status = self.status
        self.status = new_status
        self.assigned_to = assigned_to or self.assigned_to
        
        # Track resolution time
        if new_status == 'Resolved' and old_status != 'Resolved':
            self.resolved_at = datetime.now(timezone.utc)
        
        self.updated_at = datetime.now(timezone.utc)
    
    def get_priority_weight(self):
        """Get numerical weight for priority sorting"""
        priority_weights = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        return priority_weights.get(self.priority, 0)

class AdminUser(db.Model):
    """
    Administrator User Model
    Secure admin authentication with role-based access
    """
    __tablename__ = 'admin_users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # Security fields
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_username', 'username'),
        db.Index('idx_email', 'email'),
        db.Index('idx_is_active', 'is_active'),
    )
    
    def __init__(self, **kwargs):
        """Initialize with password hashing"""
        if 'password' in kwargs:
            kwargs['password_hash'] = self._hash_password(kwargs.pop('password'))
        super().__init__(**kwargs)
    
    def _hash_password(self, password):
        """Hash password with salt for security"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        ).hex() + ':' + salt
    
    def verify_password(self, password):
        """Verify password against stored hash"""
        if ':' not in self.password_hash:
            return False
        
        hash_part, salt = self.password_hash.split(':', 1)
        computed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return secrets.compare_digest(computed_hash, hash_part)
    
    def set_password(self, password):
        """Set new password with hashing"""
        self.password_hash = self._hash_password(password)
        self.updated_at = datetime.now(timezone.utc)
    
    def record_login_attempt(self, success=True):
        """Record login attempt for security monitoring"""
        if success:
            self.login_attempts = 0
            self.locked_until = None
            self.last_login = datetime.now(timezone.utc)
        else:
            self.login_attempts += 1
            if self.login_attempts >= 5:  # Lock after 5 failed attempts
                self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        db.session.commit()
    
    def is_locked(self):
        """Check if account is temporarily locked"""
        if self.locked_until and datetime.now(timezone.utc) < self.locked_until:
            return True
        return False

# ==============================================================================
# FILE UPLOAD UTILITIES
# Secure file upload handling and validation
# ==============================================================================
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_files(files, request_id):
    """Save uploaded files and return their filenames"""
    saved_files = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            # Secure the filename and add request ID prefix
            original_filename = secure_filename(file.filename)
            filename = f"{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{original_filename}"
            
            # Save file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            saved_files.append(filename)
            
            app.logger.info(f"File saved: {filename}")
        elif file and file.filename:
            app.logger.warning(f"File type not allowed: {file.filename}")
    
    return saved_files

# ==============================================================================
# AUTHENTICATION & AUTHORIZATION
# Secure authentication decorators and session management
# ==============================================================================
def admin_required(f):
    """
    Decorator to require admin authentication for route access
    Implements proper security checks and session validation
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in as admin
        if not session.get('admin_logged_in'):
            app.logger.warning(f"Unauthorized access attempt to {request.endpoint}")
            flash('Authentication required. Please log in as administrator.', 'error')
            return redirect(url_for('admin_login', next=request.url))
        
        # Verify session integrity
        if not _validate_admin_session():
            session.clear()
            flash('Session invalidated. Please log in again.', 'error')
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """
    Decorator to require super admin privileges
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_super_admin'):
            app.logger.warning(f"Unauthorized super admin access attempt to {request.endpoint}")
            flash('Insufficient privileges. Super admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def _validate_admin_session():
    """Validate admin session integrity and permissions"""
    admin_id = session.get('admin_id')
    if not admin_id:
        return False
    
    admin = db.session.get(AdminUser, admin_id)
    if not admin or not admin.is_active:
        return False
    
    # Session timeout (24 hours)
    login_time = session.get('login_time')
    if not login_time:
        return False
    
    # Ensure both datetimes are timezone-aware for comparison
    current_time = datetime.now(timezone.utc)
    if current_time - login_time > timedelta(hours=24):
        return False
    
    return True

# ==============================================================================
# TEMPLATE CONTEXT PROCESSORS
# Make global variables available to all templates
# ==============================================================================
@app.context_processor
def inject_template_globals():
    """Inject global variables into all templates"""
    return {
        'is_admin': session.get('admin_logged_in', False),
        'admin_username': session.get('admin_username', ''),
        'is_super_admin': session.get('is_super_admin', False),
        'current_year': datetime.now(timezone.utc).year,
        'app_version': '3.1.2'
    }

@app.context_processor
def utility_processor():
    """Inject utility functions into templates"""
    
    def get_category_color(index):
        """Generate consistent colors for categories"""
        colors = [
            '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1',
            '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16', '#F97316'
        ]
        return colors[index % len(colors)]
    
    def get_department_color(index):
        """Generate consistent colors for departments"""
        colors = [
            '#10B981', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6',
            '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
        ]
        return colors[index % len(colors)]
    
    def get_priority_color(priority):
        """Get color based on priority level"""
        colors = {
            'Low': '#10B981',      # Green
            'Medium': '#F59E0B',   # Yellow
            'High': '#EF4444',     # Red
            'Critical': '#DC2626'  # Dark Red
        }
        return colors.get(priority, '#6B7280')
    
    def format_datetime(value, format='medium'):
        """Format datetime for display"""
        if not value:
            return ''
        
        # Convert to naive datetime for formatting if it's timezone-aware
        if value.tzinfo is not None:
            value = value.replace(tzinfo=None)
        
        if format == 'short':
            return value.strftime('%m/%d/%Y')
        elif format == 'time':
            return value.strftime('%H:%M')
        else:
            return value.strftime('%b %d, %Y at %H:%M')
    
    return {
        'get_category_color': get_category_color,
        'get_department_color': get_department_color,
        'get_priority_color': get_priority_color,
        'format_datetime': format_datetime,
        'now': lambda: datetime.now(timezone.utc)
    }

# ==============================================================================
# APPLICATION ROUTES
# RESTful routes with proper error handling and validation
# ==============================================================================
@app.route('/')
def index():
    """Homepage route with system overview"""
    try:
        # Get basic stats for homepage
        total_requests = ServiceRequest.query.count()
        resolved_requests = ServiceRequest.query.filter_by(status='Resolved').count()
        
        return render_template('index.html',
                            total_requests=total_requests,
                            resolved_requests=resolved_requests)
    
    except Exception as e:
        app.logger.error(f"Error loading homepage: {str(e)}")
        return render_template('index.html',
                            total_requests=0,
                            resolved_requests=0)

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    """Service request submission endpoint with file upload support"""
    
    # Form options
    departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Executive']
    categories = [
        'Password Reset', 'Hardware Issue', 'Software Installation',
        'Network Problem', 'Printer Issue', 'Email Problem',
        'Access Request', 'Security Concern', 'Other'
    ]
    priorities = ['Low', 'Medium', 'High', 'Critical']
    contact_preferences = ['email', 'phone', 'teams']
    
    if request.method == 'POST':
        try:
            # Debug logging to see what's being submitted
            app.logger.info(f"Form submission received: {dict(request.form)}")
            app.logger.info(f"Files received: {[f.filename for f in request.files.getlist('attachments') if f.filename]}")
            
            # Validate required fields
            required_fields = ['requester_name', 'email', 'department', 'category', 'description']
            form_data = {field: request.form.get(field, '').strip() for field in required_fields}
            
            # Check for empty fields
            if not all(form_data.values()):
                missing_fields = [field for field, value in form_data.items() if not value]
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                app.logger.warning(f"Form validation failed: {error_msg}")
                return render_template('submit_request.html',
                                    departments=departments,
                                    categories=categories,
                                    priorities=priorities,
                                    contact_preferences=contact_preferences,
                                    error=error_msg,
                                    form_data=request.form)
            
            # Email validation
            email = form_data['email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                app.logger.warning(f"Invalid email format: {email}")
                return render_template('submit_request.html',
                                    departments=departments,
                                    categories=categories,
                                    priorities=priorities,
                                    contact_preferences=contact_preferences,
                                    error='Please provide a valid email address',
                                    form_data=request.form)
            
            # Get priority and handle case conversion
            priority = request.form.get('priority', 'Medium')
            # Convert to proper case if needed
            if priority and priority.lower() in ['low', 'medium', 'high', 'critical']:
                priority = priority.capitalize()
            
            # Get contact preference
            contact_preference = request.form.get('contact_preference', 'email')
            
            app.logger.info(f"Creating request with - Priority: {priority}, Contact: {contact_preference}")
            
            # Create new service request with explicit status
            new_request = ServiceRequest(
                requester_name=form_data['requester_name'],
                email=email,
                department=form_data['department'],
                category=form_data['category'],
                description=form_data['description'],
                priority=priority,
                contact_preference=contact_preference,
                status='Pending'  # Explicitly set status
            )
            
            db.session.add(new_request)
            db.session.flush()  # Get the ID without committing
            
            # Handle file uploads
            uploaded_files = request.files.getlist('attachments')
            if uploaded_files and any(file.filename for file in uploaded_files):
                saved_filenames = save_uploaded_files(uploaded_files, new_request.id)
                for filename in saved_filenames:
                    new_request.add_attachment(filename)
                app.logger.info(f"Saved {len(saved_filenames)} attachments for request #{new_request.id}")
            
            db.session.commit()
            
            app.logger.info(f"New service request created: #{new_request.id} by {new_request.requester_name}")
            if new_request.attachments:
                app.logger.info(f"Attachments saved: {new_request.get_attachments_list()}")
            
            return redirect(url_for('submission_success', request_id=new_request.id))
            
        except ValueError as e:
            db.session.rollback()
            app.logger.error(f"ValueError in form submission: {str(e)}")
            return render_template('submit_request.html',
                                departments=departments,
                                categories=categories,
                                priorities=priorities,
                                contact_preferences=contact_preferences,
                                error=str(e),
                                form_data=request.form)
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error submitting request: {str(e)}")
            import traceback
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            return render_template('submit_request.html',
                                departments=departments,
                                categories=categories,
                                priorities=priorities,
                                contact_preferences=contact_preferences,
                                error='An unexpected error occurred. Please try again.',
                                form_data=request.form)
    
    # GET request - show empty form
    return render_template('submit_request.html',
                         departments=departments,
                         categories=categories,
                         priorities=priorities,
                         contact_preferences=contact_preferences)

@app.route('/submission-success/<int:request_id>')
def submission_success(request_id):
    """Request submission success confirmation"""
    try:
        service_request = ServiceRequest.query.get_or_404(request_id)
        return render_template('submission_success.html',
                             request_id=request_id,
                             request=service_request)
    
    except Exception as e:
        app.logger.error(f"Error loading submission success page: {str(e)}")
        flash('Error loading request details.', 'error')
        return redirect(url_for('index'))

@app.route('/requests')
@admin_required
def view_requests():
    """Admin request management interface with attachment support"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        department_filter = request.args.get('department', '')
        priority_filter = request.args.get('priority', '')
        
        # Build query with filters
        query = ServiceRequest.query
        
        if status_filter:
            query = query.filter(ServiceRequest.status == status_filter)
        if category_filter:
            query = query.filter(ServiceRequest.category == category_filter)
        if department_filter:
            query = query.filter(ServiceRequest.department == department_filter)
        if priority_filter:
            query = query.filter(ServiceRequest.priority == priority_filter)
        
        # Get sorted results
        requests = query.order_by(
            ServiceRequest.created_at.desc()
        ).all()
        
        # Get filter options
        departments = [dept[0] for dept in 
                      db.session.query(ServiceRequest.department).distinct().all()]
        categories = [cat[0] for cat in 
                     db.session.query(ServiceRequest.category).distinct().all()]
        statuses = [status[0] for status in 
                   db.session.query(ServiceRequest.status).distinct().all()]
        priorities = [priority[0] for priority in 
                     db.session.query(ServiceRequest.priority).distinct().all()]
        
        return render_template('view_requests.html',
                             requests=requests,
                             departments=departments,
                             categories=categories,
                             statuses=statuses,
                             priorities=priorities,
                             current_filters={
                                 'status': status_filter,
                                 'category': category_filter,
                                 'department': department_filter,
                                 'priority': priority_filter
                             })
    
    except Exception as e:
        app.logger.error(f"Error loading requests: {str(e)}")
        flash('Error loading service requests.', 'error')
        return render_template('view_requests.html',
                             requests=[],
                             departments=[],
                             categories=[],
                             statuses=[],
                             priorities=[],
                             current_filters={})

@app.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with analytics"""
    try:
        # Basic metrics
        total_requests = ServiceRequest.query.count()
        pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
        resolved_requests = ServiceRequest.query.filter_by(status='Resolved').count()
        in_progress_requests = ServiceRequest.query.filter_by(status='In Progress').count()
        
        # Requests with attachments
        requests_with_attachments = ServiceRequest.query.filter(
            ServiceRequest.attachments.isnot(None),
            ServiceRequest.attachments != '[]'
        ).count()
        
        # Category statistics
        category_stats = db.session.query(
            ServiceRequest.category,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.category).all()
        
        # Department statistics
        department_stats = db.session.query(
            ServiceRequest.department,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.department).all()
        
        # Priority statistics
        priority_stats = db.session.query(
            ServiceRequest.priority,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.priority).all()
        
        # Recent requests
        recent_requests = ServiceRequest.query.order_by(
            ServiceRequest.created_at.desc()
        ).limit(10).all()
        
        # Resolution time analysis (for resolved requests)
        resolved_with_time = ServiceRequest.query.filter(
            ServiceRequest.status == 'Resolved',
            ServiceRequest.resolved_at.isnot(None)
        ).all()
        
        avg_resolution_time = None
        if resolved_with_time:
            total_seconds = sum(
                (req.resolved_at - req.created_at).total_seconds()
                for req in resolved_with_time
            )
            avg_resolution_time = total_seconds / len(resolved_with_time)
        
        return render_template('dashboard.html',
                             total_requests=total_requests,
                             pending_requests=pending_requests,
                             resolved_requests=resolved_requests,
                             in_progress_requests=in_progress_requests,
                             requests_with_attachments=requests_with_attachments,
                             category_stats=category_stats,
                             department_stats=department_stats,
                             priority_stats=priority_stats,
                             recent_requests=recent_requests,
                             avg_resolution_time=avg_resolution_time)
    
    except Exception as e:
        app.logger.error(f"Error loading dashboard: {str(e)}")
        flash('Error loading dashboard.', 'error')
        return redirect(url_for('view_requests'))

@app.route('/update-status/<int:request_id>', methods=['POST'])
@admin_required
def update_status(request_id):
    """Update request status"""
    try:
        new_status = request.form.get('status')
        assigned_to = request.form.get('assigned_to', '').strip()
        
        service_request = ServiceRequest.query.get_or_404(request_id)
        
        # Validate status
        valid_statuses = ['Pending', 'In Progress', 'Resolved']
        if new_status not in valid_statuses:
            flash('Invalid status specified.', 'error')
            return redirect(url_for('view_requests'))
        
        # Update status
        old_status = service_request.status
        service_request.update_status(new_status, assigned_to)
        
        db.session.commit()
        
        app.logger.info(f"Request #{request_id} status updated from {old_status} to {new_status} by {session.get('admin_username')}")
        
        flash(f'Request #{request_id} status updated to {new_status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating request status: {str(e)}")
        flash('Error updating request status.', 'error')
    
    return redirect(url_for('view_requests'))

# ==============================================================================
# FILE DOWNLOAD ROUTES
# Serve uploaded files securely
# ==============================================================================
@app.route('/uploads/<filename>')
@admin_required
def download_file(filename):
    """Serve uploaded files by filename"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        app.logger.error(f"File not found: {filename}")
        flash('File not found.', 'error')
        return redirect(url_for('view_requests'))

@app.route('/download_attachment/<int:request_id>/<filename>')
@admin_required
def download_attachment(request_id, filename):
    """Serve uploaded files by request ID and filename"""
    try:
        # Verify the file belongs to the request
        service_request = ServiceRequest.query.get_or_404(request_id)
        if service_request.attachments and filename in service_request.get_attachments_list():
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            flash('Attachment not found for this request.', 'error')
            return redirect(url_for('view_requests'))
            
    except FileNotFoundError:
        app.logger.error(f"File not found: {filename} for request #{request_id}")
        flash('File not found.', 'error')
        return redirect(url_for('view_requests'))

# ==============================================================================
# AUTHENTICATION ROUTES
# Secure admin authentication endpoints
# ==============================================================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login endpoint"""
    # Redirect if already logged in
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            remember_me = request.form.get('remember_me', False)
            
            # Basic validation
            if not username or not password:
                flash('Please provide both username and password.', 'error')
                return render_template('admin_login.html')
            
            # Find admin user
            admin = AdminUser.query.filter_by(username=username, is_active=True).first()
            
            # Security checks
            if not admin:
                app.logger.warning(f"Failed login attempt for non-existent user: {username}")
                flash('Invalid username or password.', 'error')
                return render_template('admin_login.html')
            
            if admin.is_locked():
                flash('Account temporarily locked due to multiple failed attempts. Please try again later.', 'error')
                return render_template('admin_login.html')
            
            # Verify password
            if admin.verify_password(password):
                # Successful login
                admin.record_login_attempt(success=True)
                
                # Set session variables
                session['admin_logged_in'] = True
                session['admin_id'] = admin.id
                session['admin_username'] = admin.username
                session['is_super_admin'] = admin.is_super_admin
                session['login_time'] = datetime.now(timezone.utc)
                
                # Remember me functionality
                if remember_me:
                    session.permanent = True
                
                app.logger.info(f"Admin login successful: {username}")
                flash(f'Welcome back, {admin.full_name}!', 'success')
                
                # Redirect to intended page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            
            else:
                # Failed login
                admin.record_login_attempt(success=False)
                app.logger.warning(f"Failed login attempt for user: {username}")
                flash('Invalid username or password.', 'error')
        
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout endpoint"""
    username = session.get('admin_username', 'Unknown')
    session.clear()
    app.logger.info(f"Admin logout: {username}")
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# ==============================================================================
# API ENDPOINTS
# RESTful API for external integrations and frontend functionality
# ==============================================================================
@app.route('/api/requests')
def api_requests():
    """API endpoint to get all service requests"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        # Get filter parameters
        status = request.args.get('status')
        category = request.args.get('category')
        department = request.args.get('department')
        
        # Build query
        query = ServiceRequest.query
        
        if status:
            query = query.filter(ServiceRequest.status == status)
        if category:
            query = query.filter(ServiceRequest.category == category)
        if department:
            query = query.filter(ServiceRequest.department == department)
        
        # Execute paginated query
        pagination = query.order_by(ServiceRequest.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'requests': [req.to_dict() for req in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    
    except Exception as e:
        app.logger.error(f"API error in /api/requests: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/requests/<int:request_id>')
def api_request_details(request_id):
    """API endpoint to get specific request details with attachments"""
    try:
        service_request = ServiceRequest.query.get_or_404(request_id)
        
        return jsonify({
            'success': True,
            'request': service_request.to_dict()
        })
    
    except Exception as e:
        app.logger.error(f"API error in /api/requests/{request_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Request not found'
        }), 404

@app.route('/api/requests/<int:request_id>/status', methods=['PUT'])
@admin_required
def api_update_status(request_id):
    """API endpoint to update request status"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        new_status = data.get('status')
        assigned_to = data.get('assigned_to')
        
        if not new_status:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        service_request = ServiceRequest.query.get_or_404(request_id)
        
        # Validate status
        valid_statuses = ['Pending', 'In Progress', 'Resolved']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        # Update status
        old_status = service_request.status
        service_request.update_status(new_status, assigned_to)
        
        db.session.commit()
        
        app.logger.info(f"API: Request #{request_id} status updated from {old_status} to {new_status}")
        
        return jsonify({
            'success': True,
            'message': f'Request status updated to {new_status}',
            'request': service_request.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"API error updating status for request {request_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/stats')
@admin_required
def api_stats():
    """API endpoint to get system statistics"""
    try:
        # Basic counts
        total_requests = ServiceRequest.query.count()
        pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
        in_progress_requests = ServiceRequest.query.filter_by(status='In Progress').count()
        resolved_requests = ServiceRequest.query.filter_by(status='Resolved').count()
        
        # Requests with attachments
        requests_with_attachments = ServiceRequest.query.filter(
            ServiceRequest.attachments.isnot(None),
            ServiceRequest.attachments != '[]'
        ).count()
        
        # Category distribution
        category_stats = db.session.query(
            ServiceRequest.category,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.category).all()
        
        # Department distribution
        department_stats = db.session.query(
            ServiceRequest.department,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.department).all()
        
        # Priority distribution
        priority_stats = db.session.query(
            ServiceRequest.priority,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.priority).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'in_progress_requests': in_progress_requests,
                'resolved_requests': resolved_requests,
                'requests_with_attachments': requests_with_attachments,
                'categories': dict(category_stats),
                'departments': dict(department_stats),
                'priorities': dict(priority_stats)
            }
        })
    
    except Exception as e:
        app.logger.error(f"API error in /api/stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# ==============================================================================
# ERROR HANDLERS
# Global error handling for better user experience
# ==============================================================================
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    app.logger.error(f"500 Error: {str(error)}")
    
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Access forbidden'}), 403
    flash('Access forbidden. Please log in with appropriate permissions.', 'error')
    return redirect(url_for('admin_login'))

# ==============================================================================
# DATABASE MIGRATION UTILITY
# Helper functions to update database schema - FIXED FOR SQLALCHEMY 2.0+
# ==============================================================================
def migrate_database():
    """Migrate database schema to support attachments"""
    with app.app_context():
        try:
            # Check if attachments column exists
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('service_requests')]
            
            if 'attachments' not in columns:
                app.logger.info("Adding attachments column to service_requests table...")
                
                # For SQLite, we need to create a new table and copy data
                if 'sqlite' in db.engine.url.drivername:
                    # SQLite doesn't support ALTER TABLE ADD COLUMN for some types, so we recreate
                    with db.engine.connect() as conn:
                        # Create new table
                        conn.execute(text('''
                            CREATE TABLE service_requests_new (
                                id INTEGER PRIMARY KEY,
                                requester_name VARCHAR(100) NOT NULL,
                                email VARCHAR(120) NOT NULL,
                                department VARCHAR(50) NOT NULL,
                                category VARCHAR(50) NOT NULL,
                                description TEXT NOT NULL,
                                priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
                                contact_preference VARCHAR(20) DEFAULT 'email',
                                status VARCHAR(20) NOT NULL DEFAULT 'Pending',
                                assigned_to VARCHAR(100),
                                attachments VARCHAR(1000),
                                created_at DATETIME NOT NULL,
                                updated_at DATETIME,
                                resolved_at DATETIME
                            )
                        '''))
                        
                        # Copy data from old table
                        conn.execute(text('''
                            INSERT INTO service_requests_new 
                            (id, requester_name, email, department, category, description, 
                             priority, contact_preference, status, assigned_to, created_at, updated_at, resolved_at)
                            SELECT id, requester_name, email, department, category, description, 
                                   priority, contact_preference, status, assigned_to, created_at, updated_at, resolved_at
                            FROM service_requests
                        '''))
                        
                        # Drop old table and rename new one
                        conn.execute(text('DROP TABLE service_requests'))
                        conn.execute(text('ALTER TABLE service_requests_new RENAME TO service_requests'))
                        
                        conn.commit()
                    
                    app.logger.info("✅ Database migrated successfully for SQLite")
                else:
                    # For other databases, use ALTER TABLE
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE service_requests ADD COLUMN attachments VARCHAR(1000)'))
                        conn.commit()
                    app.logger.info("✅ Database migrated successfully for other databases")
            else:
                app.logger.info("✅ Database already has attachments column")
                
        except Exception as e:
            app.logger.error(f"Database migration failed: {str(e)}")
            raise

# ==============================================================================
# APPLICATION INITIALIZATION
# Database setup and admin user creation
# ==============================================================================
def setup_logging():
    """Configure application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/service_desk.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Demulla Service Desk startup')

def init_db():
    """Initialize database and create default admin user"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Migrate database if needed
            migrate_database()
            
            # Create default admin user if none exists
            if not AdminUser.query.first():
                default_admin = AdminUser(
                    username='admin',
                    email='admin@demulla.com',
                    full_name='System Administrator',
                    is_super_admin=True
                )
                default_admin.set_password('admin123')  # Change in production!
                db.session.add(default_admin)
                db.session.commit()
                app.logger.info("✅ Default admin user created: username='admin'")
            
            app.logger.info("✅ Database initialization completed successfully!")
            
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

# ==============================================================================
# APPLICATION STARTUP
# Main entry point with proper initialization
# ==============================================================================
if __name__ == '__main__':
    # Setup logging
    setup_logging()
    
    # Initialize database
    init_db()
    
    # Startup message
    app.logger.info("🚀 Starting Demulla IT Service Desk with Admin Authentication...")
    app.logger.info("📧 Admin Login: http://127.0.0.1:5000/admin/login")
    app.logger.info("🔧 Default credentials: admin / admin123")
    app.logger.info("📎 File uploads enabled: /uploads directory created")
    app.logger.info("🔄 Database schema updated to support file attachments")
    app.logger.info("📎 File download routes added: download_file and download_attachment")
    
    # Run application
    app.run(
        debug=os.getenv('FLASK_ENV') == 'development',
        host='0.0.0.0',
        port=5000
    )
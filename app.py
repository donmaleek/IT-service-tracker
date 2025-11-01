"""
IT Service Request Tracking System with Admin Authentication
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import hashlib
import secrets
from functools import wraps

# Create Flask app
app = Flask(__name__)

# Set configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///service_requests.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-very-secure-secret-key-change-in-production'

# Initialize database
db = SQLAlchemy(app)

# Models
class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'requester_name': self.requester_name,
            'department': self.department,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

# Authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as administrator to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Template context processor to make admin status available in templates
@app.context_processor
def inject_admin_status():
    return dict(is_admin=session.get('admin_logged_in', False))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    departments = ['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales']
    categories = ['Password Reset', 'Hardware Issue', 'Software Installation', 
                 'Network Problem', 'Printer Issue', 'Other']
    
    if request.method == 'POST':
        try:
            requester_name = request.form.get('requester_name', '').strip()
            department = request.form.get('department', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            
            if not all([requester_name, department, category, description]):
                return render_template('submit_request.html', 
                                    departments=departments, 
                                    categories=categories,
                                    error='All fields are required')
            
            new_request = ServiceRequest(
                requester_name=requester_name,
                department=department,
                category=category,
                description=description
            )
            
            db.session.add(new_request)
            db.session.commit()
            
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
    return render_template('submission_success.html', request_id=request_id)

@app.route('/requests')
@admin_required
def view_requests():
    try:
        status_filter = request.args.get('status', '')
        category_filter = request.args.get('category', '')
        department_filter = request.args.get('department', '')
        
        query = ServiceRequest.query
        
        if status_filter:
            query = query.filter(ServiceRequest.status == status_filter)
        if category_filter:
            query = query.filter(ServiceRequest.category == category_filter)
        if department_filter:
            query = query.filter(ServiceRequest.department == department_filter)
        
        requests = query.order_by(ServiceRequest.created_at.desc()).all()
        
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
    except Exception as e:
        return f'Error loading requests: {str(e)}', 500

@app.route('/dashboard')
@admin_required
def dashboard():
    try:
        total_requests = ServiceRequest.query.count()
        pending_requests = ServiceRequest.query.filter_by(status='Pending').count()
        resolved_requests = ServiceRequest.query.filter_by(status='Resolved').count()
        in_progress_requests = ServiceRequest.query.filter_by(status='In Progress').count()
        
        category_stats = db.session.query(
            ServiceRequest.category,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.category).all()
        
        department_stats = db.session.query(
            ServiceRequest.department,
            db.func.count(ServiceRequest.id)
        ).group_by(ServiceRequest.department).all()
        
        recent_requests = ServiceRequest.query.order_by(
            ServiceRequest.created_at.desc()
        ).limit(5).all()
        
        return render_template('dashboard.html',
                             total_requests=total_requests,
                             pending_requests=pending_requests,
                             resolved_requests=resolved_requests,
                             in_progress_requests=in_progress_requests,
                             category_stats=category_stats,
                             department_stats=department_stats,
                             recent_requests=recent_requests)
    except Exception as e:
        return f'Error loading dashboard: {str(e)}', 500

@app.route('/update-status/<int:request_id>', methods=['POST'])
@admin_required
def update_status(request_id):
    try:
        new_status = request.form.get('status')
        service_request = ServiceRequest.query.get_or_404(request_id)
        
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

# Admin Authentication Routes - ONLY ONE DEFINITION
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    # Redirect if already logged in
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = AdminUser.query.filter_by(username=username, is_active=True).first()
        
        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            session['admin_id'] = admin.id
            flash('Successfully logged in as administrator.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# API Routes
@app.route('/api/requests')
def api_requests():
    try:
        requests = ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(requests),
            'requests': [req.to_dict() for req in requests]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/requests/<int:request_id>')
def api_request_details(request_id):
    try:
        request = ServiceRequest.query.get_or_404(request_id)
        return jsonify({
            'success': True,
            'request': request.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/requests/<int:request_id>/status', methods=['PUT'])
@admin_required
def api_update_status(request_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        service_request = ServiceRequest.query.get_or_404(request_id)
        service_request.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request #{request_id} status updated to {new_status}',
            'request': service_request.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Template helper functions
@app.context_processor
def utility_processor():
    def get_category_color(index):
        colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', 
                 '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1']
        return colors[index % len(colors)]
    
    def get_department_color(index):
        colors = ['#10B981', '#F59E0B', '#3B82F6', '#EF4444', '#8B5CF6',
                 '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1']
        return colors[index % len(colors)]
    
    return {
        'get_category_color': get_category_color,
        'get_department_color': get_department_color
    }

# Initialize database and create default admin
def init_db():
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not AdminUser.query.first():
            default_admin = AdminUser(
                username='admin',
                email='admin@demulla.com'
            )
            default_admin.set_password('admin123')  # Change this in production!
            db.session.add(default_admin)
            db.session.commit()
            print("✅ Default admin created: username='admin', password='admin123'")
        
        print("✅ Database tables created successfully!")

if __name__ == '__main__':
    init_db()
    print("🚀 Starting IT Service Tracker with Admin Authentication...")
    print("📧 Admin Login: http://127.0.0.1:5000/admin/login")
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
Database models for the IT Service Request Tracking System.
Defines the structure for storing service requests and system data.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class ServiceRequest(db.Model):
    """
    Represents an IT service request submitted by staff members.
    
    Attributes:
        id (int): Primary key, unique identifier for each request
        requester_name (str): Name of the person submitting the request
        department (str): Department of the requester
        category (str): Type of issue (Password Reset, Hardware, Software, etc.)
        description (str): Detailed description of the issue
        status (str): Current status of the request (Pending, In Progress, Resolved)
        created_at (datetime): Timestamp when the request was created
        updated_at (datetime): Timestamp when the request was last updated
    """
    
    __tablename__ = 'service_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Convert ServiceRequest object to dictionary for API responses.
        
        Returns:
            dict: Dictionary representation of the service request
        """
        return {
            'id': self.id,
            'requester_name': self.requester_name,
            'department': self.department,
            'category': self.category,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        """
        String representation of ServiceRequest object.
        
        Returns:
            str: Formatted string showing request ID and requester name
        """
        return f'<ServiceRequest {self.id} - {self.requester_name}>'

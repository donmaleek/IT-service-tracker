#!/usr/bin/env python3
"""
Database initialization script
"""
from app import create_app, db

def init_database():
    """Initialize the database with all tables"""
    app = create_app('development')
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        print(f"📁 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"📊 Tables created: {tables}")

if __name__ == '__main__':
    init_database()
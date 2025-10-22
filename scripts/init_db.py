"""Initialize database script"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tracker.core.database import engine, init_db
from tracker.core.models import User
from tracker.config import settings
from sqlalchemy.orm import Session


def main():
    """Initialize database with tables and default user"""
    
    print("Initializing Tracker database...")
    
    # Create database directory
    db_path = settings.get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    init_db()
    print(f"✅ Database created at: {db_path}")
    
    # Create default user
    with Session(engine) as session:
        existing_user = session.query(User).filter_by(username="default").first()
        if not existing_user:
            user = User(username="default", email=None)
            session.add(user)
            session.commit()
            print("✅ Default user created")
        else:
            print("ℹ️  Default user already exists")
    
    print("\n🎉 Database initialized successfully!")
    print("\nNext steps:")
    print("  1. Create your first entry: tracker new")
    print("  2. View your entry: tracker show today")


if __name__ == "__main__":
    main()

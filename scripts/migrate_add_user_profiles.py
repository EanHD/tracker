#!/usr/bin/env python3
"""
Migration script to add user_profiles table for character sheet feature.

This creates the UserProfile table that stores personalized character data
built from analyzing user entries.
"""

from tracker.core.database import SessionLocal, engine
from tracker.core.models import Base, UserProfile
from sqlalchemy import inspect

def main():
    """Run the migration"""
    
    print("🔄 Checking database schema...")
    
    # Check if table already exists
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if 'user_profiles' in existing_tables:
        print("✓ user_profiles table already exists")
        return
    
    print("📊 Creating user_profiles table...")
    
    try:
        # Create the user_profiles table
        UserProfile.__table__.create(engine)
        print("✓ Successfully created user_profiles table")
        
        print("\n✅ Migration complete!")
        print("\nThe character sheet feature is now ready to use:")
        print("  • tracker profile show    - View your character profile")
        print("  • tracker profile analyze - Re-analyze from entries")
        print("  • tracker retry <date>    - Regenerate AI feedback with character context")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    main()

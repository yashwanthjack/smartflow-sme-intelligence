#!/usr/bin/env python
"""
Fix user passwords in database - convert SHA256 hashes to bcrypt
"""

import os
import sys
import hashlib

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.auth import get_password_hash

def fix_passwords():
    db: Session = next(get_db())

    users = db.query(User).all()
    for user in users:
        # Check if hash is SHA256 (64 chars hex)
        if len(user.hashed_password) == 64 and all(c in '0123456789abcdef' for c in user.hashed_password.lower()):
            print(f"Fixing password for {user.email}")
            # Assume the password is known or re-hash with default
            # Since we don't know the original password, we'll set a default
            # For demo, set to "password" or something
            # But better to check if it's the demo user
            if user.email == "yash@gmail.com":
                user.hashed_password = get_password_hash("yash@1234")
            elif user.email == "admin@gmail.com":
                user.hashed_password = get_password_hash("admin")
            else:
                print(f"Unknown user {user.email}, skipping")
                continue
            print(f"Updated hash for {user.email}")

    db.commit()
    db.close()
    print("Password fixes applied.")

if __name__ == "__main__":
    fix_passwords()
# Copyright (c) 2024 Salman Ahmed. All rights reserved.
import os
import sys

def check_license():
    """Display license notice on startup"""
    print("=" * 60)
    print("PROPRIETARY SOFTWARE - Salman Ahmed")
    print("Repository: https://github.com/salman-ahmed356/blackpoint.git")
    print("Contact: salmanahmad356240@gmail.com")
    print("=" * 60)
    print("This software is for authorized use only.")
    print("Commercial use requires written permission.")
    print("=" * 60)
    
    # Optional: Add environment check for production
    if os.getenv('AUTHORIZED_USER') != 'true':
        print("WARNING: Unauthorized usage detected!")
        print("Contact salmanahmad356240@gmail.com for licensing.")
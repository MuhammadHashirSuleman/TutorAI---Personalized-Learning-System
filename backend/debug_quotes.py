#!/usr/bin/env python
"""
Simple script to debug and seed quotes without full Django setup
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    # Skip django.setup() for now since it's failing due to dependencies
    print("Testing database connection...")
    
    # Try to import settings to see if basic config works
    from django.conf import settings
    print(f"Database: {settings.DATABASES['default']['NAME']}")
    
    # Try to connect to database directly
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Available tables: {[table[0] for table in tables]}")
        
        # Check if quote-related tables exist
        quote_tables = [table[0] for table in tables if 'quote' in table[0].lower()]
        print(f"Quote-related tables: {quote_tables}")
        
        if 'motivationalquote' in [table[0].lower() for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM users_motivationalquote")
            count = cursor.fetchone()[0]
            print(f"MotivationalQuote count: {count}")
        else:
            print("MotivationalQuote table not found")
            
        if 'daily_quote_assignments' in [table[0].lower() for table in tables]:
            cursor.execute("SELECT COUNT(*) FROM daily_quote_assignments")
            count = cursor.fetchone()[0]
            print(f"DailyQuoteAssignment count: {count}")
        else:
            print("DailyQuoteAssignment table not found")
            
except Exception as e:
    print(f"Error: {e}")
    print("Cannot connect to database or check tables")

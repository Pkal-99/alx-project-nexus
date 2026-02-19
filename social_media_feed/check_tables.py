#!/usr/bin/env python
import os
import django
from django.conf import settings
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media_feed.settings')
django.setup()

# Get database cursor
cursor = connection.cursor()

# Query to get all table names in public schema
cursor.execute("""
    SELECT tablename 
    FROM pg_catalog.pg_tables 
    WHERE schemaname = 'public'
    ORDER BY tablename
""")

tables = [row[0] for row in cursor.fetchall()]

print("Django tables created in PostgreSQL:")
print("=" * 40)
for table in tables:
    print(f"• {table}")
print(f"\nTotal tables: {len(tables)}")

#!/usr/bin/env python
"""Script to create sample users"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/enigmatix/ecommerce_ai')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Delete and recreate admin
User.objects.filter(username='admin').delete()
admin = User.objects.create_superuser('admin', 'admin@shopease.com', 'admin123')
admin.first_name = 'Admin'
admin.last_name = 'User'
admin.save()
print('Admin created: admin / admin123')

# Create test users
test_users = [
    ('john_doe', 'john@example.com', 'John', 'Doe'),
    ('jane_smith', 'jane@example.com', 'Jane', 'Smith'),
]

for uname, email, fname, lname in test_users:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, 'user123')
        u.first_name = fname
        u.last_name = lname
        u.save()
        print(f'Created: {uname} / user123')

print(f'\nTotal users: {User.objects.count()}')
for u in User.objects.all():
    role = 'admin' if u.is_superuser else 'customer'
    print(f'  - {u.username} ({role})')


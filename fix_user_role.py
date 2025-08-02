import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from scheduler.models import User

# Get the user
user = User.objects.get(username='daniel')
print(f'Current role: "{user.role}" (length: {len(user.role)})')
print(f'Current phone: "{user.phone}" (type: {type(user.phone)})')

# Update the role and fix the phone field
user.role = 'student'
if user.phone == '' or user.phone is None:
    user.phone = 0  # Set default value
user.save()

print(f'Updated role: "{user.role}" (length: {len(user.role)})')
print(f'Updated phone: "{user.phone}" (type: {type(user.phone)})')
print('User role updated successfully!')

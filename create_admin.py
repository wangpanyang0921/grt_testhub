from apps.users.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@testhub.com', 'admin123')
    print('Superuser admin created with password admin123')
else:
    print('Superuser admin already exists')

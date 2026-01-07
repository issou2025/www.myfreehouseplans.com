from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing admin if exists
User.objects.filter(username='admin').delete()

# Create new superuser
admin = User.objects.create_superuser(
    username='admin',
    email='admin@freehouseplan.com',
    password='admin123'
)

print(f"✅ Superuser created: {admin.username}")
print(f"   Email: {admin.email}")
print(f"   Password: admin123")

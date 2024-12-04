from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from workshop.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a superuser and sets up admin profile'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write('Admin user already exists')
            return

        # Create superuser
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )

        # Create admin profile
        UserProfile.objects.create(
            user=admin,
            role='admin',
            phone='123-456-7890'
        )

        self.stdout.write(self.style.SUCCESS('Successfully created admin user and profile'))
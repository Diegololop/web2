from django.core.management.base import BaseCommand
from workshop.models import BusinessHours
from datetime import time

class Command(BaseCommand):
    help = 'Creates default business hours'

    def handle(self, *args, **options):
        # Default business hours: Mon-Fri 9:00-18:00, Sat 9:00-13:00, Sun closed
        default_hours = [
            # Monday to Friday
            {'day': 0, 'open_time': '09:00', 'close_time': '18:00'},
            {'day': 1, 'open_time': '09:00', 'close_time': '18:00'},
            {'day': 2, 'open_time': '09:00', 'close_time': '18:00'},
            {'day': 3, 'open_time': '09:00', 'close_time': '18:00'},
            {'day': 4, 'open_time': '09:00', 'close_time': '18:00'},
            # Saturday
            {'day': 5, 'open_time': '09:00', 'close_time': '13:00'},
            # Sunday
            {'day': 6, 'is_closed': True, 'open_time': '09:00', 'close_time': '09:00'},
        ]

        for hours in default_hours:
            BusinessHours.objects.get_or_create(
                day=hours['day'],
                defaults={
                    'open_time': hours['open_time'],
                    'close_time': hours['close_time'],
                    'is_closed': hours.get('is_closed', False)
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created default business hours'))
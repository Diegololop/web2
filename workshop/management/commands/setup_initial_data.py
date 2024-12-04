from django.core.management.base import BaseCommand
from workshop.models import Product

class Command(BaseCommand):
    help = 'Creates initial services'

    def handle(self, *args, **options):
        services = [
            {
                'name': 'Cambio de Aceite',
                'description': 'Servicio completo de cambio de aceite y filtro. Incluye revisión de niveles.',
                'price': 45000,
                'stock': 999,
                'category': 'service',
                'duration': 30
            },
            {
                'name': 'Alineación y Balanceo',
                'description': 'Servicio de alineación computarizada y balanceo de ruedas.',
                'price': 35000,
                'stock': 999,
                'category': 'service',
                'duration': 45
            },
            {
                'name': 'Revisión de Frenos',
                'description': 'Inspección completa del sistema de frenos, incluye pastillas y discos.',
                'price': 25000,
                'stock': 999,
                'category': 'service',
                'duration': 60
            },
            {
                'name': 'Diagnóstico Computarizado',
                'description': 'Diagnóstico completo del sistema electrónico del vehículo.',
                'price': 30000,
                'stock': 999,
                'category': 'service',
                'duration': 40
            },
            {
                'name': 'Mantenimiento General',
                'description': 'Servicio completo de mantenimiento preventivo, incluye revisión de 21 puntos.',
                'price': 85000,
                'stock': 999,
                'category': 'service',
                'duration': 120
            }
        ]

        for service_data in services:
            Product.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully created initial services'))
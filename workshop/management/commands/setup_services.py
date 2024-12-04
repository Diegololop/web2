from django.core.management.base import BaseCommand
from workshop.models import Product

class Command(BaseCommand):
    help = 'Creates initial services with Chilean peso prices'

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
            },
            {
                'name': 'Cambio de Pastillas de Freno',
                'description': 'Reemplazo de pastillas de freno delanteras o traseras.',
                'price': 55000,
                'stock': 999,
                'category': 'service',
                'duration': 90
            },
            {
                'name': 'Cambio de Batería',
                'description': 'Servicio de cambio de batería con diagnóstico del sistema eléctrico.',
                'price': 15000,
                'stock': 999,
                'category': 'service',
                'duration': 30
            },
            {
                'name': 'Limpieza de Inyectores',
                'description': 'Limpieza y calibración de inyectores con equipo especializado.',
                'price': 65000,
                'stock': 999,
                'category': 'service',
                'duration': 60
            }
        ]

        for service_data in services:
            Product.objects.create(**service_data)

        self.stdout.write(self.style.SUCCESS('Successfully created services with Chilean peso prices'))
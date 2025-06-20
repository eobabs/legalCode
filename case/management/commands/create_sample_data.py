from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import models

from case.models import Case, Donation
from datetime import date, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample data for demo'

    def handle(self, *args, **options):
        # Create sample users
        if not User.objects.filter(username='demo_user').exists():
            demo_user = User.objects.create_user(
                username='demo_user',
                email='demo@example.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )

            donor1 = User.objects.create_user(
                username='donor1',
                email='donor1@example.com',
                password='donor123',
                first_name='John',
                last_name='Donor'
            )

            # Create sample cases
            case1 = Case.objects.create(
                title='Fighting Wrongful Termination',
                description='I was wrongfully terminated from my job after reporting safety violations. I need legal representation to fight this injustice and protect other workers.',
                goal_amount=Decimal('5000.00'),
                creator=demo_user,
                deadline=date.today() + timedelta(days=30)
            )

            case2 = Case.objects.create(
                title='Housing Discrimination Case',
                description='Facing housing discrimination based on family status. Need legal help to ensure fair housing rights for families with children.',
                goal_amount=Decimal('3500.00'),
                creator=demo_user,
                deadline=date.today() + timedelta(days=45)
            )

            # Create sample donations
            Donation.objects.create(
                case=case1,
                donor=donor1,
                amount=Decimal('100.00'),
                message='Standing with you in this fight for justice!'
            )

            Donation.objects.create(
                case=case2,
                donor=donor1,
                amount=Decimal('50.00'),
                message='Fair housing is a basic right.',
                is_anonymous=True
            )

            # Update raised amounts
            case1.raised_amount = case1.donations.aggregate(total=models.Sum('amount'))['total'] or 0
            case2.raised_amount = case2.donations.aggregate(total=models.Sum('amount'))['total'] or 0
            case1.save()
            case2.save()

            self.stdout.write(
                self.style.SUCCESS('Sample data created successfully!')
            )
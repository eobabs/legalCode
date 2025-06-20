from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.utils import timezone


class Case(models.Model):
    CASE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('expired', 'Expired'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cases')
    status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField()
    image = models.ImageField(upload_to='case_images/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.deadline <= timezone.now().date():
            raise ValidationError('Deadline must be in the future.')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('case_detail', kwargs={'pk': self.pk})

    @property
    def progress_percentage(self):
        if self.goal_amount > 0:
            return min((self.raised_amount / self.goal_amount) * 100, 100)
        return 0

    @property
    def remaining_amount(self):
        return max(self.goal_amount - self.raised_amount, 0)

    @property
    def is_expired(self):
        return timezone.now().date() > self.deadline

    @property
    def days_remaining(self):
        if self.is_expired:
            return 0
        return (self.deadline - timezone.now().date()).days

    @property
    def total_donors(self):
        return self.donations.values('donor').distinct().count()

    def can_receive_donations(self):
        return self.status == 'active' and not self.is_expired


class Donation(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))]
    )
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        donor_name = "Anonymous" if self.is_anonymous else self.donor.username
        return f"{donor_name} - ${self.amount} to {self.case.title}"

    class Meta:
        ordering = ['-created_at']

from django.contrib import admin
from .models import Case, Donation

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'goal_amount', 'raised_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'creator__username']
    readonly_fields = ['raised_amount']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['case', 'donor', 'amount', 'is_anonymous', 'created_at']
    list_filter = ['is_anonymous', 'created_at']
    search_fields = ['case__title', 'donor__username']

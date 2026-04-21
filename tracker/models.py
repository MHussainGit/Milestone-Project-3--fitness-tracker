"""
tracker/models.py — FitTrack data models.
"""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Count, Sum
from django.utils import timezone


class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('strength',    'Strength'),
        ('cardio',      'Cardio'),
        ('flexibility', 'Flexibility'),
    ]
    MUSCLE_GROUP_CHOICES = [
        ('Chest', 'Chest'), ('Back', 'Back'), ('Legs', 'Legs'),
        ('Shoulders', 'Shoulders'), ('Arms', 'Arms'),
        ('Core', 'Core'), ('Full Body', 'Full Body'),
    ]
    name         = models.CharField(max_length=100, unique=True)
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='strength')
    muscle_group = models.CharField(max_length=50, choices=MUSCLE_GROUP_CHOICES, blank=True)
    description  = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class WorkoutQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user=user)

    def monthly_stats(self, reference_date=None):
        reference_date = reference_date or timezone.localdate()
        month_start = reference_date.replace(day=1)
        if month_start.month == 12:
            next_month_start = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month_start = month_start.replace(month=month_start.month + 1)

        return self.filter(
            date__gte=month_start,
            date__lt=next_month_start
        ).aggregate(
            total_sets=Sum('entries__sets'),
            total_workouts=Count('id', distinct=True),
            total_exercises=Count('entries__exercise', distinct=True),
        )

    def streak(self, reference_date=None):
        reference_date = reference_date or timezone.localdate()
        workout_dates = set(self.values_list('date', flat=True))
        streak = 0
        current_date = reference_date

        while current_date in workout_dates:
            streak += 1
            current_date -= timedelta(days=1)

        return streak

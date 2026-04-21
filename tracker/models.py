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
    

class WorkoutManager(models.Manager):
    def get_queryset(self):
        return WorkoutQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def monthly_stats(self, user, reference_date=None):
        return self.for_user(user).monthly_stats(reference_date)

    def streak(self, user, reference_date=None):
        return self.for_user(user).streak(reference_date)


class Workout(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    name       = models.CharField(max_length=100)
    date       = models.DateField()
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = WorkoutManager()

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.name} — {self.date} ({self.user.username})"

    def total_volume(self):
        total = Decimal('0')
        for entry in self.entries.all():
            if entry.weight:
                total += Decimal(entry.sets) * Decimal(entry.reps) * entry.weight
        return float(total)

    def total_sets(self):
        return sum(entry.sets for entry in self.entries.all())

    def entry_count(self):
        return self.entries.count()


class WorkoutEntry(models.Model):
    workout  = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='entries')
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name='workout_entries')
    sets     = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    reps     = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    weight   = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                   help_text='Weight in kg. Leave blank for bodyweight.')
    notes    = models.CharField(max_length=200, blank=True)
    is_pr    = models.BooleanField(default=False)

    class Meta:
        order_with_respect_to = 'workout'

    def __str__(self):
        return f"{self.exercise.name} — {self.sets}x{self.reps}"

    def volume(self):
        if self.weight:
            return float(Decimal(self.sets) * Decimal(self.reps) * self.weight)
        return None

    def estimated_one_rep_max(self):
        """Epley formula: weight * (1 + reps/30). Only for reps <= 12."""
        if self.weight and self.reps and self.reps <= 12:
            multiplier = Decimal(1) + Decimal(self.reps) / Decimal(30)
            estimate = self.weight * multiplier
            return float(estimate.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        return None


class BodyWeightEntry(models.Model):
    """A single bodyweight measurement for a user."""
    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bodyweight_entries')
    date   = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2,
                                 validators=[MinValueValidator(0.1)])
    notes  = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = [['user', 'date']]

    def __str__(self):
        return f"{self.user.username} — {self.date}: {self.weight}kg"


class DailyNote(models.Model):
    """One short journal entry per user per day."""
    MOOD_CHOICES = [
        ('great', 'Great'), ('good', 'Good'), ('ok', 'OK'),
        ('tired', 'Tired'), ('bad', 'Bad'),
    ]
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_notes')
    date    = models.DateField()
    mood    = models.CharField(max_length=10, choices=MOOD_CHOICES, blank=True)
    content = models.TextField(max_length=1000)

    class Meta:
        ordering = ['-date']
        unique_together = [['user', 'date']]

    def __str__(self):
        return f"{self.user.username} note — {self.date}"


class PersonalRecord(models.Model):
    """Best weight lifted for each exercise per user."""
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_records')
    exercise      = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='personal_records')
    best_weight   = models.DecimalField(max_digits=6, decimal_places=2)
    best_reps     = models.PositiveIntegerField()
    achieved_date = models.DateField()
    workout       = models.ForeignKey(Workout, on_delete=models.SET_NULL, null=True,
                                      related_name='prs_achieved')

    class Meta:
        unique_together = [['user', 'exercise']]

    def __str__(self):
        return f"{self.user.username} PR — {self.exercise.name}: {self.best_weight}kg"
    
    def est_1rm(self):
        """Calculate estimated 1RM using Epley formula: Weight × (1 + Reps/30)"""
        if self.best_reps <= 12:
            multiplier = Decimal(1) + Decimal(self.best_reps) / Decimal(30)
            estimate = self.best_weight * multiplier
            return float(estimate.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        return None

class WorkoutTemplate(models.Model):
    """A saved workout structure that can be reused."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_templates')
    name       = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (template)"


class WorkoutTemplateItem(models.Model):
    """One exercise line within a WorkoutTemplate."""
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name='items')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets     = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    reps     = models.PositiveIntegerField(default=10, validators=[MinValueValidator(1)])
    notes    = models.CharField(max_length=200, blank=True)

    class Meta:
        order_with_respect_to = 'template'

    def __str__(self):
        return f"{self.template.name} — {self.exercise.name}"

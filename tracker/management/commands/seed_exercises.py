"""
Management command: python manage.py seed_exercises

Seeds the Exercise library with sensible defaults.
Safe to run multiple times — skips exercises that already exist.
"""

from django.core.management.base import BaseCommand
from tracker.models import Exercise


DEFAULT_EXERCISES = [
    {'name': 'Bench Press',        'category': 'strength',    'muscle_group': 'Chest',      'description': 'Barbell press on a flat bench.'},
    {'name': 'Squat',              'category': 'strength',    'muscle_group': 'Legs',       'description': 'Barbell back squat.'},
    {'name': 'Deadlift',           'category': 'strength',    'muscle_group': 'Back',       'description': 'Conventional barbell deadlift.'},
    {'name': 'Pull-up',            'category': 'strength',    'muscle_group': 'Back',       'description': 'Bodyweight pull-up.'},
    {'name': 'Overhead Press',     'category': 'strength',    'muscle_group': 'Shoulders',  'description': 'Barbell pressed overhead.'},
    {'name': 'Barbell Row',        'category': 'strength',    'muscle_group': 'Back',       'description': 'Bent-over barbell row.'},
    {'name': 'Dumbbell Curl',      'category': 'strength',    'muscle_group': 'Arms',       'description': 'Alternating dumbbell curl.'},
    {'name': 'Tricep Dips',        'category': 'strength',    'muscle_group': 'Arms',       'description': 'Parallel bar dips.'},
    {'name': 'Plank',              'category': 'strength',    'muscle_group': 'Core',       'description': 'Hold a plank position. Use reps = seconds.'},
    {'name': 'Running',            'category': 'cardio',      'muscle_group': 'Legs',       'description': 'Outdoor or treadmill running.'},
    {'name': 'Rowing Machine',     'category': 'cardio',      'muscle_group': 'Full Body',  'description': 'Ergometer rowing.'},
    {'name': 'Jump Rope',          'category': 'cardio',      'muscle_group': 'Full Body',  'description': 'Skipping rope intervals.'},
    {'name': 'Yoga Flow',          'category': 'flexibility', 'muscle_group': 'Full Body',  'description': 'Full-body yoga sequence.'},
    {'name': 'Hip Flexor Stretch', 'category': 'flexibility', 'muscle_group': 'Legs',       'description': 'Kneeling hip flexor stretch.'},
    {'name': 'Romanian Deadlift',  'category': 'strength',    'muscle_group': 'Legs',       'description': 'Hinge movement targeting hamstrings.'},
]


class Command(BaseCommand):
    help = 'Seed the exercise library with default exercises.'

    def handle(self, *args, **options):
        created_count = 0

        for data in DEFAULT_EXERCISES:
            # get_or_create prevents duplicates on re-runs
            obj, created = Exercise.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category':     data['category'],
                    'muscle_group': data['muscle_group'],
                    'description':  data['description'],
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {obj.name}'))
            else:
                self.stdout.write(f'  Skipped (already exists): {obj.name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nDone — {created_count} exercise(s) created.')
        )

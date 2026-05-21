"""
tests/test_fittrack.py
----------------------
Automated test suite for FitTrack.

Covers (rubric 1.5):
- Functionality  : CRUD operations for Workout, WorkoutEntry, Exercise
- Authentication : register, login, logout, access control
- Data management: model methods, form validation
- Responsiveness : not tested here (use browser DevTools / Lighthouse)
- Usability      : see manual test plan in README

Run with:
    python manage.py test
  or:
    pytest
"""

from datetime import date
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse

from tracker.models import Exercise, Workout, WorkoutEntry
from tracker.forms import WorkoutForm, WorkoutEntryForm, ExerciseForm, RegisterForm


# Custom test client that doesn't store rendered templates (Python 3.14 workaround)
class NoTemplateTraceClient(Client):
    def _handle_template_response(self, response):
        """Override to prevent template context copying which fails on Python 3.14."""
        # Don't store templates/contexts for Python 3.14 compatibility
        return response


# ══════════════════════════════════════════════════════════════
# Model tests
# ══════════════════════════════════════════════════════════════

class ExerciseModelTests(TestCase):
    """Tests for the Exercise model."""

    def test_exercise_str(self):
        """__str__ returns name and category."""
        ex = Exercise(name='Bench Press', category='strength')
        self.assertIn('Bench Press', str(ex))
        self.assertIn('strength', str(ex))

    def test_exercise_ordering(self):
        """Exercises are returned in alphabetical order by name."""
        Exercise.objects.create(name='Squat',      category='strength')
        Exercise.objects.create(name='Bench Press', category='strength')
        names = list(Exercise.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))

    def test_exercise_name_unique(self):
        """Two exercises cannot share the same name."""
        Exercise.objects.create(name='Deadlift', category='strength')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Exercise.objects.create(name='Deadlift', category='cardio')


class WorkoutModelTests(TestCase):
    """Tests for the Workout model and its helper methods."""

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')
        self.exercise = Exercise.objects.create(name='Squat', category='strength')
        self.workout = Workout.objects.create(
            user=self.user,
            name='Leg Day',
            date=date.today(),
        )

    def test_workout_str(self):
        """__str__ contains the workout name and username."""
        self.assertIn('Leg Day', str(self.workout))
        self.assertIn('tester', str(self.workout))

    def test_total_volume_no_entries(self):
        """total_volume returns 0.0 when there are no entries."""
        self.assertEqual(self.workout.total_volume(), 0.0)

    def test_total_volume_with_entries(self):
        """total_volume correctly sums sets × reps × weight."""
        WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise,
            sets=3, reps=10, weight=100,
        )
        WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise,
            sets=2, reps=8, weight=80,
        )
        # (3×10×100) + (2×8×80) = 3000 + 1280 = 4280
        self.assertEqual(self.workout.total_volume(), 4280.0)

    def test_total_volume_bodyweight_excluded(self):
        """Bodyweight entries (weight=None) do not count toward volume."""
        WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise,
            sets=3, reps=10, weight=None,
        )
        self.assertEqual(self.workout.total_volume(), 0.0)

    def test_entry_count(self):
        """entry_count returns the correct number of entries."""
        self.assertEqual(self.workout.entry_count(), 0)
        WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise,
            sets=3, reps=10,
        )
        self.assertEqual(self.workout.entry_count(), 1)


class WorkoutEntryModelTests(TestCase):
    """Tests for the WorkoutEntry model."""

    def setUp(self):
        self.user     = User.objects.create_user(username='tester2', password='testpass123')
        self.exercise = Exercise.objects.create(name='Bench Press', category='strength')
        self.workout  = Workout.objects.create(user=self.user, name='Push Day', date=date.today())

    def test_entry_volume_with_weight(self):
        """volume() returns sets × reps × weight."""
        entry = WorkoutEntry(exercise=self.exercise, workout=self.workout,
                             sets=4, reps=8, weight=60)
        self.assertEqual(entry.volume(), 4 * 8 * 60)

    def test_entry_volume_bodyweight(self):
        """volume() returns None for bodyweight exercises."""
        entry = WorkoutEntry(exercise=self.exercise, workout=self.workout,
                             sets=3, reps=12, weight=None)
        self.assertIsNone(entry.volume())


# ══════════════════════════════════════════════════════════════
# Form validation tests
# ══════════════════════════════════════════════════════════════

class WorkoutFormTests(TestCase):
    """Tests for WorkoutForm validation."""

    def test_valid_form(self):
        """Form is valid with name and date."""
        form = WorkoutForm(data={'name': 'Push Day', 'date': '2025-01-01', 'notes': ''})
        self.assertTrue(form.is_valid())

    def test_missing_name(self):
        """Form is invalid without a name."""
        form = WorkoutForm(data={'name': '', 'date': '2025-01-01'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_missing_date(self):
        """Form is invalid without a date."""
        form = WorkoutForm(data={'name': 'Push Day', 'date': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)


class ExerciseFormTests(TestCase):
    """Tests for ExerciseForm validation."""

    def test_valid_form(self):
        """Form is valid with name and category."""
        form = ExerciseForm(data={
            'name': 'Lunge', 'category': 'strength',
            'muscle_group': 'Legs', 'description': '',
        })
        self.assertTrue(form.is_valid())

    def test_missing_name(self):
        """Form is invalid without a name."""
        form = ExerciseForm(data={'name': '', 'category': 'strength'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class RegisterFormTests(TestCase):
    """Tests for RegisterForm validation."""

    def test_passwords_must_match(self):
        """Form is invalid when passwords do not match."""
        form = RegisterForm(data={
            'username':  'alice',
            'email':     'alice@example.com',
            'password1': 'strongpass123',
            'password2': 'differentpass',
        })
        self.assertFalse(form.is_valid())

    def test_valid_registration(self):
        """Form is valid with matching passwords and valid data."""
        form = RegisterForm(data={
            'username':  'alice',
            'email':     'alice@example.com',
            'password1': 'Str0ngPass!99',
            'password2': 'Str0ngPass!99',
        })
        self.assertTrue(form.is_valid(), form.errors)


# ══════════════════════════════════════════════════════════════
# View / integration tests
# ══════════════════════════════════════════════════════════════

class AuthViewTests(TestCase):
    """Tests for registration, login, and logout views."""

    def setUp(self):
        self.client = NoTemplateTraceClient()

    def test_register_page_loads(self):
        """GET /register/ returns 200."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """GET /login/ returns 200."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        """POST to register creates a user and redirects to dashboard."""
        response = self.client.post(reverse('register'), {
            'username':  'newuser',
            'email':     'new@example.com',
            'password1': 'Str0ngPass!99',
            'password2': 'Str0ngPass!99',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_valid_credentials(self):
        """POST to login with valid credentials redirects to dashboard."""
        User.objects.create_user(username='bob', password='bobpass99!')
        response = self.client.post(reverse('login'), {
            'username': 'bob',
            'password': 'bobpass99!',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_invalid_credentials(self):
        """POST to login with wrong password re-renders the login page."""
        User.objects.create_user(username='bob', password='bobpass99!')
        response = self.client.post(reverse('login'), {
            'username': 'bob',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_redirected_from_dashboard(self):
        """Unauthenticated users are redirected to login from the dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_logout_redirects_to_login(self):
        """POST to logout redirects to the login page."""
        User.objects.create_user(username='logoutuser', password='pass1234!')
        self.client.login(username='logoutuser', password='pass1234!')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class WorkoutCRUDTests(TestCase):
    """Tests for Create, Read, Update, Delete operations on Workout."""

    def setUp(self):
        self.client = NoTemplateTraceClient()
        self.user   = User.objects.create_user(username='fituser', password='fitpass99!')
        self.client.login(username='fituser', password='fitpass99!')
        self.exercise = Exercise.objects.create(name='Press', category='strength')

    # CREATE
    def test_create_workout(self):
        """POST to workout_create creates a workout and redirects to detail."""
        response = self.client.post(reverse('workout_create'), {
            'name': 'Test Workout', 'date': '2025-06-01', 'notes': '',
        })
        self.assertEqual(Workout.objects.filter(user=self.user).count(), 1)
        workout = Workout.objects.get(user=self.user)
        self.assertRedirects(response, reverse('workout_detail', args=[workout.pk]))

    # READ
    def test_workout_list(self):
        """GET /workouts/ returns 200 and shows user's workouts."""
        Workout.objects.create(user=self.user, name='Morning Run', date=date.today())
        response = self.client.get(reverse('workout_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Morning Run')

    def test_workout_detail(self):
        """GET /workouts/<pk>/ returns 200 for an owned workout."""
        workout  = Workout.objects.create(user=self.user, name='Leg Day', date=date.today())
        response = self.client.get(reverse('workout_detail', args=[workout.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leg Day')

    def test_workout_detail_other_user_returns_404(self):
        """A user cannot view another user's workout."""
        other = User.objects.create_user(username='other', password='otherpass99!')
        workout = Workout.objects.create(user=other, name='Secret', date=date.today())
        response = self.client.get(reverse('workout_detail', args=[workout.pk]))
        self.assertEqual(response.status_code, 404)

    # UPDATE
    def test_edit_workout(self):
        """POST to workout_edit updates the workout name."""
        workout = Workout.objects.create(user=self.user, name='Old Name', date=date.today())
        self.client.post(reverse('workout_edit', args=[workout.pk]), {
            'name': 'New Name', 'date': str(date.today()), 'notes': '',
        })
        workout.refresh_from_db()
        self.assertEqual(workout.name, 'New Name')

    # DELETE
    def test_delete_workout(self):
        """POST to workout_delete removes the workout."""
        workout = Workout.objects.create(user=self.user, name='Bye', date=date.today())
        self.client.post(reverse('workout_delete', args=[workout.pk]))
        self.assertFalse(Workout.objects.filter(pk=workout.pk).exists())


class WorkoutEntryCRUDTests(TestCase):
    """Tests for Create, Read, Update, Delete on WorkoutEntry."""

    def setUp(self):
        self.client = NoTemplateTraceClient()
        self.user     = User.objects.create_user(username='entrytester', password='entrypass99!')
        self.client.login(username='entrytester', password='entrypass99!')
        self.exercise = Exercise.objects.create(name='Curl', category='strength')
        self.workout  = Workout.objects.create(user=self.user, name='Arms', date=date.today())

    def test_add_entry(self):
        """POST to entry_add creates a WorkoutEntry."""
        self.client.post(reverse('entry_add', args=[self.workout.pk]), {
            'exercise': self.exercise.pk,
            'sets': 3, 'reps': 12, 'weight': 15, 'notes': '',
        })
        self.assertEqual(self.workout.entries.count(), 1)

    def test_edit_entry(self):
        """POST to entry_edit updates the entry's sets."""
        entry = WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise, sets=3, reps=10)
        self.client.post(reverse('entry_edit', args=[self.workout.pk, entry.pk]), {
            'exercise': self.exercise.pk,
            'sets': 5, 'reps': 10, 'weight': '', 'notes': '',
        })
        entry.refresh_from_db()
        self.assertEqual(entry.sets, 5)

    def test_delete_entry(self):
        """POST to entry_delete removes the WorkoutEntry."""
        entry = WorkoutEntry.objects.create(
            workout=self.workout, exercise=self.exercise, sets=3, reps=10)
        self.client.post(reverse('entry_delete', args=[self.workout.pk, entry.pk]))
        self.assertFalse(WorkoutEntry.objects.filter(pk=entry.pk).exists())


class ExerciseCRUDTests(TestCase):
    """Tests for Create, Read, Update, Delete on Exercise."""

    def setUp(self):
        self.client = NoTemplateTraceClient()
        self.user   = User.objects.create_user(username='exuser', password='expass99!')
        self.client.login(username='exuser', password='expass99!')

    def test_create_exercise(self):
        """POST to exercise_create adds an exercise to the library."""
        self.client.post(reverse('exercise_create'), {
            'name': 'Lunge', 'category': 'strength',
            'muscle_group': 'Legs', 'description': '',
        })
        self.assertTrue(Exercise.objects.filter(name='Lunge').exists())

    def test_exercise_list_view(self):
        """GET /exercises/ returns 200."""
        response = self.client.get(reverse('exercise_list'))
        self.assertEqual(response.status_code, 200)

    def test_exercise_list_filter(self):
        """GET /exercises/?q=bench returns only matching exercises."""
        Exercise.objects.create(name='Bench Press', category='strength')
        Exercise.objects.create(name='Squat',       category='strength')
        response = self.client.get(reverse('exercise_list') + '?q=bench')
        self.assertContains(response, 'Bench Press')
        self.assertNotContains(response, 'Squat')

    def test_edit_exercise(self):
        """POST to exercise_edit updates the exercise name."""
        exercise = Exercise.objects.create(name='Old Exercise', category='cardio')
        self.client.post(reverse('exercise_edit', args=[exercise.pk]), {
            'name': 'New Exercise', 'category': 'cardio',
            'muscle_group': '', 'description': '',
        })
        exercise.refresh_from_db()
        self.assertEqual(exercise.name, 'New Exercise')

    def test_delete_exercise_unused(self):
        """POST to exercise_delete removes an unused exercise."""
        exercise = Exercise.objects.create(name='TempEx', category='cardio')
        self.client.post(reverse('exercise_delete', args=[exercise.pk]))
        self.assertFalse(Exercise.objects.filter(pk=exercise.pk).exists())

    def test_delete_exercise_in_use_blocked(self):
        """An exercise used in a workout cannot be deleted (FK PROTECT)."""
        user     = User.objects.create_user(username='protectuser', password='prot99!')
        exercise = Exercise.objects.create(name='Protected', category='strength')
        workout  = Workout.objects.create(user=user, name='W', date=date.today())
        WorkoutEntry.objects.create(workout=workout, exercise=exercise, sets=1, reps=1)

        self.client.post(reverse('exercise_delete', args=[exercise.pk]))
        # Exercise must still exist
        self.assertTrue(Exercise.objects.filter(pk=exercise.pk).exists())


class DashboardTests(TestCase):
    """Tests for the dashboard view."""

    def setUp(self):
        self.client = NoTemplateTraceClient()
        self.user   = User.objects.create_user(username='dashuser', password='dashpass99!')
        self.client.login(username='dashuser', password='dashpass99!')

    def test_dashboard_loads(self):
        """GET /dashboard/ returns 200."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_username(self):
        """Dashboard greets the logged-in user by username."""
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'dashuser')

    def test_dashboard_stats_with_data(self):
        """Dashboard displays correct workout count."""
        exercise = Exercise.objects.create(name='Press', category='strength')
        for i in range(3):
            w = Workout.objects.create(
                user=self.user, name=f'Workout {i}', date=date.today())
            WorkoutEntry.objects.create(workout=w, exercise=exercise,
                                        sets=3, reps=10, weight=50)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, '3')   # 3 workouts shown in stats

"""
tracker/views.py — All view functions for FitTrack.
"""
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView
from django.db.models import Count, Sum
import csv
import json

from .models import (
    Workout, WorkoutEntry, Exercise,
    BodyWeightEntry, DailyNote, PersonalRecord,
    WorkoutTemplate, WorkoutTemplateItem,
)
from .forms import (
    RegisterForm, LoginForm,
    WorkoutForm, WorkoutEntryForm, ExerciseForm,
    BodyWeightForm, DailyNoteForm,
    WorkoutTemplateForm, WorkoutTemplateItemForm,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _update_personal_record(user, entry, workout):
    """
    Check if a WorkoutEntry beats the user's existing PR for that exercise.
    If so, create or update the PersonalRecord row.
    Returns True if a new PR was set.
    """
    if not entry.weight:
        return False

    pr, created = PersonalRecord.objects.get_or_create(
        user=user,
        exercise=entry.exercise,
        defaults={
            'best_weight':   entry.weight,
            'best_reps':     entry.reps,
            'achieved_date': workout.date,
            'workout':       workout,
        }
    )

    if not created and entry.weight > pr.best_weight:
        pr.best_weight   = entry.weight
        pr.best_reps     = entry.reps
        pr.achieved_date = workout.date
        pr.workout       = workout
        pr.save()
        return True

    return created  # True when first time logging this exercise


# ── Auth ───────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to FitTrack, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next') or '/dashboard/'
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def profile(request):
    return render(request, 'tracker/profile.html', {
        'user_profile': request.user,
    })


@login_required
def profile_delete(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        user.delete()
        logout(request)
        messages.info(request, f'Profile "{username}" has been deleted.')
        return redirect('login')

    return render(request, 'tracker/confirm_delete.html', {
        'object_name': 'your profile',
        'cancel_url': reverse('profile'),
    })

# ── Dashboard ──────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    """
    Main dashboard — stats, recent workouts, streak, today's note, PRs.
    """
    user_workouts = Workout.objects.filter(
        user=request.user
    ).prefetch_related('entries__exercise')

    total_workouts = user_workouts.count()

    monthly_stats = Workout.objects.monthly_stats(request.user)
    monthly_sets = int(monthly_stats.get('total_sets') or 0)
    monthly_workout_count = int(monthly_stats.get('total_workouts') or 0)
    total_entries = int(monthly_stats.get('total_exercises') or 0)

    current_month = timezone.now().strftime('%B %Y')

    streak = Workout.objects.streak(request.user)

    # Today's note (if exists)
    today = timezone.now().date()
    try:
        todays_note = DailyNote.objects.get(user=request.user, date=today)
    except DailyNote.DoesNotExist:
        todays_note = None

    # Top 5 PRs
    top_prs = list(PersonalRecord.objects.filter(
        user=request.user
    ).select_related('exercise').order_by('-best_weight')[:5])

    # Latest bodyweight entry
    latest_bw = BodyWeightEntry.objects.filter(user=request.user).first()

    recent_workouts = list(user_workouts[:5])

    context = {
        'recent_workouts': recent_workouts,
        'total_workouts':  total_workouts,
        'total_entries':   total_entries,
        'monthly_sets':    monthly_sets,
        'monthly_workouts': monthly_workout_count,
        'streak':          streak,
        'todays_note':     todays_note,
        'top_prs':         top_prs,
        'current_month':   current_month,
        'latest_bw':       latest_bw,
        'today':           today,
    }
    return render(request, 'tracker/dashboard.html', context)


# ── Workouts ───────────────────────────────────────────────────────────────

@login_required
def workout_list(request):
    workouts  = Workout.objects.filter(user=request.user).prefetch_related('entries')
    templates = WorkoutTemplate.objects.filter(user=request.user).prefetch_related('items__exercise')
    return render(request, 'tracker/workout_list.html', {
        'workouts': workouts,
        'templates': templates,
    })


class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'tracker/workout_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.template = None
        template_id = request.GET.get('template')
        if template_id:
            self.template = get_object_or_404(WorkoutTemplate, pk=template_id, user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = timezone.now().date()
        if self.template:
            initial['name'] = self.template.name
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        if self.template:
            for item in self.template.items.all():
                WorkoutEntry.objects.create(
                    workout=self.object,
                    exercise=item.exercise,
                    sets=item.sets,
                    reps=item.reps,
                    notes=item.notes,
                )
            messages.success(self.request, f'Workout created from template "{self.template.name}"!')
        else:
            messages.success(self.request, 'Workout created!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': 'New Workout', 'template': self.template})
        return context

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.object.pk})


class WorkoutUpdateView(LoginRequiredMixin, UpdateView):
    model = Workout
    form_class = WorkoutForm
    template_name = 'tracker/workout_form.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Workout'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Workout updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('workout_detail', kwargs={'pk': self.object.pk})


class WorkoutDeleteView(LoginRequiredMixin, DeleteView):
    model = Workout
    template_name = 'tracker/confirm_delete.html'
    success_url = reverse_lazy('workout_list')

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'object_name': self.object.name,
            'cancel_url': reverse('workout_detail', kwargs={'pk': self.object.pk}),
        })
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        messages.info(request, f'"{self.object.name}" deleted.')
        return super().delete(request, *args, **kwargs)


@login_required
def workout_detail(request, pk):
    workout = get_object_or_404(Workout, pk=pk, user=request.user)
    entries = workout.entries.select_related('exercise')
    prs = {pr.exercise_id for pr in PersonalRecord.objects.filter(user=request.user)}
    return render(request, 'tracker/workout_detail.html', {
        'workout': workout,
        'entries': entries,
        'prs':     prs,
    })


@login_required
def workout_export_csv(request):
    """Export all workouts for the current user as a CSV download."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fittrack_workouts.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Workout', 'Exercise', 'Category', 'Sets', 'Reps', 'Weight (kg)', 'Volume (kg)', 'Notes'])

    workouts = Workout.objects.filter(
        user=request.user
    ).prefetch_related('entries__exercise').order_by('date')

    for workout in workouts:
        for entry in workout.entries.all():
            writer.writerow([
                workout.date,
                workout.name,
                entry.exercise.name,
                entry.exercise.category,
                entry.sets,
                entry.reps,
                entry.weight if entry.weight else '',
                entry.volume() if entry.volume() else '',
                entry.notes,
            ])

    return response


# ── Workout Entries ────────────────────────────────────────────────────────

@login_required
def entry_add(request, workout_pk):
    workout = get_object_or_404(Workout, pk=workout_pk, user=request.user)
    if request.method == 'POST':
        form = WorkoutEntryForm(request.POST)
        if form.is_valid():
            entry         = form.save(commit=False)
            entry.workout = workout
            entry.save()
            # Check for PR
            is_pr = _update_personal_record(request.user, entry, workout)
            if is_pr:
                entry.is_pr = True
                entry.save(update_fields=['is_pr'])
                messages.success(request, f'🏆 New PR! {entry.exercise.name} added.')
            else:
                messages.success(request, f'{entry.exercise.name} added.')
            return redirect('workout_detail', pk=workout.pk)
    else:
        form = WorkoutEntryForm()
    return render(request, 'tracker/entry_form.html', {
        'form': form, 'workout': workout, 'title': 'Add Exercise',
    })


@login_required
def entry_edit(request, workout_pk, pk):
    workout = get_object_or_404(Workout, pk=workout_pk, user=request.user)
    entry   = get_object_or_404(WorkoutEntry, pk=pk, workout=workout)
    if request.method == 'POST':
        form = WorkoutEntryForm(request.POST, instance=entry)
        if form.is_valid():
            entry = form.save()
            _update_personal_record(request.user, entry, workout)
            messages.success(request, 'Exercise updated.')
            return redirect('workout_detail', pk=workout.pk)
    else:
        form = WorkoutEntryForm(instance=entry)
    return render(request, 'tracker/entry_form.html', {
        'form': form, 'workout': workout, 'entry': entry, 'title': 'Edit Exercise',
    })


@login_required
def entry_delete(request, workout_pk, pk):
    workout = get_object_or_404(Workout, pk=workout_pk, user=request.user)
    entry   = get_object_or_404(WorkoutEntry, pk=pk, workout=workout)
    if request.method == 'POST':
        entry.delete()
        messages.info(request, 'Exercise removed.')
        return redirect('workout_detail', pk=workout.pk)
    return render(request, 'tracker/confirm_delete.html', {
        'object': entry, 'object_name': entry.exercise.name,
        'cancel_url': f'/workouts/{workout.pk}/',
    })


# ── Exercise Library ───────────────────────────────────────────────────────

@login_required
def exercise_list(request):
    exercises = Exercise.objects.all()
    query     = request.GET.get('q', '').strip()
    category  = request.GET.get('category', '')
    if query:
        exercises = exercises.filter(name__icontains=query)
    if category:
        exercises = exercises.filter(category=category)
    return render(request, 'tracker/exercise_list.html', {
        'exercises':         exercises,
        'query':             query,
        'selected_category': category,
        'categories':        Exercise.CATEGORY_CHOICES,
    })


@login_required
def exercise_create(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save()
            messages.success(request, f'"{exercise.name}" added to library.')
            return redirect('exercise_list')
    else:
        form = ExerciseForm()
    return render(request, 'tracker/exercise_form.html', {'form': form, 'title': 'Add Exercise'})


@login_required
def exercise_edit(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exercise updated.')
            return redirect('exercise_list')
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'tracker/exercise_form.html', {
        'form': form, 'title': 'Edit Exercise', 'exercise': exercise,
    })


@login_required
def exercise_delete(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk)
    if request.method == 'POST':
        try:
            name = exercise.name
            exercise.delete()
            messages.info(request, f'"{name}" deleted.')
        except Exception:
            messages.error(request, 'This exercise is used in workouts and cannot be deleted.')
        return redirect('exercise_list')
    return render(request, 'tracker/confirm_delete.html', {
        'object': exercise, 'object_name': exercise.name, 'cancel_url': '/exercises/',
    })


# ── Progress Charts ────────────────────────────────────────────────────────

@login_required
def progress(request):
    """
    Show progress charts:
    - Bodyweight over time
    - Workout frequency (weekly or monthly)
    - Weight lifted for a chosen exercise over time
    """
    # Bodyweight chart data
    bw_entries = BodyWeightEntry.objects.filter(user=request.user).order_by('date')
    bw_labels  = [str(e.date) for e in bw_entries]
    bw_data    = [float(e.weight) for e in bw_entries]

    # Workout frequency chart data — weekly or monthly view
    freq_view = request.GET.get('freq', 'weekly')  # 'weekly' or 'monthly'
    freq_labels = []
    freq_data = []
    
    all_workouts = Workout.objects.filter(user=request.user).order_by('date')
    
    if freq_view == 'monthly':
        # Group workouts by month
        month_dict = {}
        for workout in all_workouts:
            month_key = workout.date.strftime('%Y-%m')
            month_dict[month_key] = month_dict.get(month_key, 0) + 1
        for month_key in sorted(month_dict.keys()):
            freq_labels.append(month_key)
            freq_data.append(month_dict[month_key])
    else:
        # Group workouts by week (ISO week number)
        week_dict = {}
        for workout in all_workouts:
            iso_year, iso_week, _ = workout.date.isocalendar()
            week_key = f"{iso_year}-W{iso_week:02d}"
            week_dict[week_key] = week_dict.get(week_key, 0) + 1
        for week_key in sorted(week_dict.keys()):
            freq_labels.append(week_key)
            freq_data.append(week_dict[week_key])

    # Exercise progress — user picks an exercise
    selected_ex_id = request.GET.get('exercise', '')
    ex_labels = []
    ex_data = []
    ex_sets_data = []
    ex_latest_weight = None
    ex_latest_sets = None
    selected_exercise = None

    exercises = Exercise.objects.all()

    if selected_ex_id:
        selected_exercise = get_object_or_404(Exercise, pk=selected_ex_id)
        entries = WorkoutEntry.objects.filter(
            workout__user=request.user,
            exercise=selected_exercise,
            weight__isnull=False,
        ).select_related('workout').order_by('workout__date')
        ex_labels      = [str(e.workout.date) for e in entries]
        ex_data        = [float(e.weight) for e in entries]
        ex_sets_data   = [e.sets for e in entries]
        if entries:
            last_entry = entries.last()
            ex_latest_weight = float(last_entry.weight)
            ex_latest_sets = last_entry.sets

    # All PRs
    all_prs = PersonalRecord.objects.filter(
        user=request.user
    ).select_related('exercise').order_by('-best_weight')

    context = {
        'bw_labels':         json.dumps(bw_labels),
        'bw_data':           json.dumps(bw_data),
        'freq_labels':       json.dumps(freq_labels),
        'freq_data':         json.dumps(freq_data),
        'freq_view':         freq_view,
        'ex_labels':         json.dumps(ex_labels),
        'ex_data':           json.dumps(ex_data),
        'ex_sets_data':      json.dumps(ex_sets_data),
        'ex_latest_weight':  ex_latest_weight,
        'ex_latest_sets':    ex_latest_sets,
        'exercises':         exercises,
        'selected_exercise': selected_exercise,
        'selected_ex_id':    selected_ex_id,
        'all_prs':           all_prs,
    }
    return render(request, 'tracker/progress.html', context)


# ── Body Weight ────────────────────────────────────────────────────────────

@login_required
def bodyweight_list(request):
    entries = BodyWeightEntry.objects.filter(user=request.user)
    form    = BodyWeightForm(initial={'date': timezone.now().date()})
    if request.method == 'POST':
        form = BodyWeightForm(request.POST)
        if form.is_valid():
            entry      = form.save(commit=False)
            entry.user = request.user
            # Upsert — update if entry for this date already exists
            BodyWeightEntry.objects.update_or_create(
                user=request.user, date=entry.date,
                defaults={'weight': entry.weight, 'notes': entry.notes}
            )
            messages.success(request, 'Bodyweight logged.')
            return redirect('bodyweight_list')
    return render(request, 'tracker/bodyweight.html', {'entries': entries, 'form': form})


@login_required
def bodyweight_delete(request, pk):
    entry = get_object_or_404(BodyWeightEntry, pk=pk, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.info(request, 'Entry deleted.')
        return redirect('bodyweight_list')
    return render(request, 'tracker/confirm_delete.html', {
        'object': entry, 'object_name': f'{entry.date} — {entry.weight}kg',
        'cancel_url': '/bodyweight/',
    })


# ── Daily Notes ────────────────────────────────────────────────────────────

@login_required
def notes_list(request):
    notes = DailyNote.objects.filter(user=request.user)
    today = timezone.now().date()
    form  = DailyNoteForm(initial={'date': today})
    if request.method == 'POST':
        form = DailyNoteForm(request.POST)
        if form.is_valid():
            note      = form.save(commit=False)
            note.user = request.user
            DailyNote.objects.update_or_create(
                user=request.user, date=note.date,
                defaults={'mood': note.mood, 'content': note.content}
            )
            messages.success(request, 'Note saved.')
            return redirect('notes_list')
    return render(request, 'tracker/notes.html', {'notes': notes, 'form': form})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(DailyNote, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.info(request, 'Note deleted.')
        return redirect('notes_list')
    return render(request, 'tracker/confirm_delete.html', {
        'object': note, 'object_name': f'Note — {note.date}',
        'cancel_url': '/notes/',
    })


# ── Workout Templates ──────────────────────────────────────────────────────

@login_required
def template_list(request):
    templates = WorkoutTemplate.objects.filter(user=request.user).prefetch_related('items__exercise')
    return render(request, 'tracker/template_list.html', {'templates': templates})


@login_required
def template_create(request):
    if request.method == 'POST':
        form = WorkoutTemplateForm(request.POST)
        if form.is_valid():
            template      = form.save(commit=False)
            template.user = request.user
            template.save()
            messages.success(request, f'Template "{template.name}" created.')
            return redirect('template_detail', pk=template.pk)
    else:
        form = WorkoutTemplateForm()
    return render(request, 'tracker/template_form.html', {'form': form, 'title': 'New Template'})


@login_required
def template_detail(request, pk):
    template = get_object_or_404(WorkoutTemplate, pk=pk, user=request.user)
    items    = template.items.select_related('exercise')
    form     = WorkoutTemplateItemForm()
    if request.method == 'POST':
        form = WorkoutTemplateItemForm(request.POST)
        if form.is_valid():
            item          = form.save(commit=False)
            item.template = template
            item.save()
            messages.success(request, f'{item.exercise.name} added to template.')
            return redirect('template_detail', pk=template.pk)
    return render(request, 'tracker/template_detail.html', {
        'template': template, 'items': items, 'form': form,
    })


@login_required
def template_delete(request, pk):
    template = get_object_or_404(WorkoutTemplate, pk=pk, user=request.user)
    if request.method == 'POST':
        name = template.name
        template.delete()
        messages.info(request, f'Template "{name}" deleted.')
        return redirect('template_list')
    return render(request, 'tracker/confirm_delete.html', {
        'object': template, 'object_name': template.name, 'cancel_url': '/templates/',
    })


@login_required
def template_item_delete(request, template_pk, pk):
    template = get_object_or_404(WorkoutTemplate, pk=template_pk, user=request.user)
    item     = get_object_or_404(WorkoutTemplateItem, pk=pk, template=template)
    if request.method == 'POST':
        item.delete()
        messages.info(request, 'Exercise removed from template.')
        return redirect('template_detail', pk=template.pk)
    return render(request, 'tracker/confirm_delete.html', {
        'object': item, 'object_name': item.exercise.name,
        'cancel_url': f'/templates/{template.pk}/',
    })

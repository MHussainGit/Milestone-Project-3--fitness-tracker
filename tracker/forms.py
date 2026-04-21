"""
tracker/forms.py — All Django forms for FitTrack.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    Workout, WorkoutEntry, Exercise,
    BodyWeightEntry, DailyNote,
    WorkoutTemplate, WorkoutTemplateItem,
)


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class RegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class WorkoutForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Workout
        fields = ('name', 'date', 'notes')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Push Day'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class WorkoutEntryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WorkoutEntry
        fields = ('exercise', 'sets', 'reps', 'weight', 'notes')
        widgets = {
            'exercise': forms.Select(),
            'sets': forms.NumberInput(attrs={'min': 1, 'max': 99}),
            'reps': forms.NumberInput(attrs={'min': 1, 'max': 999}),
            'weight': forms.NumberInput(attrs={'min': 0, 'step': '0.5', 'placeholder': 'BW'}),
            'notes': forms.TextInput(attrs={'maxlength': 200, 'placeholder': 'e.g. felt strong'}),
        }

    def clean(self):
        cleaned = super().clean()
        sets = cleaned.get('sets')
        reps = cleaned.get('reps')
        if sets is not None and sets < 1:
            self.add_error('sets', 'Sets must be at least 1.')
        if reps is not None and reps < 1:
            self.add_error('reps', 'Reps must be at least 1.')
        return cleaned


class ExerciseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ('name', 'category', 'muscle_group', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Bulgarian Split Squat'}),
            'category': forms.Select(),
            'muscle_group': forms.Select(),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class BodyWeightForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = BodyWeightEntry
        fields = ('date', 'weight', 'notes')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'min': 0.1, 'step': '0.1', 'placeholder': 'kg'}),
            'notes': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }


class DailyNoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = DailyNote
        fields = ('date', 'mood', 'content')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'mood': forms.Select(),
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'How did you feel today?'}),
        }


class WorkoutTemplateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WorkoutTemplate
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Push Day A'}),
        }


class WorkoutTemplateItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = WorkoutTemplateItem
        fields = ('exercise', 'sets', 'reps', 'notes')
        widgets = {
            'exercise': forms.Select(),
            'sets': forms.NumberInput(attrs={'min': 1}),
            'reps': forms.NumberInput(attrs={'min': 1}),
            'notes': forms.TextInput(attrs={'placeholder': 'Optional'}),
        }

from django.contrib import admin
from .models import Exercise, Workout, WorkoutEntry, BodyWeightEntry, DailyNote, PersonalRecord, WorkoutTemplate, WorkoutTemplateItem

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'muscle_group')
    list_filter  = ('category', 'muscle_group')
    search_fields = ('name',)

class WorkoutEntryInline(admin.TabularInline):
    model  = WorkoutEntry
    extra  = 0
    fields = ('exercise', 'sets', 'reps', 'weight', 'notes', 'is_pr')

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display  = ('name', 'user', 'date')
    list_filter   = ('user',)
    inlines       = [WorkoutEntryInline]

@admin.register(PersonalRecord)
class PRAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'best_weight', 'best_reps', 'achieved_date')

@admin.register(BodyWeightEntry)
class BodyWeightAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weight')

@admin.register(DailyNote)
class DailyNoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood')

class TemplateItemInline(admin.TabularInline):
    model = WorkoutTemplateItem
    extra = 0

@admin.register(WorkoutTemplate)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    inlines      = [TemplateItemInline]

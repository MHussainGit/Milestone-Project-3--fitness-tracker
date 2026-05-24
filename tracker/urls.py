"""tracker URL patterns."""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('dashboard/', views.dashboard,    name='dashboard'),

    # Workouts
    path('workouts/',                  views.workout_list,          name='workout_list'),
    path('workouts/new/',              views.workout_create,               name='workout_create'),
    path('workouts/export/',           views.workout_export_csv,    name='workout_export'),
    path('workouts/<int:pk>/',         views.workout_detail,        name='workout_detail'),
    path('workouts/<int:pk>/edit/',    views.WorkoutUpdateView.as_view(),  name='workout_edit'),
    path('workouts/<int:pk>/delete/',  views.WorkoutDeleteView.as_view(),  name='workout_delete'),

    # Workout entries
    path('workouts/<int:workout_pk>/entries/add/',             views.entry_add,    name='entry_add'),
    path('workouts/<int:workout_pk>/entries/<int:pk>/edit/',   views.entry_edit,   name='entry_edit'),
    path('workouts/<int:workout_pk>/entries/<int:pk>/delete/', views.entry_delete, name='entry_delete'),

    # Exercises
    path('exercises/',                 views.exercise_list,   name='exercise_list'),
    path('exercises/new/',             views.exercise_create, name='exercise_create'),
    path('exercises/<int:pk>/edit/',   views.exercise_edit,   name='exercise_edit'),
    path('exercises/<int:pk>/delete/', views.exercise_delete, name='exercise_delete'),

    # Progress & charts
    path('progress/', views.progress, name='progress'),

    # Bodyweight tracker
    path('bodyweight/',                views.bodyweight_list,   name='bodyweight_list'),
    path('bodyweight/<int:pk>/delete/', views.bodyweight_delete, name='bodyweight_delete'),

    # Daily notes
    path('notes/',                views.notes_list,  name='notes_list'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),

    # Templates
    path('templates/',                                          views.template_list,        name='template_list'),
    path('templates/new/',                                      views.template_create,      name='template_create'),
    path('templates/<int:pk>/',                                 views.template_detail,      name='template_detail'),
    path('templates/<int:pk>/delete/',                          views.template_delete,      name='template_delete'),
    path('templates/<int:template_pk>/items/<int:pk>/delete/',  views.template_item_delete, name='template_item_delete'),

    # User profile
    path('profile/',         views.profile,        name='profile'),
    path('profile/delete/',  views.profile_delete, name='profile_delete'),

    # Password reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(extra_context={'title': 'Reset Password'}),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(extra_context={'title': 'Set New Password'}),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]

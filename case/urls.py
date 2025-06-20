from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home and main pages
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Cases
    path('cases/', views.CaseListView.as_view(), name='case_list'),
    path('cases/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('cases/create/', views.create_case, name='create_case'),
    path('cases/<int:pk>/donate/', views.donate_to_case, name='donate_to_case'),

    # User dashboard
    path('dashboard/', views.user_dashboard, name='dashboard'),
]

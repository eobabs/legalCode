from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.http import JsonResponse

urlpatterns = [
    path('', views.home, name='home' ),

    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('cases/', views.CaseListView.as_view(), name='case_list'),
    path('cases/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('cases/create/', views.create_case, name='create_case'),
    path('cases/<int:pk>/donate/', views.initiate_payment, name='initiate_payment'),

    path('payment/callback/', views.payment_callback, name='payment_callback'),

    path('dashboard/', views.user_dashboard, name='dashboard'),
]

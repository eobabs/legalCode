from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Legal Code API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('case.urls')),
    # path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



"""
URL configuration for legalCode project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path
#
# urlpatterns = [
#     #    path('admin/', admin.site.urls),
# ]
# from django.contrib import admin
# from django.urls import path, include
# from django.contrib.auth import views as auth_views
#
# from case import views
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.home, name='home'),
#     path('register/', views.register_view, name='register'),
#     path('login/', auth_views.LoginView.as_view(), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
#     path('cases/', views.CaseListView.as_view(), name='case_list'),
#     path('cases/<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
#     path('cases/create/', views.create_case, name='create_case'),
#     path('cases/<int:pk>/donate/', views.donate_to_case, name='donate_to_case'),
#     path('dashboard/', views.user_dashboard, name='dashboard'),
# ]
#

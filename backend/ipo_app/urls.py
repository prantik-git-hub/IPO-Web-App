from django.urls import path, reverse
from django.shortcuts import redirect
from . import views
from .views import dashboard_home_view

app_name = "ipo_app"

urlpatterns = [
    # Root redirect
    path(
        '',
        lambda request: redirect(reverse('ipo_app:ipo-list'))
        if request.user.is_authenticated and request.user.is_staff
        else redirect(reverse('admin:login'))
    ),
     path('home/', dashboard_home_view, name='dashboard-home'),
    # Auth
    path('ipo-login/', views.ipo_login_view, name='ipo-login'),
    path('ipo-logout/', views.ipo_logout_view, name='ipo-logout'),

    # IPO views
    path('ipo/', views.ipo_list_view, name='ipo-list'),
    path('ipo/add/', views.add_ipo_view, name='ipo-add'),
    path('ipo/<int:pk>/edit/', views.update_ipo_view, name='ipo-edit'),
    path('ipo/<int:ipo_id>/', views.ipo_detail_view, name='ipo-detail-page'),
    path('ipo/<int:ipo_id>/delete/', views.delete_ipo_view, name='ipo-delete'),

    # API & utility
    path('ipo/api/receive/', views.receive_ipo_data, name='ipo-receive'),
    path('ipo/redirect/add/', views.redirect_to_ipo_add, name='ipo-redirect-add'),
]

# workers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'workers', views.WorkerViewSet, basename='worker')
router.register(r'assignments', views.WorkerAssignmentViewSet, basename='assignment')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'payments', views.PaymentViewSet, basename='payment')

app_name = 'workers'

urlpatterns = [
    path('', include(router.urls)),
]

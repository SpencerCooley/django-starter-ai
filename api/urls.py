
from django.urls import path
from .views import JobView

urlpatterns = [
    path('job/', JobView.as_view(), name='job'),
]

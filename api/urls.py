
from django.urls import path
from .views import JobView, TaskResultView

urlpatterns = [
    path('job/', JobView.as_view(), name='job'),
    path('results/', TaskResultView.as_view(), name='task-results'),
]

from django.urls import path
from .views import analyze_image, summarize_text

urlpatterns = [
    path('analyze/', analyze_image, name='analyze_image'),
    path('summarize/<int:result_id>/', summarize_text, name='summarize_text'),
]
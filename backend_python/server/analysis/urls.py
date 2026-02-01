from django.urls import include, path
from .views import AnalyzeTwitterView
urlpatterns = [
    path('analyze-twitter/', AnalyzeTwitterView.as_view(), name='twitter-analyze'),
    path('get-graph/',),
]
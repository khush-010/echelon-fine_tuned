from django.urls import include, path
from .views import AnalyzeTwitterView, GetGraphView
urlpatterns = [
    path('analyze-twitter/', AnalyzeTwitterView.as_view(), name='twitter-analyze'),
    path('get-graph/',  GetGraphView.as_view(), name='get-graph'),
]
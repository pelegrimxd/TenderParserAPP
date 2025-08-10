from django.urls import path
from .views import TenderCSVToJSONView

urlpatterns = [
    path('tenders-data/', TenderCSVToJSONView.as_view(), name='tenders-data'),
]

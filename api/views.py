import csv
import os
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


class TenderCSVToJSONView(APIView):
    """Ручка API для работы с данными тендеров"""
    def get(self, request):
        csv_path = os.path.join(settings.STATIC_ROOT, 'tenders.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                json_data = list(csv.DictReader(f))
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        return Response(json_data)
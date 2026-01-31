from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .services.twitter_service import fetch_twitter_user
from .services.aggregation import aggregate_twitter_data
from .services.ai_service import generate_response

import os
from django.conf import settings
import json


    
class AnalyzeTwitterView(APIView):

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------
        # Step 1: Fetch Raw API Data
        # ----------------------------------------
        # api_response = fetch_twitter_user(username)
        BASE_DIR = settings.BASE_DIR

        file_path = os.path.join(BASE_DIR, "analysis", "response.json")

        with open(file_path, "r") as f:
            api_response = json.load(f)
        
        if not api_response:
            return Response(
                {"error": "Failed to fetch user data"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ----------------------------------------
        # Step 2: Aggregate & Compute Metrics
        # ----------------------------------------
        dashboard_data = aggregate_twitter_data(api_response)

        if not dashboard_data:
            return Response(
                {"error": "Failed to process user data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ----------------------------------------
        # Step 3: Optional AI Model Analysis
        # (You can remove this if not needed)
        # ----------------------------------------
        

        # ----------------------------------------
        # Step 4: Return Frontend-Ready Response
        # ----------------------------------------
        return Response(dashboard_data, status=status.HTTP_200_OK)

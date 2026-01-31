from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .services.twitter_service import fetch_twitter_user, clean_user_features, fetch_user_tweets
from .services.aggregation import aggregate_twitter_data
from .services.ai_service import generate_response
import pickle
import os
from django.conf import settings
from datetime import datetime, timezone

    
class AnalyzeTwitterView(APIView):

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_api_response = fetch_twitter_user(username)
        # print("Profile API Response:", profile_api_response)
        user_id = profile_api_response["result"]["data"]["user"]["result"]["rest_id"]


        tweets_api_response = fetch_user_tweets(user_id, count=100)
        
        # BASE_DIR = settings.BASE_DIR

        # file_path = os.path.join(BASE_DIR, "analysis", "response.json")

        # with open(file_path, "r") as f:
        #     profile_api_response = json.load(f)
            
        # tweets_file = os.path.join(BASE_DIR, "analysis", "services", "data.json")
        # with open(tweets_file, "r", encoding="utf-8") as f:
        #     tweets_api_response = json.load(f)
        
        if not profile_api_response:
            return Response(
                {"error": "Failed to fetch user data"},
                status=status.HTTP_404_NOT_FOUND
            )
        if not tweets_api_response:
            return Response(
                {"error": "Failed to fetch user tweets"},
                status=status.HTTP_404_NOT_FOUND
            )

        dashboard_data = aggregate_twitter_data(tweets_api_response)
        created_at_str = profile_api_response["result"]["data"]["user"]["result"]["core"]["created_at"]

        account_created = datetime.strptime(
            created_at_str,
            "%a %b %d %H:%M:%S %z %Y"
        )

        dashboard_data["account_age_days"] = (
            datetime.now(timezone.utc) - account_created
        ).days
        if not dashboard_data:
            return Response(
                {"error": "Failed to process user data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        cleaned_data = clean_user_features(profile_api_response)
        parent_dir = os.path.dirname(settings.BASE_DIR)

        model_path = os.path.join(parent_dir, 'profile_classifier.pkl')

        # print("Model Path: ", model_path)
        with open(model_path, 'rb') as f:
            profile_classifier = pickle.load(f)

        prediction = profile_classifier.predict_proba(cleaned_data)
        dashboard_data['ml_prediction'] = prediction
        print("Prediction:", prediction)
        return Response(dashboard_data, status=status.HTTP_200_OK)

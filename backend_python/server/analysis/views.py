from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from .services.twitter_service import fetch_twitter_user, clean_user_features, fetch_user_tweets, clean_tweets_api_response
from .services.aggregation import aggregate_twitter_data
from .services.ai_service import generate_response
import pickle
import os
from django.conf import settings
from datetime import datetime, timezone 
from tensorflow.keras.models import load_model 
import joblib
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

    
class AnalyzeTwitterView(APIView):
    
    def tweet_prediction(self, cleaned_tweets_data, tokenizer, scaler, tweet_model, max_len):
        sum = 0
        for idx in  range(min(len(cleaned_tweets_data),100)):
            text = cleaned_tweets_data[idx][0]

            sequence = tokenizer.texts_to_sequences([text])
            
            text_padded = pad_sequences(sequence, maxlen=max_len)

            num_features = np.array([cleaned_tweets_data[idx][1:]])
            
            num_features = scaler.transform(num_features)
            prediction = tweet_model.predict([text_padded, num_features])
            sum += prediction
            
            print("Tweet Model Prediction", prediction)
        return sum/min(100, len(cleaned_tweets_data))

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
        

        
        print("Profile Response:",profile_api_response)
        created_at_str = profile_api_response["result"]["data"]["user"]["result"]["core"]["created_at"]

        if created_at_str:
            account_created = datetime.strptime(
                created_at_str,
                "%a %b %d %H:%M:%S %z %Y"
            )
            account_age_days = (
                datetime.now(timezone.utc) - account_created
            ).days
        else:
            account_age_days = 0

        dashboard_data = aggregate_twitter_data(
            tweets_api_response,
            account_age_days=account_age_days
        )
        dashboard_data["profile_url"] = (
            profile_api_response["result"]["data"]["user"]["result"]
            .get("avatar", {})
            .get("image_url")
        )
        if not dashboard_data:
            return Response(
                {
                    "error": "Not enough data to analyze",
                    "error_code": "INSUFFICIENT_DATA",
                    "can_analyze": False
                },
                status=HTTPStatus.UNPROCESSABLE_ENTITY
            )
        
        cleaned_user_data = clean_user_features(profile_api_response)
        cleaned_tweets_data = clean_tweets_api_response(tweets_api_response)
        # print("Cleaned User Data:", cleaned_user_data)
        # print("Cleaned Tweets Data:", cleaned_tweets_data)
        dashboard_data['behavior_scores']
        
        parent_dir = os.path.dirname(settings.BASE_DIR)
        model_path = os.path.join(parent_dir, 'profile_classifier.pkl')

        # print("Model Path: ", model_path)
        with open(model_path, 'rb') as f:
            profile_classifier = pickle.load(f)

        prediction = profile_classifier.predict_proba(cleaned_user_data)
        # dashboard_data['ml_prediction'] = prediction[0][0]
        print("Prediction:", prediction)
        
        
        tweet_model_path = os.path.join(parent_dir, 'fake_account_model.h5')
        tokenizer_path = os.path.join(parent_dir, 'tokenizer.pickle')
        scaler_path = os.path.join(parent_dir, 'scaler.pickle')
        tweet_model = load_model(tweet_model_path)
        tokenizer = pickle.load(open(tokenizer_path, "rb"))
        scaler = pickle.load(open(scaler_path, "rb"))
        
        max_len = tweet_model.input[0].shape[1]
        # print("Cleaned Tweet Data", cleaned_tweets_data)
        tweet_prediction=self.tweet_prediction(cleaned_tweets_data, tokenizer, scaler, tweet_model, max_len)
        print("Tweet Prediction Model",tweet_prediction )
        tweet_prediction=1-tweet_prediction
        final_prediction = (prediction[0][0] + tweet_prediction)/2
        dashboard_data['ml_prediction'] = final_prediction

        
        return Response(dashboard_data, status=status.HTTP_200_OK)

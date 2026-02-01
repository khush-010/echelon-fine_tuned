from http import HTTPStatus
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timezone
from django.conf import settings
import os
import json
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import shap
from server.shap_analysis import predict_with_shap
import time

from .services.twitter_service import (
    fetch_twitter_user,
    fetch_user_tweets,
    clean_user_features,
    clean_tweets_api_response,
    get_followers_username,
)
from .services.aggregation import aggregate_twitter_data

from .services.network_graph import build_follower_graph
USE_SIMULATION = False


class AnalyzeTwitterView(APIView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        parent_dir = os.path.dirname(settings.BASE_DIR)
        self.tweet_model = load_model(os.path.join(parent_dir, "fake_account_model.h5"))
        file_path = os.path.join(parent_dir, "shape_background.npy")
        background = np.load(file_path)
        # print("shape",background.shape)
        background = background[np.random.choice(
            background.shape[0], 15, replace=False
        )]

        self.explainer = shap.KernelExplainer(self.shap_predict_fn, background)
        self.tokenizer = pickle.load(open(os.path.join(parent_dir, "tokenizer.pickle"), "rb"))
        self.scaler = pickle.load(open(os.path.join(parent_dir, "scaler.pickle"), "rb"))
        
    def shap_predict_fn(self, X):
        max_len = self.tweet_model.input[0].shape[1]
        X_text = X[:, :max_len].astype(int)
        X_num  = X[:, max_len:]
        return self.tweet_model.predict([X_text, X_num])


    def tweet_prediction(self, cleaned_tweets_data, tokenizer, scaler, tweet_model, max_len):
        total = 0
        count = min(len(cleaned_tweets_data), 100)

        for idx in range(count):
            text = cleaned_tweets_data[idx][0]

            sequence = tokenizer.texts_to_sequences([text])
            text_padded = pad_sequences(sequence, maxlen=max_len)

            num_features = np.array([cleaned_tweets_data[idx][1:]])
            num_features = scaler.transform(num_features)

            prediction = tweet_model.predict([text_padded, num_features], verbose=0)
            total += prediction

        return total / count if count > 0 else 0

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if USE_SIMULATION:
            base_dir = settings.BASE_DIR
            with open(os.path.join(base_dir, "analysis", "response.json")) as f:
                profile_api_response = json.load(f)
            with open(os.path.join(base_dir, "analysis", "services", "data.json")) as f:
                tweets_api_response = json.load(f)
        else:
            profile_api_response = fetch_twitter_user(username)
            if profile_api_response==None:
                return Response(
                    {"error": "Failed to fetch user data"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if (
                not profile_api_response
                or "result" not in profile_api_response
                or "data" not in profile_api_response["result"]
                or "user" not in profile_api_response["result"]["data"]
                or "result" not in profile_api_response["result"]["data"]["user"]
            ):
                return Response(
                    {
                        "error": "User not found",
                        "error_code": "USER_NOT_FOUND",
                        "can_analyze": False
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            user_result = profile_api_response["result"]["data"]["user"]["result"]


            user_id = user_result["rest_id"]

            tweets_api_response = fetch_user_tweets(user_id, count=100)
            if tweets_api_response==None:
                return Response(
                    {"error": "Failed to fetch user tweets"},
                    status=status.HTTP_404_NOT_FOUND
                )

        if (
            not profile_api_response
            or "result" not in profile_api_response
            or "data" not in profile_api_response["result"]
            or "user" not in profile_api_response["result"]["data"]
            or "result" not in profile_api_response["result"]["data"]["user"]
        ):
            return Response(
                {
                    "error": "User not found",
                    "error_code": "USER_NOT_FOUND",
                    "can_analyze": False
                },
                status=status.HTTP_404_NOT_FOUND
            )

        user_result = profile_api_response["result"]["data"]["user"]["result"]


        created_at_str = user_result["core"].get("created_at")

        if created_at_str:
            created_at = datetime.strptime(
                created_at_str,
                "%a %b %d %H:%M:%S %z %Y"
            )
            account_age_days = (
                datetime.now(timezone.utc) - created_at
            ).days
        else:
            account_age_days = 0

        dashboard_data = aggregate_twitter_data(
            tweets_api_response,
            account_age_days=account_age_days
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

        dashboard_data["profile_url"] = (
            user_result.get("avatar", {}).get("image_url")
        )

        tweets_per_day = dashboard_data.get(
            "visual_metrics", {}
        ).get("posts_per_day", 0)

        cleaned_user_data = clean_user_features(
            profile_api_response,
            tweets_per_day
        )

        cleaned_tweets_data = clean_tweets_api_response(
            tweets_api_response
        )
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(curr_dir, "latest.json"), 'w') as f:
            json.dump(cleaned_tweets_data, f)

        parent_dir = os.path.dirname(settings.BASE_DIR)

        with open(os.path.join(parent_dir, "profile_classifier.pkl"), "rb") as f:
            profile_classifier = pickle.load(f)

        profile_prediction = profile_classifier.predict_proba(
            cleaned_user_data
        )[0][0]
        print("Profile Prediction Model",profile_prediction )  
        profile_prediction=1-profile_prediction         
        

        max_len = self.tweet_model.input[0].shape[1]

        tweet_prediction = self.tweet_prediction(
            cleaned_tweets_data,
            self.tokenizer,
            self.scaler,
            self.tweet_model,
            max_len
        )
        print("Tweet Prediction Model",tweet_prediction )
        # tweet_prediction = 1 - tweet_prediction
        dashboard_data['user_id']=user_id
        dashboard_data['username']=username
        dashboard_data["ml_prediction"] = (
            0.4*profile_prediction + 0.6*tweet_prediction
        ) 
        print("Final Prediction",dashboard_data["ml_prediction"] )
        return Response(dashboard_data, status=status.HTTP_200_OK)

    def get(self, request):
    
        # parent_dir = os.path.dirname(settings.BASE_DIR)
        # file_path = os.path.join(parent_dir, "shape_background.npy")
        # background = np.load(file_path)
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        
        with open(os.path.join(curr_dir, "latest.json")) as f:
            cleaned_tweets_data = json.load(f)
    
        max_len = self.tweet_model.input[0].shape[1]
        # sttime=time.time()
        shap_response = predict_with_shap(0, cleaned_tweets_data, self.scaler, self.tokenizer, self.tweet_model, self.explainer, max_len)
        # print("Time taken for SHAP:", time.time() - sttime)
        return Response(shap_response, status=status.HTTP_200_OK)


class GetGraphView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        user_name = request.data.get("user_name")
        print("User ID:", user_id)
        print("User Name:", user_name)
        if not user_id or not user_name:
            return Response(
                {"error": "user_id and user_name are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        response = get_followers_username(user_id)
        
        # Check if get_followers_username returned None or empty
        if response is None:
            return Response(
                {"error": "Could not fetch followers"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        return build_follower_graph(response,user_name)
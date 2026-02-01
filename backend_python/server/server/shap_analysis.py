import time
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import shap

NUM_FEATURES = [
    "retweet_count",
    "reply_count",
    "favorite_count",
    "num_hashtags",
    "num_urls",
    "num_mentions"
]
# def shap_predict_fn(X):
#     X_text = X[:, :max_len].astype(int)
#     X_num  = X[:, max_len:]
#     return model.predict([X_text, X_num])
# background = np.load("shap_background.npy") 
# explainer = shap.KernelExplainer(shap_predict_fn, background)

def predict_with_shap(idx,cleaned_tweets_data,scaler, tokenizer, model, explainer, max_len):

    text = cleaned_tweets_data[idx][0]

    num_features = np.array([
        cleaned_tweets_data[idx][1:]])

    # Scale numeric
    num_features = scaler.transform(num_features)

    # Tokenize & pad
    seq = tokenizer.texts_to_sequences([text])
    text_padded = pad_sequences(seq, maxlen=max_len)

    # Combine
    combined = np.hstack([text_padded, num_features])

    # Prediction
    prob = float(model.predict([text_padded, num_features])[0][0])
    label = "BOT" if prob >= 0.5 else "HUMAN"

    # SHAP explanation
    shap_vals = explainer.shap_values(combined)[0]

    # ---- TEXT SHAP ----
    index_word = {v: k for k, v in tokenizer.word_index.items()}
    text_shap_vals = shap_vals[:max_len]

    text_explanation = [
        {
            "word": index_word.get(tok, "<PAD>"),
            "importance": float(val)
        }
        for tok, val in zip(text_padded[0], text_shap_vals)
        if tok != 0
    ]

    # ---- NUMERIC SHAP ----
    num_shap_vals = shap_vals[max_len:]

    num_explanation = [
        {
            "feature": name,
            "importance": float(val)
        }
        for name, val in zip(NUM_FEATURES, num_shap_vals)
    ]

  
    response = {
        "prediction": label,
        "confidence": prob,
        "text_explanation": sorted(
            text_explanation, key=lambda x: x["importance"], reverse=True
        )[:5],
        "numeric_explanation": sorted(
            num_explanation, key=lambda x: x["importance"], reverse=True
        )[:5]
    }

    return response

#  from sklearn.preprocessing import MinMaxScaler
from flask import Flask, request, jsonify

#  from keras.models import load_model
#  import numpy as np

app = Flask("ESPOL Bike Loans")
#  model = load_model("loans_model.h5")


@app.get("/")
def home():
    return {"message": "Bike loans"}


@app.post("/predict")
def predict_loans():
    try:
        data = request.get_json(force=True)
        preprocessed_data = preprocess_input(data)

        prediction = model.predict(preprocessed_data)
        loans = prediction[0]

        return jsonify(loans)
    except Exception as e:
        return jsonify({"error": str(e)})


def preprocess_data():
    return preprocessed_data

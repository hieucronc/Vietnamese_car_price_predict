import pandas as pd
import numpy as np
import joblib
import datetime
from fastapi import FastAPI, HTTPException

# Khởi tạo FastAPI
app = FastAPI()

# Đọc dữ liệu thông tin xe từ file Excel
def load_car_info(file_path):
    return pd.read_excel(file_path)

# Load mô hình và thông tin xe
MODEL_PATH = "random_forest_model.pkl"
CAR_INFO_PATH = "car_info.xlsx"

model_info = joblib.load(MODEL_PATH)
model = model_info["model"]
car_info = load_car_info(CAR_INFO_PATH)

@app.get("/")
def home():
    return {"message": "Welcome to Car Price Prediction API"}

@app.post("/predict/")
def predict_price(car_name: str, year_of_manufacture: int, mileage: float):
    current_year = datetime.datetime.now().year
    car_age = current_year - year_of_manufacture
    
    car_encoded = car_info.loc[car_info["Car Name"] == car_name, "Car Name Encoded"]
    
    if car_encoded.empty:
        raise HTTPException(status_code=404, detail="Car name not found in database")
    
    car_encoded = int(car_encoded.values[0])
    features = pd.DataFrame([[car_encoded, car_age, mileage]], columns=["Car Name Encoded", "Car Age", "Mileage"])
    
    log_price_pred = model.predict(features)[0]
    predicted_price = np.expm1(log_price_pred)
    
    return {"car_name": car_name, "year_of_manufacture": year_of_manufacture, "mileage": mileage, "predicted_price": f"{predicted_price:,.0f} VNĐ"}

# Chạy API bằng lệnh: uvicorn filename:app --reload

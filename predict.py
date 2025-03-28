import joblib
import pandas as pd
import numpy as np
import datetime

def load_car_info(file_path):
    return pd.read_excel(file_path)

def predict_car_price(model_path, car_info_path):
    model_info = joblib.load(model_path)
    model = model_info["model"]
    car_info = load_car_info(car_info_path)
    
    car_name = input("Nhập tên xe: ")
    year_of_manufacture = int(input("Nhập năm sản xuất: "))
    mileage = float(input("Nhập số km đã đi: "))
    
    current_year = datetime.datetime.now().year
    car_age = current_year - year_of_manufacture
    
    car_encoded = car_info.loc[car_info["Car Name"] == car_name, "Car Name Encoded"]
    
    if car_encoded.empty:
        print("Không tìm thấy thông tin xe trong cơ sở dữ liệu!")
        return
    
    car_encoded = int(car_encoded.values[0])
    
    # Chuyển dữ liệu thành DataFrame có tên cột
    features = pd.DataFrame([[car_encoded, car_age, mileage]], columns=["Car Name Encoded", "Car Age", "Mileage"])
    
    log_price_pred = model.predict(features)[0]
    predicted_price = np.expm1(log_price_pred)
    
    print(f"Giá dự đoán cho {car_name} ({year_of_manufacture}, {mileage} km): {predicted_price:,.0f} VNĐ")


if __name__ == "__main__":
    predict_car_price("random_forest_model.pkl", "car_info.xlsx")

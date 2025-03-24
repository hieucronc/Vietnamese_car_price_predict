import pandas as pd
import joblib
import numpy as np

model = joblib.load("random_forest_car_price_model.pkl")
scaler = joblib.load("scaler.pkl") 
car_info = pd.read_excel("car_info.xlsx")

target_car_name = input("Nhập tên xe: ")
target_year = int(input("Nhập năm sản xuất: "))
target_mileage = int(input("Nhập số km đã đi: "))

target_car_age = 2024 - target_year

car_details = car_info[car_info["Car Name"] == target_car_name]
if car_details.empty:
    print("Không tìm thấy thông tin xe. Vui lòng kiểm tra lại tên xe!")
    exit()

car_details = car_details.iloc[0]

car_data = {
    "Car Age": target_car_age,
    "Mileage": target_mileage,
}

car_data[f"Origin_{car_details['Origin']}"] = 1
car_data[f"Body Type_{car_details['Body Type']}"] = 1
car_data[f"Transmission_{car_details['Transmission']}"] = 1
car_data[f"Engine_{car_details['Engine']}"] = 1

input_df = pd.DataFrame([car_data])

train_columns = joblib.load("train_columns.pkl")  

for col in train_columns:
    if col not in input_df.columns:
        input_df[col] = 0

input_df = input_df[train_columns]

input_df[["Mileage", "Car Age"]] = scaler.transform(input_df[["Mileage", "Car Age"]])

predicted_price_log = model.predict(input_df)[0]
predicted_price = np.expm1(predicted_price_log)  # Chuyển từ log về giá thực tế

print(f"Dự đoán giá xe: {predicted_price:,.0f} VND")

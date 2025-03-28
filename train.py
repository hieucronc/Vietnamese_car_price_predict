import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Đọc dữ liệu từ file CSV
def load_data(file_path):
    df = pd.read_csv(file_path)
    df["Log_Price"] = np.log1p(df["Price"])  # Áp dụng log-transform
    return df

# Đọc dữ liệu thông tin xe từ file Excel
def load_car_info(file_path):
    return pd.read_excel(file_path)

# Huấn luyện mô hình Random Forest
def train_model(X_train, y_train):
    model = RandomForestRegressor(
        n_estimators=300,  # số lượng cây 300
        max_depth=None,  # Cho phép cây phát triển tự do
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model

# Đánh giá mô hình
def evaluate_model(model, X_test, y_test_log, df_test, car_info):
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    y_test = np.expm1(y_test_log)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"MAE: {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²: {r2:.4f}")
    
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r', lw=2)
    plt.xlabel("Giá thực tế")
    plt.ylabel("Giá dự đoán")
    plt.title("So sánh giá thực tế vs dự đoán")
    plt.show()
    
    # Ghép thông tin xe từ car_info vào kết quả dự đoán
    results_df = df_test.copy()
    results_df["Actual Price"] = y_test.values
    results_df["Predicted Price"] = y_pred
    results_df = results_df.merge(car_info, on="Car Name Encoded", how="left")
    
    results_df = results_df[["Car Name", "Car Age", "Mileage", "Actual Price", "Predicted Price"]]
    
    # Xuất kết quả ra file Excel
    results_df.to_excel("car_price_predictions.xlsx", index=False)
    print("Kết quả đã được lưu vào car_price_predictions.xlsx")

if __name__ == "__main__":
    file_path = "processed_car_data.csv"  
    car_info_path = "car_info.xlsx"  # file thông tin xe để lấy thông tin từ code name
    
    df = load_data(file_path)
    car_info = load_car_info(car_info_path)
    
    # Chọn đặc trưng và nhãn đầu ra
    X = df[["Car Name Encoded", "Car Age", "Mileage"]]
    y_log = df["Log_Price"]
    
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    X_train = df_train[["Car Name Encoded", "Car Age", "Mileage"]]
    X_test = df_test[["Car Name Encoded", "Car Age", "Mileage"]]
    y_train_log = df_train["Log_Price"]
    y_test_log = df_test["Log_Price"]
    
    # Huấn luyện mô hình
    model = train_model(X_train, y_train_log)
    
    joblib.dump(model, "random_forest_model.pkl")
    print("Mô hình đã được lưu vào random_forest_model.pkl")
    
    evaluate_model(model, X_test, y_test_log, df_test, car_info)

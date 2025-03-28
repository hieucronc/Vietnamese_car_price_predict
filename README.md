"""# Vietnamese Car Price Prediction 🚗

## Mô tả Dự Án
Dự án này sử dụng mô hình **Random Forest Regressor** để dự đoán giá xe cũ dựa trên các thông tin như:
- Tên xe
- Năm sản xuất
- Số km đã đi (Mileage)

API được xây dựng bằng **FastAPI** để cung cấp dịch vụ dự đoán giá xe thông qua HTTP request.

---

## 🗂️ Cấu Trúc Các File Chính

| File                 | Mô tả |
|----------------------|-------|
| `train2.py`         | Huấn luyện mô hình |
| `predict.py`        | Chạy mô hình đã huấn luyện để dự đoán giá xe |
| `api.py`            | FastAPI để triển khai API dự đoán |
| `car_info.xlsx`     | Thông tin về các xe có trong tập dữ liệu |
| `processed_car_data.csv` | Dữ liệu xe đã qua xử lý |

---

## 🚀 Cách Chạy API

### 1️⃣ Cài đặt thư viện
```bash
pip install -r requirements.txt
```
2️⃣ Chạy API bằng FastAPI
```arduino
uvicorn api:app --reload
```
3️⃣ Kiểm tra API trên trình duyệt
Mở trình duyệt và truy cập:

```arduino
http://127.0.0.1:8000/docs
```
Đây là giao diện Swagger để thử nghiệm API.

📌 Giải Thích api.py
```python
app = FastAPI()
```
✅ Khởi tạo FastAPI để tạo API.

```python
model_info = joblib.load("random_forest_model.pkl")
model = model_info["model"]
car_info = pd.read_excel("car_info.xlsx")
```
✅ Tải mô hình đã huấn luyện và dữ liệu xe.

```python
@app.post("/predict/")
def predict_price(car_name: str, year_of_manufacture: int, mileage: float):
```
✅ Định nghĩa API nhận vào 3 tham số:

car_name: Tên xe

year_of_manufacture: Năm sản xuất

mileage: Số km đã đi

```python
current_year = datetime.datetime.now().year
car_age = current_year - year_of_manufacture
```
✅ Tính tuổi của xe.
```python
car_encoded = car_info.loc[car_info["Car Name"] == car_name, "Car Name Encoded"]
if car_encoded.empty:
    raise HTTPException(status_code=404, detail="Car name not found in database")
```
✅ Kiểm tra xem xe có trong cơ sở dữ liệu không.

```python
features = pd.DataFrame([[car_encoded, car_age, mileage]], columns=["Car Name Encoded", "Car Age", "Mileage"])
log_price_pred = model.predict(features)[0]
predicted_price = np.expm1(log_price_pred)
```
✅ Dự đoán giá xe và chuyển đổi từ log-scale về giá thực tế.

```python
return {"car_name": car_name, "year_of_manufacture": year_of_manufacture, "mileage": mileage, "predicted_price": f"{predicted_price:,.0f} VNĐ"}
```
✅ Trả về kết quả dưới dạng JSON.

📊 Huấn Luyện Mô Hình (train2.py)
1️⃣ Đọc dữ liệu
```python
df = pd.read_csv("processed_car_data.csv")
df.dropna(inplace=True)
df["Log_Price"] = np.log1p(df["Price"])
```
✅ Xóa dữ liệu thiếu, áp dụng log-transform để chuẩn hóa giá xe.

2️⃣ Chia tập dữ liệu train/test
```python
X = df[["Car Name Encoded", "Car Age", "Mileage"]]
y_log = df["Log_Price"]
X_train, X_test, y_train_log, y_test_log = train_test_split(X, y_log, test_size=0.2, random_state=42)
```
✅ Chia dữ liệu 80% train, 20% test.

3️⃣ Huấn luyện mô hình
```python


param_dist = {'n_estimators': [100, 200, 300], 'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4]}
model = RandomForestRegressor(random_state=42, n_jobs=-1)
random_search = RandomizedSearchCV(model, param_dist, n_iter=5, cv=2, scoring='neg_mean_absolute_error', random_state=42)
random_search.fit(X_train, y_train_log)
```
✅ Dùng RandomizedSearchCV để tìm tham số tối ưu.

4️⃣ Lưu mô hình
```python


joblib.dump({"model": model}, "random_forest_model.pkl")
```
✅ Lưu mô hình vào file để sử dụng trong API.


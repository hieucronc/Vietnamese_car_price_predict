import pandas as pd
import os

# Định nghĩa thư mục lưu trữ
output_folder = "post_info_db"
os.makedirs(output_folder, exist_ok=True)

# Đường dẫn đầy đủ đến các file CSV
brands_csv_path = os.path.join(output_folder, "brands.csv")
models_csv_path = os.path.join(output_folder, "models.csv")
versions_csv_path = os.path.join(output_folder, "versions.csv")

# Đọc file Excel
try:
    df = pd.read_excel("post_info_db/car_info_process.xlsx")
except FileNotFoundError:
    print("Lỗi: Không tìm thấy file car_info_process.xlsx")
    exit()

# Khởi tạo các DataFrame để lưu dữ liệu cho từng bảng
brands_df = pd.DataFrame(columns=['id', 'name'])
models_df = pd.DataFrame(columns=['id', 'brand_id', 'name'])
versions_df = pd.DataFrame(columns=['id', 'model_id', 'name', 'origin', 'transmission', 'fuel_type', 'engine_capacity', 'seats', 'car_name_encoded'])

# Biến theo dõi ID
brand_id_counter = 1
model_id_counter = 1
version_id_counter = 1

# Dictionary để lưu trữ tên brand đã xử lý để tránh trùng lặp
processed_brands = {}

# Dictionary để lưu trữ tên model đã xử lý theo brand để tránh trùng lặp
processed_models = {}

# Dictionary để lưu trữ thông tin brand_id, model_id, version_id để thêm vào DataFrame gốc
extracted_ids = []

# Duyệt qua từng dòng của DataFrame gốc
for index, row in df.iterrows():
    # Lấy thông tin cần thiết
    brand_name = row['Brand']
    model_name = row['Model']
    model_version = row['Version']
    car_name_encoded = row['Car Name Encoded']
    origin = row['Origin'].split(': ')[1] if isinstance(row['Origin'], str) and ': ' in row['Origin'] else row['Origin']
    transmission = row['Transmission']
    engine = row['Engine']
    body_type = row['Body Type']

    current_brand_id = None
    current_model_id = None
    current_version_id = version_id_counter

    if brand_name:
        # Xử lý bảng brands
        if brand_name not in processed_brands:
            brands_df = pd.concat([brands_df, pd.DataFrame([{'id': brand_id_counter, 'name': brand_name}])], ignore_index=True)
            processed_brands[brand_name] = brand_id_counter
            current_brand_id = brand_id_counter
            brand_id_counter += 1
        else:
            current_brand_id = processed_brands[brand_name]

        if model_name:
            # Xử lý bảng models
            model_key = (current_brand_id, model_name)
            if model_key not in processed_models:
                models_df = pd.concat([models_df, pd.DataFrame([{'id': model_id_counter, 'brand_id': current_brand_id, 'name': model_name}])], ignore_index=True)
                processed_models[model_key] = model_id_counter
                current_model_id = model_id_counter
                model_id_counter += 1
            else:
                current_model_id = processed_models[model_key]

            # Xử lý bảng versions
            fuel_type_parts = engine.split(' ')
            fuel_type = fuel_type_parts[0] if fuel_type_parts else None
            engine_capacity = None  # Khởi tạo engine_capacity là None

            if fuel_type != "Electric" and len(fuel_type_parts) > 1:
                engine_capacity = ' '.join(fuel_type_parts[1:]).replace('\xa0', ' ')

            # Ước tính số chỗ ngồi
            seats = None
            if isinstance(body_type, str):
                body_type_lower = body_type.lower()
                if 'suv' in body_type_lower:
                    seats = 7
                elif 'crossover' in body_type_lower:
                    seats = 5
                elif 'hatchback' in body_type_lower:
                    seats = 5
                elif 'sedan' in body_type_lower:
                    seats = 5
                elif 'convertible' in body_type_lower or 'cabriolet' in body_type_lower or 'coupe' in body_type_lower:
                    seats = 2

            versions_df = pd.concat([versions_df, pd.DataFrame([{'id': current_version_id, 'model_id': current_model_id, 'name': model_version, 'origin': origin, 'transmission': transmission, 'fuel_type': fuel_type, 'engine_capacity': engine_capacity, 'seats': seats, 'car_name_encoded': car_name_encoded}])], ignore_index=True)

    extracted_ids.append({'Car Name Encoded': car_name_encoded, 'brand_id': current_brand_id, 'model_id': current_model_id, 'version_id': current_version_id})
    version_id_counter += 1

# Ghi các DataFrame vào file CSV trong thư mục post_info_db
brands_df.to_csv(brands_csv_path, index=False)
models_df.to_csv(models_csv_path, index=False)
versions_df.to_csv(versions_csv_path, index=False)

# Tạo DataFrame từ thông tin ID đã trích xuất
extracted_ids_df = pd.DataFrame(extracted_ids)

# Merge DataFrame gốc với thông tin ID đã trích xuất dựa trên 'Car Name Encoded'
merged_df = pd.merge(df, extracted_ids_df, on='Car Name Encoded', how='left')

# Lưu DataFrame đã merge vào file Excel gốc (ghi đè)
try:
    merged_df.to_excel("car_info_process.xlsx", index=False)
    print(f"Đã trích xuất dữ liệu thành công vào các file trong thư mục '{output_folder}'.")
    print("Đã thêm thông tin brand_id, model_id, version_id vào file car_info_process.xlsx")
except Exception as e:
    print(f"Lỗi khi ghi file car_info_process.xlsx: {e}")
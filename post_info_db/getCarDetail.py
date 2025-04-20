import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# Đọc file Excel chứa thông tin xe để map ID
try:
    car_info_df = pd.read_excel("post_info_db/car_info_process.xlsx")
except FileNotFoundError:
    print("Không tìm thấy file car_info_process.xlsx. Vui lòng kiểm tra lại đường dẫn.")
    exit()

df = pd.read_excel("post_info_db/bonbanh_cars.xlsx")  # Đọc toàn bộ file

car_details = []
car_images = []
car_count = 0
output_dir = "post_info_db"  # Lưu trực tiếp vào thư mục post_info_db

# Tên file để lưu dữ liệu chi tiết và ảnh
details_full_filename = os.path.join(output_dir, "bonbanh_car_details.xlsx")
images_full_filename = os.path.join(output_dir, "bonbanh_car_images.xlsx")

def map_car_info(processed_car_name):
    """Tìm kiếm thông tin xe trong car_info_df dựa trên tên xe đã xử lý."""
    matching_row = car_info_df[car_info_df['Car Name'] == processed_car_name]
    if not matching_row.empty:
        return {
            'brand_id': matching_row.iloc[0]['brand_id'],
            'model_id': matching_row.iloc[0]['model_id'],
            'version_id': matching_row.iloc[0]['version_id']
        }
    return None

for index, row in df.iterrows():
    url = row["Link bài đăng"]
    car_count += 1
    print(f"Đang lấy dữ liệu từ xe thứ {car_count}: {url}")

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Lỗi timeout khi lấy dữ liệu từ {url}, bỏ qua...")
        continue
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy dữ liệu từ {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    def extract_info(label):
        for div in soup.find_all(["div"], class_=["row", "row_last"]):
            label_tag = div.find("div", class_="label")
            if label_tag and label in label_tag.text.strip():
                value_tag = div.find("span", class_="inp")
                return value_tag.text.strip() if value_tag else None
        return None

    full_car_name = row["Tên xe"].strip()
    car_name_to_match = full_car_name

    # Loại bỏ 4 chữ số cuối (năm sản xuất) nếu có
    car_name_to_match = re.sub(r'\s*\d{4}$', '', car_name_to_match)

    # Loại bỏ dấu '-' ở cuối string nếu có
    if car_name_to_match.endswith('-'):
        car_name_to_match = car_name_to_match[:-1].strip()

    year = extract_info("Năm sản xuất")
    title = f"{full_car_name}" if full_car_name else None

    description_div = soup.find("div", class_="car_des")
    description_h3 = description_div.find_next("h3") if description_div else None
    description_text = description_h3.find_next("div", class_="des_txt").text.strip() if description_h3 and description_h3.find_next("div", class_="des_txt") else None

    price_str = str(row["Giá xe"])  # Ép kiểu sang chuỗi
    price = None
    if price_str and "Triệu" in price_str:
        try:
            price = float(price_str.replace(" Triệu", "").strip()) * 1000000
        except ValueError:
            print(f"Lỗi chuyển đổi giá trị '{price_str}' sang số.")
            price = None
    elif price_str and "Tỷ" in price_str:
        try:
            price = float(price_str.replace(" Tỷ", "").strip()) * 1000000000
        except ValueError:
            print(f"Lỗi chuyển đổi giá trị '{price_str}' sang số.")
            price = None
    elif price_str.isdigit(): # Nếu chỉ là số, coi như đơn vị là VNĐ
        try:
            price = float(price_str)
        except ValueError:
            print(f"Lỗi chuyển đổi giá trị '{price_str}' sang số.")
            price = None

    odo_str = extract_info("Số Km đã đi")
    odo = None
    if odo_str and "Km" in odo_str:
        try:
            odo = int(odo_str.replace(" Km", "").replace(",", "").strip())
        except ValueError:
            print(f"Lỗi chuyển đổi số km '{odo_str}' sang số.")
            odo = None

    location_parts = soup.find("div", class_="contact-box").find("div", class_="contact-txt").text.split("Địa chỉ:") if soup.find("div", class_="contact-box") and soup.find("div", class_="contact-box").find("div", class_="contact-txt") and "Địa chỉ:" in soup.find("div", class_="contact-box").find("div", class_="contact-txt").text else None
    location = location_parts[1].strip() if location_parts and len(location_parts) > 1 else None

    # Tìm thông tin brand_id, model_id, version_id
    car_info = map_car_info(car_name_to_match)
    brand_id = car_info['brand_id'] if car_info else None
    model_id = car_info['model_id'] if car_info else None
    version_id = car_info['version_id'] if car_info else None

    details = {
        "sale_post_id": car_count,
        "brand_id": brand_id,
        "model_id": model_id,
        "version_id": version_id,
        "title": title,
        "description": description_text,
        "price": price,
        "year": year,
        "odo": odo,
        "location": location,
        "status": "active",
    }
    car_details.append(details)

    # Lấy thông tin ảnh lớn
    image_container = soup.find("div", id="medium_img")
    if image_container:
        image_links = image_container.find_all("a", class_="highslide")
        for img_link in image_links:
            if "href" in img_link.attrs:
                image_url = img_link["href"]
                car_images.append({"sale_post_id": car_count, "image_url": image_url})

    time.sleep(0.2)

# Lưu dữ liệu chi tiết sau khi vòng lặp kết thúc
if car_details:
    df_details = pd.DataFrame(car_details)
    df_details.to_excel(details_full_filename, index=False)
    print(f"Đã lưu dữ liệu chi tiết vào {details_full_filename}")
else:
    print("Không có dữ liệu chi tiết nào để lưu.")

# Lưu dữ liệu ảnh sau khi vòng lặp kết thúc
if car_images:
    df_images = pd.DataFrame(car_images)
    df_images.to_excel(images_full_filename, index=False)
    print(f"Đã lưu dữ liệu ảnh vào {images_full_filename}")
else:
    print("Không có dữ liệu ảnh nào để lưu.")

print("Hoàn tất việc thu thập và lưu dữ liệu.")
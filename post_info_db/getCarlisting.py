import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL gốc
base_url = "https://bonbanh.com/oto-cu-da-qua-su-dung-gia-tu-200-1950-trieu-sf000000100/page," 

# Danh sách lưu dữ liệu
car_list = []

# Số trang cần duyệt (có thể chỉnh sửa)
num_pages = 300  # Thay đổi số trang tùy theo nhu cầu

for page in range(1, num_pages + 1):
    url = f"{base_url}{page}"
    print(f"Đang lấy dữ liệu từ: {url}")
    
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Lỗi khi lấy dữ liệu trang {page}")
        continue
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Tìm danh sách xe
    cars = soup.find_all("li", class_="car-item")
    
    print(f"Tìm thấy {len(cars)} xe trên trang {page}")
    
    for car in cars:
        name_tag = car.find("h3", itemprop="name")
        price_tag = car.find("b", itemprop="price")
        link_tag = car.find("a", itemprop="url")
        
        name = name_tag.text.strip() if name_tag else "N/A"
        price = price_tag["content"] if price_tag else "N/A"
        link = "https://bonbanh.com/" + link_tag["href"] if link_tag else "N/A"
        
        car_list.append({
            "Tên xe": name,
            "Giá xe": price,
            "Link bài đăng": link
        })
    
    # Tránh bị chặn do gửi quá nhiều request
    time.sleep(2)

# Lưu vào file Excel nếu có dữ liệu
if car_list:
    df = pd.DataFrame(car_list)
    df.to_excel("bonbanh_cars.xlsx", index=False)
    print("Dữ liệu đã được lưu vào bonbanh_cars.xlsx")
else:
    print("Không tìm thấy dữ liệu xe nào.")

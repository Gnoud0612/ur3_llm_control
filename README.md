# Điều Khiển Tay Máy Robot UR3 Bằng LLM

**Thông tin sinh viên:**
- **Họ và tên:** Nguyen Tung Duong
- **Mã sinh viên:** 23020732


## 1. Mô tả dự án
Dự án này tích hợp Mô hình Ngôn ngữ Lớn (LLM) thông qua AI Gateway (9Router) để điều khiển cánh tay robot UR3. Hệ thống có khả năng nhận các câu lệnh bằng ngôn ngữ tự nhiên từ người dùng, hiểu ngữ nghĩa (bao gồm việc phân tích mã sinh viên), lập kế hoạch gồm chuỗi các hành động tuần tự và kiểm tra tính hợp lệ của kế hoạch trước khi thực thi.

> **LƯU Ý QUAN TRỌNG:** Phiên bản nộp bài này đang được cấu hình chạy ở **Chế độ Giả lập lệnh (Logic/Mock Mode)**. 
> - **Mục đích:** Tập trung chứng minh tính chính xác tuyệt đối của tầng Logic AI (Khả năng hiểu lệnh, lập kế hoạch của LLM và bộ lọc lỗi Task Validator).
> - **Hành vi:** Các lệnh gắp/thả (`pick`, `place`, `home`) sẽ mô phỏng độ trễ và trả về `SUCCESS` trơn tru trên Terminal mà không cần bật môi trường mô phỏng vật lý Gazebo.

---

## 2. Cấu trúc thư mục (Theo chuẩn yêu cầu)

```text
ur3_llm_control/
├── launch/
│   └── llm_robot.launch.py       # File khởi chạy chính của hệ thống bằng ROS 2 Launch
├── ur3_llm_control/
│   ├── llm_planner.py            # Module gọi API tới LLM để sinh kế hoạch
│   ├── skill_executor.py         # Node thực thi chính, điều phối toàn bộ quá trình
│   ├── robot_skills.py           # Định nghĩa các kỹ năng của robot (pick, place, home)
│   └── task_validator.py         # Bộ lọc an toàn, phát hiện các lệnh sai logic/vùng đích
├── config/
│   ├── scene.yaml                # Định nghĩa tọa độ không gian làm việc (objects, zones, home)
│   └── student_config.yaml       # Thông tin cá nhân và cấu hình sinh viên
└── README.md                     # Tài liệu hướng dẫn sử dụng
```

## 3. Hướng dẫn cài đặt và khởi chạy chi tiết

Bước 1: Cài đặt và biên dịch mã nguồn (Build Workspace)
Mở Terminal và clone repository này vào thư mục src trong workspace ROS 2 của bạn (ví dụ: ~/workspaces/ur_gz/src):
# Tiến hành build package
cd ~/workspaces/ur_gz
colcon build --packages-select ur3_llm_control --symlink-install
source install/setup.bash
# Cập nhật môi trường
source install/setup.bash

Bước 2: Bật AI Gateway (9Router)
Chương trình yêu cầu 9Router để làm cầu nối giao tiếp với LLM. Mở một Terminal mới và chạy:
export NODE_TLS_REJECT_UNAUTHORIZED=0
9router

Bước 3: Khởi chạy Node Điều khiển
Quay lại Terminal ở Bước 1 (đã source môi trường), tiến hành khởi chạy chương trình bằng file Launch:
ros2 run ur3_llm_control executor

## 4. Kịch bản kiểm thử (Test Cases)
Kịch bản 1: Thực thi chuẩn xác theo Mã sinh viên
Lệnh nhập vào: Arrange all objects according to my student ID

Kịch bản 2: Bộ lọc an toàn (Bẫy lỗi vùng đích không tồn tại)
Lệnh nhập vào: Put the red cube in zone D

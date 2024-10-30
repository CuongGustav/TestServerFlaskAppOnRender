# # t.py
# # pip install hezar[vision]
# # pip install vietocr
from hezar.models import Model
from hezar.utils import load_image
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
from PIL import ImageFilter

# Cấu hình và khởi tạo VietOCR
config = Cfg.load_config_from_file('config.yml')  # hoặc sử dụng config mặc định nếu cần
config['weights'] = './transformerocr.pth'  # Đường dẫn tới trọng số đã huấn luyện
config['device'] = 'cpu'  # Sử dụng CPU
detector = Predictor(config)

# Tải mô hình CRAFT để phát hiện vùng chứa văn bản
craft_model = Model.load("hezarai/CRAFT")

# Hàm xử lý ảnh và nhận diện văn bản
# Hàm xử lý ảnh và nhận diện văn bản
def process_image(image, max_size=(600, 338)):  # Thêm tham số max_size


    # Chuyển đổi hình ảnh từ RGBA sang RGB nếu cần
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Thay đổi kích thước hình ảnh
    image.thumbnail(max_size, Image.LANCZOS)  # Giữ nguyên tỉ lệ

    # Định nghĩa chiều cao của hình ảnh
    H = image.size[1]  # Lấy chiều cao của hình ảnh

    # Định nghĩa các vùng cần loại bỏ
    regions_to_remove = [
        (0, 0, 220, 13),           # Vùng góc trái trên
        (0, H - 44, 76, 44),    # Vùng góc trái dưới (tính từ phía dưới lên)
    ]

    # Loại bỏ các vùng xác định
    for (x, y, w, h) in regions_to_remove:
        image.paste((255, 255, 255), (x, y, x + w, y + h))  # Thay thế vùng cần loại bỏ bằng màu trắng

    #Tăng độ sắc nét cho hình ảnh
    image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=0))

    # Dự đoán vùng chứa văn bản bằng CRAFT
    outputs = craft_model.predict(image)
    boxes = outputs[0]["boxes"]

    # Nhóm các boxes theo dòng
    grouped_boxes = group_boxes_by_line(boxes)
    
    # Mở file để ghi kết quả dòng
    result_text = ""
    img_pil = image  # Ảnh đã được mở bằng PIL từ main.py

    # Vòng lặp qua từng dòng
    for line_boxes in grouped_boxes:
        line_boxes = sorted(line_boxes, key=lambda box: box[0])  # Sắp xếp theo tọa độ x

        # Nhận diện văn bản trong từng box
        line_texts = []
        for box in line_boxes:
            x, y, w, h = box[0], box[1], box[2], box[3]

            # Kiểm tra các tọa độ trước khi cắt
            if w > 0 and h > 0:  # Kích thước hợp lệ
                cropped_img = img_pil.crop((x, y, x + w, y + h))

                # Dự đoán văn bản bằng VietOCR
                s = detector.predict(cropped_img, return_prob=False)
                line_texts.append(s)
            else:
                print(f"Invalid box: {box}")  # Ghi lại các hộp không hợp lệ

        result_text += ' '.join(line_texts) + '\n'

    return result_text



# Hàm nhóm các boxes theo dòng
def group_boxes_by_line(boxes, line_threshold=15):
    lines = []
    boxes = sorted(boxes, key=lambda box: box[1])  # Sắp xếp các hộp theo trục y
    current_line = [boxes[0]]
    
    for box in boxes[1:]:
        if abs(box[1] - current_line[-1][1]) < line_threshold:
            current_line.append(box)
        else:
            lines.append(current_line)
            current_line = [box]
    lines.append(current_line)  
    return lines



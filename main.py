import pickle
import base64
import io
import cv2
from PIL import Image
from flask import Flask, Response, request, jsonify
from googletrans import Translator
import os
import time

app = Flask(__name__)

# # Kiểm tra xem mô hình có tồn tại không trước khi nạp
# model = None
# model_file_path = 'model.pkl'

# if os.path.exists(model_file_path):
#     try:
#         with open(model_file_path, 'rb') as model_file:
#             model = pickle.load(model_file)
#         print("Mô hình đã được nạp thành công.")
#     except Exception as e:
#         print(f"Lỗi khi nạp mô hình: {e}")
# else:
#     print("Tệp mô hình không tồn tại. Sẽ sử dụng mô hình giả định.")

# Tạo một instance của Google Translator
translator = Translator()

# Đường dẫn RTSP của camera
rtsp_url = 'rtsp://Cuonggustav@gmail.com:Cuongqb137@@192.168.2.30:554/stream1'

# Tạo video stream từ camera
# Tạo video stream từ camera
def generate_video_stream():
    cap = cv2.VideoCapture(rtsp_url)

    while True:
        success, frame = cap.read()
        if not success:
            print("Không thể đọc khung hình từ camera, đang thử lại...")
            cap.release()  # Giải phóng camera trước khi thử lại
            cap = cv2.VideoCapture(rtsp_url)  # Thử lại kết nối
            continue  # Thử lại vòng lặp
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Nhận dữ liệu hình ảnh từ web client
    data = request.json
    image_data = data['image']

    # Decode hình ảnh từ chuỗi base64
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
    except Exception as e:
        return jsonify({'message': 'Failed to decode image', 'error': str(e)}), 400

    # Chuyển đổi hình ảnh qua mô hình (model.predict)
    result_english = model_predict(image)

    # Dịch văn bản từ tiếng Anh sang tiếng Việt
    result_vietnamese = translator.translate(result_english, src='en', dest='vi').text

    # Trả về kết quả cho web client
    return jsonify({
        'message': 'Image received and processed successfully',  # Thông báo trạng thái
        'english_text': result_english,
        'vietnamese_text': result_vietnamese
    })


def model_predict(image):
    # Thực hiện xử lý hình ảnh và gọi mô hình
    # if model is not None:
    #     # Gọi hàm dự đoán của mô hình của bạn (cần thay thế hàm này với code thực tế)
    #     # result = model.predict(image)
    #     text_result = "Example text from model"  # Giả định kết quả từ mô hình
    # else:
    #     # Nếu mô hình không được nạp, trả về kết quả giả định
    #     text_result = "Model not loaded, using placeholder text."  # Thay thế bằng văn bản bạn muốn trả về
    
    text_result = "This is a placeholder text from the model."  # Văn bản giả định
    return text_result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# main.py
import base64
import os
import io
import cv2
from PIL import Image
from flask import Flask, Response, request, jsonify, render_template
from googletrans import Translator
import time
from flask_cors import CORS  # Thêm vào để xử lý CORS
from t import process_image  # Import hàm xử lý từ t.py

app = Flask(__name__)
CORS(app)

# Tạo một instance của Google Translator
translator = Translator()

# Đường dẫn RTSP của camera
rtsp_url = 'rtsp://Cuonggustav@gmail.com:Cuongqb137@@192.168.2.30:554/stream1'

# Route chính
@app.route('/')
def index():
    return render_template('index.html')

# Tạo video stream từ camera
def generate_video_stream():
    print("Bắt đầu kết nối với camera...")
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Không thể mở kết nối với camera.")
        return

    print("Kết nối thành công. Bắt đầu phát video...")
    while True:
        success, frame = cap.read()
        if not success:
            print("Không thể đọc khung hình từ camera.")
            break
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
    print("Nhận yêu cầu từ client...")
    data = request.json
    print('Nhận dữ liệu từ client:', data)

    if not data or 'image' not in data:
        print("Không có dữ liệu hình ảnh nào được nhận.")
        return jsonify({'message': 'No image data received'}), 400
    
    image_data = data['image']

    # Decode hình ảnh từ chuỗi base64
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        print("Hình ảnh đã được giải mã thành công.")
    except Exception as e:
        print(f'Không thể giải mã hình ảnh: {e}')
        return jsonify({'message': 'Failed to decode image', 'error': str(e)}), 400

    # Gọi hàm xử lý hình ảnh từ t.py
    result_english = process_image(image)
    print("Văn bản tiếng Anh đã nhận diện:", result_english)

    # Dịch văn bản từ tiếng Anh sang tiếng Việt
    result_vietnamese = translator.translate(result_english, src='en', dest='vi').text
    print("Văn bản tiếng Việt đã dịch:", result_vietnamese)

    # Trả về kết quả cho web client
    return jsonify({
        'message': 'Image received and processed successfully',
        'english_text': result_english,
        'vietnamese_text': result_vietnamese
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))  # Lấy cổng từ biến môi trường, mặc định là 5000
#     app.run(host='0.0.0.0', port=port)
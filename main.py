import base64
import io
import cv2
from PIL import Image
from flask import Flask, Response, request, jsonify
from googletrans import Translator
import time
from flask_cors import CORS  # Thêm vào để xử lý CORS

app = Flask(__name__)
CORS(app)  # Kích hoạt CORS

# Tạo một instance của Google Translator
translator = Translator()

# Đường dẫn RTSP của camera
rtsp_url = 'rtsp://Cuonggustav@gmail.com:Cuongqb137@@172.20.10.2:554/stream1'

# Route chính
@app.route('/')
def index():
    return "Hello, this is the main page of the Flask application!"

# Tạo video stream từ camera
def generate_video_stream():
    retry_count = 0  # Đếm số lần thử lại
    max_retries = 5  # Số lần thử lại tối đa

    while True:
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print("Không thể mở camera, kiểm tra lại đường dẫn RTSP.")
            time.sleep(5)  # Đợi 5 giây trước khi thử lại
            continue

        while True:
            success, frame = cap.read()
            if not success:
                retry_count += 1
                print("Không thể đọc khung hình từ camera, đang thử lại...")
                if retry_count >= max_retries:
                    print("Đã thử quá nhiều lần, không thể kết nối đến camera.")
                    cap.release()  # Giải phóng camera
                    break  # Thoát khỏi vòng lặp
                time.sleep(2)  # Đợi 2 giây trước khi thử lại
                cap.release()  # Giải phóng camera trước khi thử lại
                break  # Thoát khỏi vòng lặp để thử lại kết nối
            else:
                retry_count = 0  # Reset retry count khi thành công
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
    print("Nhận yêu cầu từ client...")  # Thêm log
    data = request.json
    print('Nhận dữ liệu từ client:', data)  # In ra dữ liệu nhận được

    if not data or 'image' not in data:
        print("Không có dữ liệu hình ảnh nào được nhận.")
        return jsonify({'message': 'No image data received'}), 400
    
    image_data = data['image']

    # Decode hình ảnh từ chuỗi base64
    try:
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        print("Hình ảnh đã được giải mã thành công.")  # Thêm log
    except Exception as e:
        print(f'Không thể giải mã hình ảnh: {e}')  # Log lỗi
        return jsonify({'message': 'Failed to decode image', 'error': str(e)}), 400

    # Gọi mô hình xử lý hình ảnh
    result_english = model_predict(image)
    print("Văn bản tiếng Anh đã nhận diện:", result_english)  # Thêm log

    # Dịch văn bản từ tiếng Anh sang tiếng Việt
    result_vietnamese = translator.translate(result_english, src='en', dest='vi').text
    print("Văn bản tiếng Việt đã dịch:", result_vietnamese)  # Thêm log

    # Trả về kết quả cho web client
    return jsonify({
        'message': 'Image received and processed successfully',
        'english_text': result_english,
        'vietnamese_text': result_vietnamese
    })

def model_predict(image):
    # Thực hiện xử lý hình ảnh và gọi mô hình
    # Giả định là mô hình nhận diện văn bản từ hình ảnh
    text_result = "This is a placeholder text from the model."  # Văn bản giả định
    return text_result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

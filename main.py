import pickle
import base64
import io
import cv2
from PIL import Image
from flask import Flask, Response, request, jsonify
from googletrans import Translator

app = Flask(__name__)

# Nạp mô hình từ file model.pkl
with open('model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Tạo một instance của Google Translator (hoặc API dịch khác)
translator = Translator()

# Đường dẫn RTSP của camera
rtsp_url = 'rtsp://Cuonggustav@gmail.com:Cuongqb137@@192.168.2.30:554/stream1'

# Tạo video stream từ camera
def generate_video_stream():
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        success, frame = cap.read()
        if not success:
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
    # Ví dụ trả về text từ ảnh (bạn cần thay thế hàm này bằng hàm tương ứng với model của bạn)
    text_result = "Example text from model"  # Thay thế với code thực tế để lấy text từ hình ảnh
    return text_result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import base64
import io
import json
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from t import process_image  # Hàm xử lý từ t.py

app = Flask(__name__)
CORS(app)

# Tên file JSON để lưu kết quả
RESULT_FILE = 'processed_results.json'

def save_to_json(data):
    try:
        with open(RESULT_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Kết quả đã được lưu vào {RESULT_FILE}.")
    except Exception as e:
        print(f"Lỗi khi ghi file JSON: {e}")


def load_from_json():
    try:
        with open(RESULT_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {RESULT_FILE} chưa tồn tại.")
        return None
    except Exception as e:
        print(f"Lỗi khi đọc file JSON: {e}")
        return None


@app.route('/process_image', methods=['POST'])
def process_image_endpoint():
    print("Nhận yêu cầu từ client để xử lý hình ảnh...")

    # Kiểm tra xem client gửi file hoặc Base64
    image = None
    if 'file' in request.files:
        print("Nhận file ảnh từ client.")
        file = request.files['file']
        try:
            # Đọc file ảnh (JPG, PNG)
            image = Image.open(file)
            print(f"Hình ảnh đã được load thành công từ file ({file.filename}).")
        except Exception as e:
            print(f'Lỗi khi đọc file ảnh: {e}')
            return jsonify({'message': 'Error reading file', 'error': str(e)}), 400

    elif 'image' in request.json:
        print("Nhận chuỗi Base64 từ client.")
        try:
            image_data = request.json['image']
            # Decode Base64 và đọc ảnh
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            print("Hình ảnh đã được giải mã thành công từ Base64.")
        except Exception as e:
            print(f'Lỗi khi giải mã Base64: {e}')
            return jsonify({'message': 'Failed to decode Base64 image', 'error': str(e)}), 400
    else:
        print("Không nhận được dữ liệu hình ảnh hợp lệ.")
        return jsonify({'message': 'No valid image data received'}), 400

    # Gọi model xử lý hình ảnh
    try:
        result_english = process_image(image)
        print("Văn bản tiếng Anh đã nhận diện:", result_english)

        result_data = {'english_text': result_english}
        save_to_json(result_data)

    except Exception as e:
        print(f'Lỗi khi xử lý hình ảnh: {e}')
        return jsonify({'message': 'Error processing image', 'error': str(e)}), 500

    return jsonify({'message': 'Image processed successfully', 'english_text': result_english}), 200


@app.route('/get_result', methods=['GET'])
def get_result():
    print("Nhận yêu cầu lấy kết quả đã xử lý...")

    result_data = load_from_json()
    if not result_data:
        print("Không có kết quả nào được lưu.")
        return jsonify({'message': 'No processed results available'}), 404

    return jsonify(result_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

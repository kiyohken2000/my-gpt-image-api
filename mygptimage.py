import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from image_generator import generate_and_encode_image

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST'])
def main():
  try:
    print('関数の開始')
    
    # 受信したテキストを代入
    request_dict = request.get_json()
    recieved_model_name = str(request_dict['model'])
    received_prompt = str(request_dict['prompt'])
    received_negative_prompt = str(request_dict['negative_prompt'])

    base64_image = generate_and_encode_image(
      model=recieved_model_name,
      prompt=received_prompt,
      negative_prompt=received_negative_prompt
    )

    # 結果の出力
    return jsonify({'image': base64_image}), 200

  except Exception as e:
    print('error', e)
    return jsonify({'error': str(e)}), 500
  
if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
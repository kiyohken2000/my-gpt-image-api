import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from image_generator import generate_and_encode_image
from image_uploader import upload_function
from threading import Timer
import asyncio
import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)
CORS(app)

def shutdown_server():
  os._exit(0)

def run_upload_function(base64_image):
  asyncio.run(upload_function(base64_image))

@app.route('/', methods=['POST'])
def main():
  try:
    # タイムスタンプを生成（例：20240705_123456）
    timestamp = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y/%m/%d %H:%M:%S")
    print('関数の開始', timestamp)
    
    # 受信したテキストを代入
    request_dict = request.get_json()
    recieved_model_name = str(request_dict['model'])
    received_prompt = str(request_dict['prompt'])
    received_negative_prompt = str(request_dict['negative_prompt'])
    print('受信したモデル', recieved_model_name)
    print('受信したプロンプト', received_prompt)
    print('受信したネガティブプロンプト', received_negative_prompt)

    base64_image = generate_and_encode_image(
      model=recieved_model_name,
      prompt=received_prompt,
      negative_prompt=received_negative_prompt
    )
    print("Base64エンコードされた画像 (prefixあり):")
    print(base64_image[:100] + "...") # 最初の100文字だけを表示

    # upload_functionを使用して画像をアップロード（非同期関数を同期的に実行）
    run_upload_function(base64_image)
    print("画像のアップロードを開始しました。")

    # 結果の出力
    response = jsonify({'image': base64_image})
    
    # レスポンス送信後にサーバーをシャットダウン
    # Timer(1, shutdown_server).start()
    
    return response, 200

  except Exception as e:
    print('error', e)
    error_response = jsonify({'error': str(e)})
    
    # エラーレスポンス送信後にサーバーをシャットダウン
    Timer(0.1, shutdown_server).start()
    
    return error_response, 500
  
if __name__ == "__main__":
  app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
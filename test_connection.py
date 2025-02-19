from gradio_client import Client

def test_connection():
  try:
    client = Client("retwpay/novaAnimeXL_ilV40HappyValentine")
    print("接続成功")
  except Exception as e:
    print(f"接続エラー: {str(e)}")

if __name__ == "__main__":
  test_connection()
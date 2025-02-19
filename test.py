import asyncio
from image_generator import generate_and_encode_image
from image_uploader import upload_function

async def mygptimage():
  # 画像を生成してBase64エンコード
  model = "retwpay/retwpay-novaAnimeXL_ilV40HappyValentine"
  prompt = "a girl"
  negative_prompt = ""

  base64_image = generate_and_encode_image(model, prompt, negative_prompt)
  print("Base64エンコードされた画像 (prefixあり):")
  print(base64_image[:100] + "...") # 最初の100文字だけを表示

  # 画像をアップロード
  result = await upload_function(
     base64string=base64_image,
     model_name=model,
     prompt=prompt,
     negative_prompt=negative_prompt
  )
  if result:
      print(f"Image URL: {result['imageUrl']}")
      print(f"Viewer URL: {result['viewerUrl']}")
  else:
      print("アップロードに失敗しました。")

# メイン部分
if __name__ == "__main__":
  asyncio.run(mygptimage())
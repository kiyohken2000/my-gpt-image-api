import asyncio
from image_generator import generate_and_encode_image
from image_uploader import upload_function
from ng_word_checker import check_ng_words

async def mygptimage():
  # 画像を生成してBase64エンコード
  model = "retwpay/waiNSFWIllustrious_v110"
  prompt = "a girl"
  negative_prompt = "modern, recent, old, oldest, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured, long body, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, very displeasing, (worst quality, bad quality:1.2), bad anatomy, sketch, jpeg artifacts, signature, watermark, username, signature, simple background, conjoined,bad ai-generated"

  # プロンプトにNGワードが含まれているかチェック
  has_ng_word, found_ng_words = check_ng_words(prompt)
  if has_ng_word:
    error_msg = f"プロンプトにNGワードが含まれています: {', '.join(found_ng_words)}"
    print(error_msg)
    return
  
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
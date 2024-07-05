from image_generator import generate_and_encode_image

def mygptimage():
  # 関数を実行してBase64エンコードされた画像を取得
  model = "votepurchase/votepurchase-7thAnimeXLPonyA_v10"
  prompt = "a girl"
  negative_prompt = "nsfw, (low quality, worst quality:1.2), very displeasing, 3d, watermark, signature, ugly, poorly drawn"

  base64_image = generate_and_encode_image(model, prompt, negative_prompt)
  print("Base64エンコードされた画像 (prefixあり):")
  print(base64_image[:100] + "...") # 最初の100文字だけを表示
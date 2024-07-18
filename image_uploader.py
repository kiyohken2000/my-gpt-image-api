import aiohttp
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Firebase初期化（まだ初期化していない場合）
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def upload_function(base64string, model_name, prompt, negative_prompt):
  try:
    # プレフィックスを削除
    prefix = "data:image/png;base64,"
    if base64string.startswith(prefix):
        base64string = base64string[len(prefix):]

    # Firestoreからkeyを取得
    key_doc = db.collection('key').document('imgbb').get()
    if not key_doc.exists:
      raise Exception("ImgBB key not found in Firestore")
    imgbb_key = key_doc.to_dict()['key']

    url = "https://api.imgbb.com/1/upload"
    params = {
      "key": imgbb_key
    }
    
    data = aiohttp.FormData()
    data.add_field('image', base64string)
    
    async with aiohttp.ClientSession() as session:
      async with session.post(url, data=data, params=params) as response:
        response.raise_for_status()
        data = await response.json()
            
    image_url = data["data"]["url"]
    viewer_url = data["data"]["url_viewer"]
    thumb = data["data"]["thumb"]["url"]

    # Firestoreにデータを保存
    images_ref = db.collection('images')
    new_doc = images_ref.document()
    doc_id = new_doc.id

    new_doc.set({
      'id': doc_id,
      'imageUrl': image_url,
      'viewerUrl': viewer_url,
      'thumb': thumb,
      'modelName': model_name,
      'prompt': prompt,
      'negativePrompt': negative_prompt,
      'createdAt': firestore.SERVER_TIMESTAMP
    })

    print(f"Document successfully written with ID: {doc_id}")
    
    return {"imageUrl": image_url, "viewerUrl": viewer_url, "thumb": thumb}
  
  except Exception as e:
    print(f"upload function error: {e}")
    return None
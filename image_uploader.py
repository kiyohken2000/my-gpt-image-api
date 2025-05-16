import aiohttp
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import base64
import io

# Firebase初期化（まだ初期化していない場合）
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

async def upload_to_imgbb(base64string, imgbb_key):
    """ImgBBにアップロードする関数"""
    try:
        # プレフィックスを削除
        prefix = "data:image/png;base64,"
        if base64string.startswith(prefix):
            base64string = base64string[len(prefix):]

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
        
        return {"imageUrl": image_url, "viewerUrl": viewer_url, "thumb": thumb}
    
    except Exception as e:
        print(f"ImgBB upload error: {e}")
        return None

async def upload_to_catbox(base64string, userhash):
    """catbox.moeにアップロードする関数 (ライブラリなし)"""
    try:
        # プレフィックスを削除
        prefix = "data:image/png;base64,"
        if base64string.startswith(prefix):
            base64string = base64string[len(prefix):]
        
        # base64をバイナリデータに変換
        binary_data = base64.b64decode(base64string)
        
        url = "https://catbox.moe/user/api.php"
        
        # FormDataを作成
        data = aiohttp.FormData()
        data.add_field('reqtype', 'fileupload')
        # ユーザーハッシュを追加 (認証付きアップロード)
        data.add_field('userhash', userhash)
        # ファイル名を適当に設定
        data.add_field('fileToUpload', io.BytesIO(binary_data), filename='generated_image.png', content_type='image/png')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
                # catboxは単純にURLの文字列を返す
                image_url = await response.text()
                
        # catboxはサムネイルやビューアーURLなどを別途提供しないので、同じURLを使用
        return {"imageUrl": image_url, "viewerUrl": image_url, "thumb": image_url}
    
    except Exception as e:
        print(f"Catbox upload error: {e}")
        return None

async def upload_function(base64string, model_name, prompt, negative_prompt):
    try:
        # ImgBBのkeyをFirestoreから取得
        key_doc = db.collection('key').document('imgbb').get()
        if not key_doc.exists:
            raise Exception("ImgBB key not found in Firestore")
        imgbb_key = key_doc.to_dict()['key']
        
        # catboxのuserhashをFirestoreから取得 (なければデフォルト値を使用)
        catbox_doc = db.collection('key').document('catbox').get()
        catbox_userhash = '29b715e9a63037b830a7a6e7f'
        if catbox_doc.exists:
            catbox_data = catbox_doc.to_dict()
            if 'userhash' in catbox_data:
                catbox_userhash = catbox_data['userhash']
        
        # まずImgBBにアップロード試行
        upload_result = await upload_to_imgbb(base64string, imgbb_key)
        
        # ImgBBアップロード失敗した場合はcatboxにアップロード試行
        if upload_result is None:
            print("ImgBB upload failed, trying catbox.moe...")
            upload_result = await upload_to_catbox(base64string, catbox_userhash)
            
            # catboxも失敗した場合
            if upload_result is None:
                print("Both ImgBB and catbox uploads failed")
                return None
        
        # アップロード先に関わらず、Firestoreにデータを保存
        image_url = upload_result["imageUrl"]
        viewer_url = upload_result["viewerUrl"] 
        thumb = upload_result["thumb"]

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
            'createdAt': firestore.SERVER_TIMESTAMP,
            'like': 0,
            'dislike': 0,
        })

        print(f"Document successfully written with ID: {doc_id}")
        
        return upload_result
    
    except Exception as e:
        print(f"upload function error: {e}")
        return None
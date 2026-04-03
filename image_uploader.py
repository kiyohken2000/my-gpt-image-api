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

TADAUP_API_KEY = "AoLU ets7 2zh3 gvqc cTEe BHfp"

async def upload_to_tadaup(base64string):
    """ただのうｐろだにアップロードする関数"""
    try:
        # プレフィックスを削除
        prefix = "data:image/png;base64,"
        if base64string.startswith(prefix):
            base64string = base64string[len(prefix):]

        # base64をバイナリデータに変換
        binary_data = base64.b64decode(base64string)

        url = "https://tadaup.jp/wp-json/custom/v1/upload"
        auth = aiohttp.BasicAuth("API", TADAUP_API_KEY)

        data = aiohttp.FormData()
        data.add_field('file[]', io.BytesIO(binary_data), filename='image.png', content_type='image/png')
        data.add_field('r18', 'yes')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, auth=auth) as response:
                response.raise_for_status()
                result = await response.json()

        if not result.get("success"):
            raise Exception(f"Upload failed: {result}")

        image_url = result["source_url"]

        return {"imageUrl": image_url, "viewerUrl": image_url, "thumb": image_url}

    except Exception as e:
        print(f"Tadaup upload error: {e}")
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
        # catboxのuserhashをFirestoreから取得 (なければデフォルト値を使用)
        catbox_doc = db.collection('key').document('catbox').get()
        catbox_userhash = '29b715e9a63037b830a7a6e7f'
        if catbox_doc.exists:
            catbox_data = catbox_doc.to_dict()
            if 'userhash' in catbox_data:
                catbox_userhash = catbox_data['userhash']

        # まずただのうｐろだにアップロード試行
        upload_result = await upload_to_tadaup(base64string)

        # ただのうｐろだ失敗した場合はcatboxにアップロード試行
        if upload_result is None:
            print("Tadaup upload failed, trying catbox.moe...")
            upload_result = await upload_to_catbox(base64string, catbox_userhash)

            # catboxも失敗した場合
            if upload_result is None:
                print("Both Tadaup and catbox uploads failed")
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
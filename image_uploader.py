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


def _base64_to_binary(base64string):
    """data URIのプレフィックスを除去してバイナリデータに変換する"""
    prefix = "data:image/png;base64,"
    if base64string.startswith(prefix):
        base64string = base64string[len(prefix):]
    return base64.b64decode(base64string)


async def upload_to_imgpile(base64string, api_key):
    """imgpile (imgpile.com) にアップロードする関数"""
    try:
        binary_data = _base64_to_binary(base64string)

        # 新API: 生バイトを POST /uploads に送る（multipartではなく --data-binary 相当）
        url = "https://imgpile.com/uploads"
        headers = {"Authorization": f"Bearer {api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=binary_data, headers=headers) as response:
                response.raise_for_status()
                result = await response.json()

        # レスポンスにURLが含まれるのでそのまま使う（無料プランはPNG→WebP再エンコードされるため拡張子は自前で組まない）
        data = result["data"]
        urls = data["urls"]

        image_url = urls["original"]
        viewer_url = data["pageUrl"]
        thumb = urls.get("thumb") or urls.get("xs")

        return {"imageUrl": image_url, "viewerUrl": viewer_url, "thumb": thumb}

    except Exception as e:
        print(f"imgpile upload error: {e}")
        return None


async def upload_to_imge(base64string, api_key):
    """im.ge (im.ge) にアップロードする関数"""
    try:
        binary_data = _base64_to_binary(base64string)

        url = "https://im.ge/api/v1/upload"
        headers = {"Authorization": f"Bearer {api_key}"}

        data = aiohttp.FormData()
        data.add_field('file', io.BytesIO(binary_data), filename='generated_image.png', content_type='image/png')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                response.raise_for_status()
                result = await response.json()

        data_dict = result["data"]
        image_url = data_dict.get("direct_url") or data_dict["image"]["image"]["url"]
        viewer_url = data_dict.get("viewer_url") or data_dict.get("url_viewer") or image_url
        thumb = data_dict.get("thumb_url") or image_url

        return {"imageUrl": image_url, "viewerUrl": viewer_url, "thumb": thumb}

    except Exception as e:
        print(f"im.ge upload error: {e}")
        return None


async def upload_to_imghippo(base64string, api_key):
    """Imghippo (imghippo.com) にアップロードする関数"""
    try:
        binary_data = _base64_to_binary(base64string)

        url = "https://api.imghippo.com/v1/upload"

        data = aiohttp.FormData()
        data.add_field('api_key', api_key)
        data.add_field('title', 'generated_image')
        data.add_field('file', io.BytesIO(binary_data), filename='generated_image.png', content_type='image/png')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response.raise_for_status()
                result = await response.json()

        if not result.get("success"):
            raise Exception(f"Upload failed: {result}")

        data_dict = result["data"]
        image_url = data_dict["url"]
        viewer_url = data_dict.get("view_url", image_url)

        # Imghippoはサムネイルを別途提供しないので同じURLを使用
        return {"imageUrl": image_url, "viewerUrl": viewer_url, "thumb": image_url}

    except Exception as e:
        print(f"Imghippo upload error: {e}")
        return None


async def upload_to_catbox(base64string, userhash):
    """catbox.moeにアップロードする関数 (ライブラリなし)"""
    try:
        binary_data = _base64_to_binary(base64string)

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


def _get_key_doc(doc_name):
    """Firestoreの key コレクションからドキュメントを取得する (なければ空dict)"""
    doc = db.collection('key').document(doc_name).get()
    if doc.exists:
        return doc.to_dict() or {}
    return {}


async def upload_function(base64string, model_name, prompt, negative_prompt):
    try:
        # 各アップローダのAPIキーをFirestoreから取得
        imgpile_key = _get_key_doc('imgpile').get('key')
        imge_key = _get_key_doc('imge').get('key')
        imghippo_key = _get_key_doc('imghippo').get('key')

        # catboxのuserhashをFirestoreから取得 (なければデフォルト値を使用)
        catbox_userhash = _get_key_doc('catbox').get('userhash', '29b715e9a63037b830a7a6e7f')

        upload_result = None

        # imgpile → im.ge → Imghippo → catbox の順にアップロードを試行
        if imgpile_key:
            upload_result = await upload_to_imgpile(base64string, imgpile_key)

        if upload_result is None and imge_key:
            print("imgpile upload failed, trying im.ge...")
            upload_result = await upload_to_imge(base64string, imge_key)

        if upload_result is None and imghippo_key:
            print("im.ge upload failed, trying Imghippo...")
            upload_result = await upload_to_imghippo(base64string, imghippo_key)

        if upload_result is None:
            print("Imghippo upload failed, trying catbox.moe...")
            upload_result = await upload_to_catbox(base64string, catbox_userhash)

        # すべて失敗した場合
        if upload_result is None:
            print("All uploads failed")
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

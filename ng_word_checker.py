import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Firebase初期化（まだ初期化していない場合）
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

def check_ng_words(prompt):
    """
    プロンプトがFirestoreに保存されているNGワードを含むかチェックする
    戻り値: (bool, list) - (NGワードが含まれるか, 見つかったNGワードのリスト)
    """
    try:
        db = initialize_firebase()
        
        # FirestoreからNGワードを取得
        words_ref = db.collection('ngwords').document('words')
        words_doc = words_ref.get()
        
        if not words_doc.exists:
            print("NGワードのドキュメントが見つかりません")
            return False, []
            
        ng_words = words_doc.to_dict().get('word_list', [])
        found_ng_words = []
        
        # プロンプト内にNGワードが含まれているかチェック
        for word in ng_words:
            if word.lower() in prompt.lower():
                found_ng_words.append(word)
                
        return len(found_ng_words) > 0, found_ng_words
    except Exception as e:
        print(f"NGワードのチェック中にエラーが発生しました: {e}")
        return False, []
import gradio_client
import gradio_client.utils
from gradio_client import Client
import os
import datetime
import base64

# サーバー側と同様のモンキーパッチをクライアント側にも適用
old_get_type = gradio_client.utils.get_type
def new_get_type(schema):
    if isinstance(schema, bool):
        return "bool"
    return old_get_type(schema)

gradio_client.utils.get_type = new_get_type

# _json_schema_to_python_typeの修正も追加
old_json_schema_to_python_type = gradio_client.utils._json_schema_to_python_type
def new_json_schema_to_python_type(schema, defs=None):
    if isinstance(schema, bool):
        return "bool"
    try:
        return old_json_schema_to_python_type(schema, defs)
    except Exception as e:
        # エラーが発生した場合は汎用的な型を返す
        return "any"

gradio_client.utils._json_schema_to_python_type = new_json_schema_to_python_type

def generate_and_encode_image(model, prompt, negative_prompt):
    client = Client(model)
    result = client.predict(
        prompt=prompt,
        negative_prompt=negative_prompt,
        seed=0,
        randomize_seed=True,
        width=1024,
        height=1024,
        guidance_scale=7,
        num_inference_steps=28,
        api_name="/infer"
    )

    # 元のファイルパスを取得
    original_path = result

    # タイムスタンプを生成（例：20240705_123456）
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 新しいファイル名を生成（例：20240705_123456.png）
    new_filename = f"{timestamp}.png"

    # 現在の.pyファイルのディレクトリを取得
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 新しいファイルパスを生成
    new_path = os.path.join(current_directory, new_filename)

    # ファイルをコピーして名前を変更
    with open(original_path, 'rb') as f_in, open(new_path, 'wb') as f_out:
        f_out.write(f_in.read())

    print(f"画像が保存されました: {new_path}")

    # 画像をBase64エンコード
    with open(new_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # prefixを追加
    encoded_string_with_prefix = f"data:image/png;base64,{encoded_string}"

    # 元のファイルを削除
    os.remove(original_path)

    # 新しいファイルを削除（必要に応じてコメントアウトしてください）
    os.remove(new_path)

    return encoded_string_with_prefix
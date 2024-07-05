# Huggingface Spaces API

[Huggingface Spaces](https://huggingface.co/votepurchase)をウェブAPIで使えるようにした

## 使用方法

```
curl -X POST \
  https://mygpt-image-api-omc3n2et7a-an.a.run.app \
  -H "Content-Type: application/json" \
  -d '{
    "model": "votepurchase/votepurchase-7thAnimeXLPonyA_v10",
    "prompt": "a girl",
    "negative_prompt": "nsfw, (low quality, worst quality:1.2), very displeasing, 3d, watermark, signature, ugly, poorly drawn"
  }'
```

## レスポンス

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```
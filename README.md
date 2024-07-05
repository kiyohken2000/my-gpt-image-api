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

使えるモデル

- 実写系
  - votepurchase/votepurchase-juggernautXL_hyper_8step_sfw
  - votepurchase/NSFW-gen-v2
- 実写系(Pony)
  - votepurchase/votepurchase-waiREALCN_v10
  - votepurchase/votepurchase-waiREALMIX_v70
- アニメ系
  - votepurchase/votepurchase-animagine-xl-3.1
  - votepurchase/votepurchase-AnythingXL_xl
- アニメ系(Pony)
  - votepurchase/votepurchase-ponyDiffusionV6XL
  - votepurchase/votepurchase-7thAnimeXLPonyA_v10
- フィギュア
  - votepurchase/votepurchase-PVCStyleModelMovable_beta27Realistic
- フィギュア(Pony)
  - votepurchase/votepurchase-PVCStyleModelMovable_pony151

## レスポンス

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```
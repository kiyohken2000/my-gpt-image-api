import aiohttp

async def upload_function(base64string):
  try:
    # プレフィックスを削除
    prefix = "data:image/png;base64,"
    if base64string.startswith(prefix):
        base64string = base64string[len(prefix):]
    url = "https://api.imgbb.com/1/upload"
    params = {
      "key": "6d613e2bff8d8fdb6982f6258703d709"
    }
    
    data = aiohttp.FormData()
    data.add_field('image', base64string)
    
    async with aiohttp.ClientSession() as session:
      async with session.post(url, data=data, params=params) as response:
        response.raise_for_status()
        data = await response.json()
            
    image_url = data["data"]["url"]
    viewer_url = data["data"]["url_viewer"]
    
    return {"imageUrl": image_url, "viewerUrl": viewer_url}
  
  except Exception as e:
    print(f"upload function error: {e}")
    return None
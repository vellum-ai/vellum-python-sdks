import requests
import json
import os
import time

def post_linkedin(
    post_text: str,
    video_script: str,
    image_urls: list[str] = None,
) -> str:
    # access token valid for 2 months
    ACCESS_TOKEN = "AQUx0A37biltL7DfV0EgSYgguIfuZOdEkWW3cdc4yihW1pQjvSKfug0lDVMpcK0xcTe8nOZcysMrygy5AmOrVAecwJ8ec7SKI0yMc0Gw8cgyai7ier65sfauX4D2AEdGPbRehvipaHGQJWNHRv9R7AoOxK9_mK1T-N0CLVoRhEXz9UShWeWgBC2o2tI2poZFdSMCHzZZEr6HliCxha8c20JY7uIc_2OZIIhbNBS0QOqjVM3rEorA5O5YlYVat7w3vvaNTI88FsE5zUvkNgFBuGI-q-D1t8_9WQ21cwvhaAxHaTMY2Pb7AxbhA-kopAPzjG5cZ2utpN82dJT4pvrkKt-HMK19PA"
    # sub of the user
    user_data = None
    primary_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    try:
        response = requests.get("https://api.linkedin.com/v2/userinfo", headers=primary_headers)
        response.raise_for_status()
        user_data = response.json()
        print(f"User Data: {user_data}")
    except requests.exceptions.RequestException as e:
        return f"❌ An error occurred while fetching user data: {e}"
    if not user_data:
        return "❌ User data is not available or does not contain 'id'."
    SUB_VALUE = user_data.get("sub")
    print(f"User SUB Value: {SUB_VALUE}")
    api_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    video_asset = None
    if (video_script):
        video_post_data = {
            "registerUploadRequest": {
                "recipes": [
                    "urn:li:digitalmediaRecipe:feedshare-video"
                ],
                "owner": f"urn:li:person:{SUB_VALUE}",
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }
        try:
            response = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, data=json.dumps(video_post_data))
            response.raise_for_status()
            res_video_data = response.json()
            upload_url, video_asset = res_video_data.get("value").get("uploadMechanism").get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest").get("uploadUrl"), res_video_data.get("value").get("asset")
            
            captions_url = "https://api.captions.ai/api/ads"
            captions_headers = {
                "x-api-key": os.getenv("CAPTIONS_API_KEY"),
                "Content-Type": "application/json"
            }
            captions_payload = None
            if image_urls and len(image_urls) > 0:
                captions_payload = {
                    "script": video_script,
                    "creatorName": "Kate",
                    "mediaUrls": image_urls,
                }
            else:
                captions_payload = {
                    "script": video_script,
                    "creatorName": "Kate",
                    "mediaUrls": [ "https://gw42iab886.ufs.sh/f/ixsAdYLYnHROGSzz5vnLWRkTKZGDdCNyYuv5gEpi7JbcjAfz" ],
                }
            captions_response = requests.request("POST", f"{captions_url}/submit", json=captions_payload, headers=captions_headers)
            operationId = captions_response.json().get("operationId")
            captions_payload = {
                "operationId": operationId,
            }
            json_response = None
            video_binary_data = None
            video_content_type = None
            try:
                while True:
                    response = requests.request("POST", f"{captions_url}/poll", json=captions_payload, headers=captions_headers)
                    json_response = response.json()
                    print(f"Captions Response: {json_response}")
                    if "progress" not in json_response:
                        raise Exception("Invalid response format, 'state' key not found")
                    time.sleep(60)
            except Exception as e:
                if json_response is not None:
                    response = requests.get(json_response["url"], stream=True)
                    video_binary_data = response.content
                    video_content_type = response.headers.get('Content-Type')
            specific_headers = {
                'Authorization': f'Bearer {ACCESS_TOKEN}',
                'Content-Type': video_content_type
            }
            put_response = requests.put(
                upload_url,
                headers=specific_headers,
                data=video_binary_data,
                timeout=30
            )
            put_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return f"❌ An error occurred in video upload: {e}"
    post_data = None
    if video_script and video_asset:
        post_data = {
            "author": f"urn:li:person:{SUB_VALUE}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "VIDEO",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "Main Video"
                            },
                            "media": video_asset,
                            "title": {
                                "text": "Main Video Text"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    else:
        post_data = {
            "author": f"urn:li:person:{SUB_VALUE}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    print(f"Post Data: {post_data}")
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(post_data))
        response.raise_for_status()
        return f"✅ Success! Post was created. Status Code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error occured: {e}"
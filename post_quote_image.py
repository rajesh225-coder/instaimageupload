import cloudinary
import cloudinary.api
import os
import requests
import random
import time

# --- Cloudinary Configuration ---
# Fetch Cloudinary credentials from environment variables (GitHub Secrets)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# --- Instagram Configuration ---
# Fetch Instagram credentials from environment variables (GitHub Secrets)
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.environ.get("INSTAGRAM_PAGE_ID")

# --- Facebook Configuration ---
# Fetch Facebook credentials from environment variables (GitHub Secrets)
FACEBOOK_PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")


def get_resources_from_cloudinary_folder(folder_name, resource_type):
    """
    Fetches resource URLs (images) from a specified Cloudinary folder.
    """
    try:
        if not cloudinary.config().cloud_name or \
           not cloudinary.config().api_key or \
           not cloudinary.config().api_secret:
            print("Error: Cloudinary credentials not set in environment variables.")
            return []

        result = cloudinary.api.resources(
            type="upload",
            resource_type=resource_type,
            prefix=f"{folder_name}/",
            max_results=500
        )
        resource_urls = [resource['secure_url'] for resource in result.get('resources', [])]
        print(f"Successfully fetched {len(resource_urls)} {resource_type}s from Cloudinary folder '{folder_name}'.")
        return resource_urls
    except Exception as e:
        print(f"Error fetching {resource_type}s from Cloudinary: {e}")
        return []


def upload_image_to_instagram_feed(image_url, caption):
    """
    Uploads a single image to Instagram feed.
    No 'media_type' parameter is used for image feed posts.
    """
    if not INSTAGRAM_ACCESS_TOKEN:
        print("Error: Instagram access token not configured in environment variables.")
        return False
    if not INSTAGRAM_PAGE_ID:
        print("Error: Instagram page ID not configured in environment variables.")
        return False

    try:
        print(f"\n--- Starting Instagram Feed Image Upload Process ---")
        print(f"Creating Instagram media container for image: {image_url}")

        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media"
        container_payload = {
            'image_url': image_url,
            'caption': caption,
            'access_token': INSTAGRAM_ACCESS_TOKEN,
            'share_to_feed': True # Ensure it appears on the profile grid
        }
        # Explicitly set headers for content type (can sometimes help with picky APIs)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(container_url, data=container_payload, headers=headers)
        container_data = response.json()

        if 'id' not in container_data:
            print(f"Error creating Instagram feed container. Response: {container_data}")
            if 'error' in container_data and 'error_user_msg' in container_data['error']:
                print(f"Instagram API Error Message: {container_data['error']['error_user_msg']}")
            return False

        creation_id = container_data['id']
        print(f"Instagram feed media container created with ID: {creation_id}.")

        # Publish the media container
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_data = publish_response.json()

        if 'id' in publish_data:
            print(f"Image successfully uploaded to Instagram Feed! Post ID: {publish_data['id']}")
            return True
        else:
            print(f"Error publishing image to Instagram Feed. Response: {publish_data}")
            if 'error' in publish_data and 'error_user_msg' in publish_data['error']:
                print(f"Instagram API Error Message: {publish_data['error']['error_user_msg']}")
            return False

    except requests.exceptions.RequestException as req_err:
        print(f"Network or API request error during Instagram feed image upload: {req_err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Instagram feed image upload: {e}")
        return False


def upload_image_to_facebook_page(image_url, message):
    """
    Uploads an image to a Facebook Page.
    Requires a Facebook Page ID and a Page Access Token with publish_pages/pages_manage_posts permission.
    """
    if not FACEBOOK_PAGE_ACCESS_TOKEN:
        print("Error: Facebook Page access token not configured in environment variables.")
        return False
    if not FACEBOOK_PAGE_ID:
        print("Error: Facebook Page ID not configured in environment variables.")
        return False

    try:
        # Facebook Page photo upload endpoint
        # The 'url' parameter is used for external URLs for Facebook photos.
        upload_url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/photos"
        upload_payload = {
            'url': image_url, # The URL of the image hosted on Cloudinary
            'message': message,
            'access_token': FACEBOOK_PAGE_ACCESS_TOKEN,
            'published': True # Set to True to publish immediately
        }
        
        print(f"\n--- Starting Facebook Page Image Upload Process ---")
        print(f"Attempting to upload image to Facebook Page: {image_url}")
        response = requests.post(upload_url, data=upload_payload)
        response_data = response.json()

        if 'id' in response_data:
            print(f"Image successfully uploaded to Facebook Page! Post ID: {response_data['id']}")
            return True
        else:
            print(f"Error uploading image to Facebook Page. Response: {response_data}")
            if 'error' in response_data and 'message' in response_data['error']:
                print(f"Facebook API Error Message: {response_data['error']['message']}")
            return False

    except requests.exceptions.RequestException as req_err:
        print(f"Network or API request error during Facebook upload: {req_err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Facebook upload: {e}")
        return False


def main():
    image_folder_name = "Quotes"

    # Fetch images from Cloudinary
    all_image_urls = get_resources_from_cloudinary_folder(image_folder_name, "image")

    if not all_image_urls:
        print(f"No images found in Cloudinary folder: '{image_folder_name}'. Exiting.")
        return

    # --- Post to Instagram Feed ---
    selected_instagram_image_url = random.choice(all_image_urls)
    instagram_image_caption = "Here's your daily dose of inspiration! ✨ #quotes #motivation #inspiration #dailyquotes"
    
    print(f"\n--- Preparing to post random image to Instagram Feed: {selected_instagram_image_url} ---")
    success_instagram = upload_image_to_instagram_feed(selected_instagram_image_url, instagram_image_caption)
    if success_instagram:
        print(f"\nRandom image upload process to Instagram Feed completed successfully!")
    else:
        print(f"\nFailed to upload the random image to Instagram Feed.")

    # --- Post to Facebook Page ---
    # You might want to pick a different image for Facebook or use the same one.
    selected_facebook_image_url = random.choice(all_image_urls)
    facebook_post_message = "Get inspired with today's random quote image! #motivation #quotes #inspiration"
    
    print(f"\n--- Preparing to post random image to Facebook Page: {selected_facebook_image_url} ---")
    success_facebook = upload_image_to_facebook_page(selected_facebook_image_url, facebook_post_message)
    if success_facebook:
        print(f"\nRandom image upload process to Facebook Page completed successfully!")
    else:
        print(f"\nFailed to upload the random image to Facebook Page.")


if __name__ == "__main__":
    main()

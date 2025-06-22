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

def get_resources_from_cloudinary_folder(folder_name, resource_type):
    """
    Fetches resource URLs (images or videos) from a specified Cloudinary folder.
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
        response = requests.post(container_url, data=container_payload)
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
        print(f"Publishing image to Instagram Feed with creation ID: {creation_id}")
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

def upload_image_to_instagram_story(image_url):
    """
    Uploads a single image to Instagram Story.
    Requires 'media_type': 'STORY'.
    """
    if not INSTAGRAM_ACCESS_TOKEN:
        print("Error: Instagram access token not configured in environment variables.")
        return False
    if not INSTAGRAM_PAGE_ID:
        print("Error: Instagram page ID not configured in environment variables.")
        return False

    try:
        print(f"\n--- Starting Instagram Story Image Upload Process ---")
        print(f"Creating Instagram story container for image: {image_url}")

        # Step 1: Create media container for Story
        # Stories endpoint uses 'instagram_business_account_id/media' with media_type='STORY'
        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media"
        container_payload = {
            'image_url': image_url,
            'media_type': 'STORY', # This is correct and required for Stories
            'access_token': INSTAGRAM_ACCESS_TOKEN,
            # For stories, you can add 'link_sticker' or other story-specific features here
            # e.g., 'link_sticker': '{"link":"https://www.example.com"}'
        }
        response = requests.post(container_url, data=container_payload)
        container_data = response.json()

        if 'id' not in container_data:
            print(f"Error creating Instagram story container. Response: {container_data}")
            if 'error' in container_data and 'error_user_msg' in container_data['error']:
                print(f"Instagram API Error Message: {container_data['error']['error_user_msg']}")
            return False

        creation_id = container_data['id']
        print(f"Instagram story media container created with ID: {creation_id}.")

        # Step 2: Publish the created media container to Story
        # The publish endpoint is the same as for feed posts, but uses the story's creation_id
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        print(f"Publishing image to Instagram Story with creation ID: {creation_id}")
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_data = publish_response.json()

        if 'id' in publish_data:
            print(f"Image successfully uploaded to Instagram Story! Story ID: {publish_data['id']}")
            return True
        else:
            print(f"Error publishing image to Instagram Story. Response: {publish_data}")
            if 'error' in publish_data and 'error_user_msg' in publish_data['error']:
                print(f"Instagram API Error Message: {publish_data['error']['error_user_msg']}")
            return False

    except requests.exceptions.RequestException as req_err:
        print(f"Network or API request error during Instagram story upload: {req_err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Instagram story upload: {e}")
        return False

def main():
    image_folder_name = "Quotes"

    # Fetch images from Cloudinary
    all_image_urls = get_resources_from_cloudinary_folder(image_folder_name, "image")

    if not all_image_urls:
        print(f"No images found in Cloudinary folder: '{image_folder_name}'. Exiting.")
        return

    # --- Post to Instagram Feed ---
    selected_feed_image_url = random.choice(all_image_urls)
    feed_image_caption = "Here's your daily dose of inspiration! ✨ #quotes #motivation #inspiration #dailyquotes"
    success_feed = upload_image_to_instagram_feed(selected_feed_image_url, feed_image_caption)
    if success_feed:
        print(f"\nRandom image upload process to Instagram Feed completed successfully!")
    else:
        print(f"\nFailed to upload the random image to Instagram Feed.")


    # --- Post to Instagram Story ---
    selected_story_image_url = random.choice(all_image_urls)
    # Important: Stories work best with 9:16 aspect ratio (e.g., 1080x1920 pixels).
    # Ensure your images in Cloudinary for stories are optimized for this ratio.
    print(f"\n--- Preparing to post random image to Instagram Story: {selected_story_image_url} ---")
    success_story = upload_image_to_instagram_story(selected_story_image_url)
    if success_story:
        print(f"\nRandom image upload process to Instagram Story completed successfully!")
    else:
        print(f"\nFailed to upload the random image to Instagram Story.")


if __name__ == "__main__":
    main()

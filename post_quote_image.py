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
    Fetches resource URLs (images) from a specified Cloudinary folder.
    """
    try:
        # Check if Cloudinary credentials are set from environment variables
        if not cloudinary.config().cloud_name or \
           not cloudinary.config().api_key or \
           not cloudinary.config().api_secret:
            print("Error: Cloudinary credentials not set in environment variables.")
            return []

        result = cloudinary.api.resources(
            type="upload",
            resource_type=resource_type,
            prefix=f"{folder_name}/",
            max_results=500 # Adjust as needed to ensure all images are fetched
        )
        resource_urls = [resource['secure_url'] for resource in result.get('resources', [])]
        print(f"Successfully fetched {len(resource_urls)} {resource_type}s from Cloudinary folder '{folder_name}'.")
        return resource_urls
    except Exception as e:
        print(f"Error fetching {resource_type}s from Cloudinary: {e}")
        return []

def upload_image_to_instagram(image_url, caption):
    """Uploads a single image to Instagram."""
    if not INSTAGRAM_ACCESS_TOKEN:
        print("Error: Instagram access token not configured in environment variables.")
        return False
    if not INSTAGRAM_PAGE_ID:
        print("Error: Instagram page ID not configured in environment variables.")
        return False

    try:
        print(f"\n--- Starting Instagram Image Upload Process ---")
        print(f"Creating Instagram media container for image: {image_url}")

        # Step 1: Create media container
        container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media"
        container_payload = {
            'image_url': image_url,
            'caption': caption,
            'access_token': INSTAGRAM_ACCESS_TOKEN,
            'share_to_feed': True
        }
        container_response = requests.post(container_url, data=container_payload)
        container_data = container_response.json()

        if 'id' not in container_data:
            print(f"Error creating Instagram container for image. Response: {container_data}")
            if 'error' in container_data and 'error_user_msg' in container_data['error']:
                print(f"Instagram API Error Message: {container_data['error']['error_user_msg']}")
            return False

        creation_id = container_data['id']
        print(f"Instagram image media container created with ID: {creation_id}.")

        # Step 2: Publish the media container
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_PAGE_ID}/media_publish"
        publish_payload = {
            'creation_id': creation_id,
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        publish_data = publish_response.json()

        if 'id' in publish_data:
            print(f"Image successfully uploaded to Instagram! Post ID: {publish_data['id']}")
            return True
        else:
            print(f"Error publishing image to Instagram. Response: {publish_data}")
            if 'error' in publish_data and 'error_user_msg' in publish_data['error']:
                print(f"Instagram API Error Message: {publish_data['error']['error_user_msg']}")
            return False

    except requests.exceptions.RequestException as req_err:
        print(f"Network or API request error during Instagram image upload: {req_err}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during Instagram image upload: {e}")
        return False

def main():
    image_folder_name = "Quotes"

    # Fetch images from Cloudinary
    all_image_urls = get_resources_from_cloudinary_folder(image_folder_name, "image")

    if not all_image_urls:
        print(f"No images found in Cloudinary folder: '{image_folder_name}'. Exiting.")
        return

    # Select a random image from all available images
    selected_image_url = random.choice(all_image_urls)
    image_caption = "Here's your daily dose of inspiration! ✨ #quotes #motivation #inspiration #dailyquotes"

    print(f"\n--- Preparing to post random image to Instagram: {selected_image_url} ---")
    success = upload_image_to_instagram(selected_image_url, image_caption)

    if success:
        print(f"Random image upload process to Instagram completed successfully!")
    else:
        print(f"Failed to upload the random image to Instagram.")

if __name__ == "__main__":
    main()

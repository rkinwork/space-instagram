import os
import time
import glob
import itertools

import requests
from instabot import Bot

IMAGES_DIR = 'images'
HUBBLE_HOST = 'http://hubblesite.org/api/v3/'
ACCEPTABLE_IMAGE_FILES_EXTENSIONS = ['jpg', 'jpeg', 'pdf', 'png', 'bpm']


def get_file_extension(filename):
    _, extension = filename.rsplit('.', 1)
    if extension and extension.lower() in ACCEPTABLE_IMAGE_FILES_EXTENSIONS:
        return extension
    return None


def download_picture(url, picture_name, image_store_path=IMAGES_DIR):
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(image_store_path, exist_ok=True)
    with open(os.path.join(image_store_path, picture_name), 'wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch():
    response = requests.get('https://api.spacexdata.com/v3/launches/latest')
    response.raise_for_status()
    flight_number = response.json()['flight_number']
    for link_number, link in enumerate(sorted(response.json()['links']['flickr_images']), 1):
        download_picture(link, f"spacex_{flight_number}_{link_number}.jpg")


def download_hubble_collection(collection_name):
    # http://hubblesite.org/api/v3/images/printshop
    response = requests.get(os.path.join(HUBBLE_HOST, f'images/{collection_name}'))
    response.raise_for_status()
    list(map(download_hubble_picture_by_image_id,
             [picture_description['id'] for picture_description in response.json()]))


def hubble_image_urls_by_image_id(image_id):
    response = requests.get(os.path.join(HUBBLE_HOST, f'image/{image_id}'))
    response.raise_for_status()
    urls = [image_file_node['file_url'] for image_file_node in response.json()['image_files']]
    return sorted(urls)


def download_hubble_picture_by_image_id(image_id):
    high_res_picture_url = hubble_image_urls_by_image_id(image_id)[0]
    file_name = f"{image_id}.{get_file_extension(high_res_picture_url)}"
    download_picture(high_res_picture_url, file_name)


def get_instabot_instance(username=None, password=None):
    bot_username = username if username else os.getenv('SPACE_INSTAGRAM_LOGIN')
    bot_password = password if password else os.getenv('SPACE_INSTAGRAM_PASSWORD')
    bot = Bot(verbosity=False)
    bot.login(username=bot_username, password=bot_password)
    return bot


def main():
    download_hubble_collection('printshop')
    fetch_spacex_last_launch()


def remove_temp_photos():
    for file_path in glob.glob("images/*.REMOVE_ME"):
        os.remove(file_path)


def upload_photo_to_instagram(filename='', caption=''):
    pic = os.path.abspath(filename)
    bot = get_instabot_instance()
    bot.upload_photo(pic, caption=caption)
    bot.api.last_response.raise_for_status()


def upload_all_photos():
    images_to_publish = (glob.glob(f"images/*.{extension}") for extension in ACCEPTABLE_IMAGE_FILES_EXTENSIONS)
    for image_path in itertools.chain.from_iterable(images_to_publish):
        upload_photo_to_instagram(image_path)
        time.sleep(60)

    remove_temp_photos()

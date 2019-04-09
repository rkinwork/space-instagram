import os
import pprint
import time
import glob
import itertools

import requests
from instabot import Bot

IMAGES_DIR = 'images'
HUBBLE_HOST = 'http://hubblesite.org/api/v3/'
ACCEPTABLE_IMAGE_FILES_EXTENSIONS = ['jpg', 'jpeg', 'pdf', 'png', 'bpm']

pp = pprint.PrettyPrinter()


def get_file_extension(filename):
    _, extension = filename.rsplit('.', 1)
    if extension and extension.lower() in ACCEPTABLE_IMAGE_FILES_EXTENSIONS:
        return extension
    return None


def download_picture(url, picture_name, image_store_path=IMAGES_DIR):
    response = requests.get(url)
    if not response.ok:
        return None
    os.makedirs(image_store_path, exist_ok=True)
    with open(os.path.join(image_store_path, picture_name), 'wb') as file:
        file.write(response.content)


def fetch_spacex_last_launch():
    response = requests.get('https://api.spacexdata.com/v3/launches/latest')

    flight_number = response.json()['flight_number']
    for link_number, link in enumerate(sorted(response.json()['links']['flickr_images']), 1):
        download_picture(link, f"spacex_{flight_number}_{link_number}.jpg")
    print('All images has been downloaded to images folder')


def download_hubble_collection(collection_name):
    # http://hubblesite.org/api/v3/images/printshop
    response = requests.get(os.path.join(HUBBLE_HOST, f'images/{collection_name}'))
    if not response.ok:
        return None
    print([picture_description['id'] for picture_description in response.json()])
    list(map(download_hubble_picture_by_image_id,
             [picture_description['id'] for picture_description in response.json()]))


def hubble_image_urls_by_image_id(image_id):
    response = requests.get(os.path.join(HUBBLE_HOST, f'image/{image_id}'))
    if not response.ok:
        return None
    urls = [image_file_node['file_url'] for image_file_node in response.json()['image_files']]
    return sorted(urls)


def download_hubble_picture_by_image_id(image_id):
    high_res_picture_url = hubble_image_urls_by_image_id(image_id)[0]
    file_name = f"{image_id}.{get_file_extension(high_res_picture_url)}"
    print(f"downloading {file_name}")
    download_picture(high_res_picture_url, file_name)
    print("downloading finished")


def get_instabot_instance(username=None, password=None):
    bot_username = username if username else os.getenv('SPACE_INSTAGRAM_LOGIN')
    bot_password = password if password else os.getenv('SPACE_INSTAGRAM_PASSWORD')
    bot = Bot()
    bot.login(username=bot_username, password=bot_password)
    return bot


def main():
    download_hubble_collection('printshop')
    fetch_spacex_last_launch()


def upload_photo_to_instagram(filename='', caption=''):
    pic = os.path.abspath(filename)
    bot = get_instabot_instance()
    bot.upload_photo(pic, caption=caption)
    if bot.api.last_response.status_code != 200:
        print(bot.api.last_response)
    for file_path in glob.glob(f"{filename}*.REMOVE_ME"):
        os.remove(file_path)


def upload_all_photos():
    images_to_publish = (glob.glob(f"images/*.{extension}") for extension in ACCEPTABLE_IMAGE_FILES_EXTENSIONS)
    for image_path in itertools.chain.from_iterable(images_to_publish):
        print(image_path)
        upload_photo_to_instagram(image_path)
        time.sleep(60)

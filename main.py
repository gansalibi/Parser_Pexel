import requests
from tqdm import tqdm
import json
import os
import math
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')
proxy_login = os.getenv('PROXY_LOGIN')
proxy_pass = os.getenv('PROXY_PASS')



def scrap_pexels(query=''):
    headers = {'Authorization': token}
    query_str = f'https://api.pexels.com/v1/search?query={query}&per_page=80&orientation=landscape'
    proxies = {
        'https': f'http://{proxy_login}:{proxy_pass}@38.152.69.94:8000'
    }

    response = requests.get(url=query_str, headers=headers, proxies=proxies)

    if response.status_code != 200:
        return f'Ошибка: Статус код - {response.status_code}, {response.json}'

    img_dir_path = '_'.join(i for i in query.split(' ') if i.isalnum())
    print(img_dir_path)

    if not os.path.exists(img_dir_path):
        os.makedirs(img_dir_path)

    json_data = response.json()

    with open(f'result_{query}.json', 'w') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=True)

    images_count = json_data.get('total_results')

    if not json_data.get('next_page'):
        img_urls = [item.get('src').get('original') for item in json_data.get('photos')]
        download_images(img_list=img_urls, img_dir_path=img_dir_path, proxies=proxies)
    else:
        print(f'[INFO] Всего изображений: {images_count}. Сохранение может занять какое-то время.')

        images_list_urls = []
        for page in range(math.ceil(images_count/80)+1):
            query_str = f'{query_str}&page={page}'
            response = requests.get(url=query_str, headers=headers, proxies=proxies)
            json_data = response.json()
            img_urls = [item.get('src').get('original') for item in json_data.get('photos')]
            images_list_urls.extend(img_urls)
        download_images(img_list=images_list_urls, img_dir_path=img_dir_path, proxies=proxies)

def download_images(img_list=[], img_dir_path='', proxies={}):

    for item_url in tqdm(img_list):
        response = requests.get(url=item_url, proxies=proxies)

        if response.status_code == 200:
            with open(f'./{img_dir_path}/{item_url.split("-")[-1]}', 'wb') as file:
                file.write(response.content)
        else:
            print('Что-то пошло не так при скачивании изображения!')

def main():
    query = input('Введите ключевую фразу для поиска: ')
    scrap_pexels(query=query)



if __name__ == '__main__':
    main()


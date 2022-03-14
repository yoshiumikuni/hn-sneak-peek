from tqdm import tqdm
import os
import requests
import concurrent.futures
import urllib.parse

def split_list(a_list, wanted_parts=1):
	length = len(a_list)
	return [a_list[i*length // wanted_parts: (i+1)*length // wanted_parts]
		for i in range(wanted_parts)]

def download_image(list_of_urls, save_path):
	length_list = len(list_of_urls)
	for i in tqdm(range(length_list)):
		response = requests.get(list_of_urls[i], stream=True)
		filename = list_of_urls[i].rsplit('/',1)[-1]
		save_path = urllib.parse.urljoin(save_path, filename)
		with open(save_path, 'wb') as file:
			for data in response.iter_content(1024):
				file.write(data)

url_list = [
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-black-000.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-blue-00f.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-cyan-0ff.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-gray-7f7f7f.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-green-0f0.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-purple-f0f.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-red-f00.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-white-fff.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/cs-yellow-ff0.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/ia-forrest.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/ia-installing.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/pg-coral.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/pg-couplevn.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/web-booking.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/web-braverangels.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/web-jakearchibald.png',
	'https://raw.githubusercontent.com/test-images/png/main/202105/web-surma.png'	
]

path = '177013/'
os.makedirs(path, exist_ok=True)
url_list = split_list(url_list, os.cpu_count())
with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
	for i in range(os.cpu_count()):
		executor.submit(download_image, url_list[i], path)
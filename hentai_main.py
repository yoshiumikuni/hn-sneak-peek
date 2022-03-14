from PIL import Image
from tqdm import tqdm
import concurrent.futures
import PySimpleGUI as sg
import hentai as hn
import urllib.parse
import requests
import datetime
import base64
import io
import os

def split_list(a_list, wanted_parts=1):
	length = len(a_list)
	return [a_list[i*length // wanted_parts: (i+1)*length // wanted_parts]
		for i in range(wanted_parts)]

def download_images(list_of_urls, save_path):
	length_list = len(list_of_urls)
	for i in tqdm(range(length_list)):
		response = requests.get(list_of_urls[i], stream=True)
		filename = list_of_urls[i].rsplit('/',1)[-1] # get path after the lash slash (/) of url
		# https://example.com/.../.../file.txt -> output: file.txt

		save_path = urllib.parse.urljoin(save_path, filename)
		with open(save_path, 'wb') as file:
			for data in response.iter_content(1024):
				file.write(data) # write file to local machine

def convert_image_to_png(image_source, size=(500,500)):
	img = Image.open(image_source)
	img.thumbnail(size)
	img_byte = io.BytesIO()
	img.save(img_byte, format='PNG')
	return img_byte.getvalue()

def sauce_exists(sauce_code):	
	try:
		sauce = hn.Hentai(sauce_code)
		status = hn.Hentai.exists(sauce.id)
	except Exception as e:
		return False
	return status

def sauce_show_cover(image_url_or_link):
	get_image = requests.get(image_url_or_link, stream=True).raw
	img = Image.open(get_image)
	img.show()

def sauce_info(sauce_code):
	doujin = hn.Hentai(sauce_code)
	sauce_title 		= doujin.title() # title from web - String
	sauce_title_pretty 	= doujin.title(hn.Format.Pretty) # title pretty - String
	sauce_artist_name	= doujin.artist[0].name # artist name - String
	sauce_artist_url	= doujin.artist[0].url # artist URL - string
	sauce_tag 			= [] # lists of tags - Lists

	for tag in doujin.tag:
		sauce_tag.append(tag.name) # append tags in doujin.tag 

	sauce_uploaddate	= doujin.upload_date
	sauce_uploaddate	= sauce_uploaddate.strftime('%d/%m/%Y')	# upload date - String
	sauce_url_images	= doujin.image_urls	# list of image URL - Lists

	return sauce_title, sauce_title_pretty, sauce_artist_name, sauce_artist_url, sauce_tag, sauce_uploaddate, sauce_url_images



sg.theme("DarkAmber")

layout_main_top = [
	[sg.Text('Sauce	'), sg.InputText(key='-CODE-'), sg.Button('Go')],
	[sg.Text('Title 	:   -', key='title_txt')],
	[sg.Text('Artist 	:   -', key='artist_txt')],
	[sg.Text('Page(s) 	:   -', key='page_txt')],
	[sg.Text('Uploaded :   -', key='uploaddate_txt')],
	[sg.Text('Tags	:'), sg.Multiline(size=(47, 5), disabled=True, key='tags_txt')],
]

layout_main_bottom = [
	[sg.Button('Download', disabled=True, key='download_btn'), sg.Button('View Cover', disabled=True, key='view_btn')],
]

# layout interface of the main window
layout_main = [
	[sg.Column(layout_main_top)],
	[sg.HSeparator()],
	[sg.Column(layout_main_bottom, justification='right')]
]

# show window application
window = sg.Window('NH Sneak Peek', layout_main)


sauce_is_exists = False
images_urls = None

# looping. Here the logic of the program run
while True:
	event, values = window.read()

	if event == sg.WIN_CLOSED or event == 'Cancel':
		break
	
	# go button clicked
	if event == 'Go':
		# checking if the nuke code exist in nhentai website
		with concurrent.futures.ThreadPoolExecutor() as executor:
			future = executor.submit(sauce_exists, values['-CODE-'])
			sauce_is_exists = future.result() # returning True or False

		if values['-CODE-'] == "":
			sg.popup_error("Please provide the nuke code", title='Error')

		# if the nuke code found (exists)
		elif sauce_is_exists:
			# accessing API
			with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
				future = executor.submit(sauce_info, values['-CODE-'])
				return_value = future.result()
				title, title_pretty, artist_name, artist_url, tags, upload_date, images_urls = return_value

				# modif title text, if too long cut it so the main window not expanding
				if len(title) >= 55:
					window['title_txt'].update('Title 	:   {0}...'.format(title[0:55]))
					window['title_txt'].set_tooltip(title)
				else:
					window['title_txt'].update('Title 	:   {0}'.format(title))
					# window['title_txt'].set_tooltip(title)

				# update value of artist, total hentai pages, upload date
				window['artist_txt'].update('Artist 	:   {0}'.format(artist_name))
				window['page_txt'].update('Page(s) 	:   {0}'.format(len(images_urls)))
				window['uploaddate_txt'].update('Uploaded :   {0}'.format(upload_date))
				tags = ', '.join(map(str, tags))
				window['tags_txt'].update(tags)

				# enable view cover & download button
				window['view_btn'].update(disabled=False)
				window['download_btn'].update(disabled=False)
		else:
			sg.popup_error("Code not found or error occurred", title='Error')
	
	if event == 'view_btn':
		with concurrent.futures.ThreadPoolExecutor() as executor:
			# show hentai cover in default user image viewer
			img = executor.submit(sauce_show_cover, images_urls[0])

	if event == 'download_btn':
		url_list = split_list(images_urls, os.cpu_count()) # spliting long list into current user CPU cores
		# example: current user processor core is 4, so long list splited into 4

		path = values['-CODE-'] + '/' # adding '/' so images saved into path folder, not current folder
		os.makedirs(path, exist_ok=True)

		with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
			for i in range(os.cpu_count()):
				executor.submit(download_images, url_list[i], path)


# terminate program
window.close()
from PIL import Image
import PySimpleGUI as sg
import hentai as hn
import urllib.parse
import requests
import datetime
import io
import os

def split_list(a_list, wanted_parts=1):
	length = len(a_list)
	return [a_list[i*length // wanted_parts: (i+1)*length // wanted_parts]
		for i in range(wanted_parts)]

def download_images(list_of_urls, save_location, window):
	length_list = len(list_of_urls)
	for i in range(length_list):
		window.set_title('NH Sneak Peek - Downloading... {}/{}'.format(i+1, length_list))
		response = requests.get(list_of_urls[i], stream=True)
		filename = list_of_urls[i].rsplit('/',1)[-1] # get path after the lash slash (/) of url
		# https://example.com/.../.../file.txt -> output: file.txt as string

		save_path = urllib.parse.urljoin(save_location, filename)
		with open(save_path, 'wb') as file:
			for data in response.iter_content(1024):
				file.write(data) # write file to local machine

def show_sauce_cover(image_url):
	image = requests.get(image_url, stream=True).raw
	image = Image.open(image)
	image.show()

def sauce_is_exists(sauce_code):
	try:
		sauce = hn.Hentai(sauce_code)
		is_exists = hn.Hentai.exists(sauce.id)
	except Exception as e:
		print(e)
		return False
	else:
		return True

def get_sauce_info(sauce_code):
	doujin = hn.Hentai(sauce_code)
	
	try:
		title = doujin.title()
		title_pretty = doujin.title(hn.Format.Pretty)
		artist = doujin.artist[0].name
		url = doujin.artist[0].url
		tag = []

		for i in doujin.tag:
			tag.append(i.name)

		uploaddate = doujin.upload_date
		uploaddate = uploaddate.strftime('%d/%m/%Y')

		image_urls = doujin.image_urls
	except Exception as e:
		sg.popup_error(e, title='Error')
		window['go_btn'].update(disabled=False)
	else:
		return title, title_pretty, artist, url, tag, uploaddate, image_urls

def main():
	sg.theme('DarkAmber')
	layout_main_top = [
		[sg.Text('Sauce	'), sg.InputText(key='-CODE-'), sg.Button('Go', key='go_btn')],
		[sg.Text('Title 	:   -', key='title_txt')],
		[sg.Text('Artist 	:   -', key='artist_txt')],
		[sg.Text('Page(s) 	:   -', key='page_txt')],
		[sg.Text('Uploaded :   -', key='uploaddate_txt')],
		[sg.Text('Tags	:'), sg.Multiline(size=(47, 5), disabled=True, key='tags_txt')],
	]

	layout_main_bottom = [
		[sg.Button('Download', disabled=True, key='download_btn'), sg.Button('View Cover', disabled=True, key='view_btn')]
	]

	layout_main = [
		[sg.Column(layout_main_top)],
		[sg.HSeparator()],
		[sg.Column(layout_main_bottom, justification='right')]
	]

	window = sg.Window('NH Sneak Peek', layout_main)

	image_urls = None
	while True:
		event, values = window.read()

		if event == sg.WIN_CLOSED:
			break

		if event == 'go_btn':
			window['go_btn'].update(disabled=True)
			window.set_title('NH Sneak Peek - Getting sauce info... please wait...')

			window.perform_long_operation(lambda: sauce_is_exists(values['-CODE-']), 'get_sauce_is_exists_complete')

		elif event == 'view_btn':
			window['view_btn'].update(disabled=True)
			window['download_btn'].update(disabled=True)
			window['go_btn'].update(disabled=True)
			window.set_title('NH Sneak Peek - Getting image cover... please wait...')

			window.perform_long_operation(lambda: show_sauce_cover(image_urls[0]), 'get_sauce_cover_complete')

		elif event == 'download_btn':
			window['view_btn'].update(disabled=True)
			window['download_btn'].update(disabled=True)
			window['go_btn'].update(disabled=True)

			save_location = values['-CODE-'] + '/'
			os.makedirs(save_location, exist_ok=True)

			window.perform_long_operation(lambda: download_images(image_urls, save_location, window), 'download_images_complete')

		if event == 'get_sauce_is_exists_complete':
			if values['get_sauce_is_exists_complete'] == True:
				window.perform_long_operation(lambda: get_sauce_info(values['-CODE-']), 'get_sauce_info_complete')
			else:
				sg.popup_error('Nuke code not found!', title='Error')
				
				window['go_btn'].update(disabled=False)
				window.set_title('NH Sneak Peek')

				window['title_txt'].update('Title 	:   ')
				window['artist_txt'].update('Artist 	:   ')
				window['page_txt'].update('Page(s) 	:   ')
				window['uploaddate_txt'].update('Uploaded :   ')
				window['tags_txt'].update('')

		elif event == 'get_sauce_info_complete':
			window.set_title('NH Sneak Peek - Viewing {}'.format(values['-CODE-']))
			window['go_btn'].update(disabled=False)
			
			sauce_info = values['get_sauce_info_complete']
			
			if len(sauce_info[0]) >= 55:
				window['title_txt'].update('Title 	:   {0}...'.format(sauce_info[0][0:55]))
				window['title_txt'].set_tooltip(sauce_info[0])
			else:
				window['title_txt'].update('Title 	:   {0}'.format(sauce_info[0]))

			window['artist_txt'].update('Artist 	:   {0}'.format(sauce_info[2]))
			window['page_txt'].update('Page(s) 	:   {0}'.format(len(sauce_info[6])))
			window['uploaddate_txt'].update('Uploaded :   {0}'.format(sauce_info[5]))
			window['tags_txt'].update(sauce_info[4])

			window['view_btn'].update(disabled=False)
			window['download_btn'].update(disabled=False)

			image_urls = sauce_info[6]
			
		elif event == 'get_sauce_cover_complete':
			window.set_title('NH Sneak Peek - Viewing {}'.format(values['-CODE-']))
			
			window['view_btn'].update(disabled=False)
			window['download_btn'].update(disabled=False)
			window['go_btn'].update(disabled=False)

		elif event == 'download_images_complete':
			sg.popup_ok('Download Complete!')

			window.set_title('NH Sneak Peek - Viewing {}'.format(values['-CODE-']))

			window['view_btn'].update(disabled=False)
			window['download_btn'].update(disabled=False)
			window['go_btn'].update(disabled=False)
			

if __name__ == '__main__':
	main()
	print('Program Closing')
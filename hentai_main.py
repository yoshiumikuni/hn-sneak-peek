from PIL import Image
import concurrent.futures
import PySimpleGUI as sg
import hentai as hn
import requests
import datetime
import io
import os


def sauce_exists(sauce_code):	
	try:
		sauce = hn.Hentai(sauce_code)
		status = hn.Hentai.exists(sauce.id)
	except Exception as e:
		print(e)
		return False

	return status

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

# add image viewer navigation function that working with button.
# def image_viewer(url_in_list, nav_code):




sg.theme("DarkAmber")

# layout interface of the main window
layout = [
	[sg.Text('Sauce'), sg.InputText(key='-CODE-'), sg.Button('Go')],
	[sg.Text('Title : ', key='-TXT_TITLE-')],
	[sg.Text('Artist : ', key='-TXT_ARTIST-')],
	[sg.Text('Uploaded : ', key='-TXT_UPLOAD-')],
	[sg.Text('Page(s) :', key='-TXT_PAGES-')],
	[sg.Text('Tags : ')],
	[sg.Multiline(size=(55, 5), disabled=True, key='-TXT_TAGS-')],

	# Image viewer & 2 button for navigation
	[sg.Column([[sg.Image(key="-IMAGE-")]], justification='center')],
	# [sg.Column([[sg.Button('< Prev', visible=True, key='prev'), sg.Button('Next >', visible=True, key='next')]],justification='center')],
]

# show window application
window = sg.Window('NH Sneak Peek', layout)

# looping. Here the logic of the program run
while True:
	sauce_is_exists = False
	images_urls = None

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
			sg.popup_error("Please provide the nuke code")

		# if the nuke code found (exists)
		elif sauce_is_exists:
			# accessing API
			with concurrent.futures.ThreadPoolExecutor() as executor:
				future = executor.submit(sauce_info, values['-CODE-'])
				return_value = future.result()
				title, title_pretty, artist_name, artist_url, tags, upload_date, images_urls = return_value

				# modif title text, if too long cut it so the main window not expanding
				if len(title_pretty) > 65:
					window['-TXT_TITLE-'].update('Title : {0}'.format(title_pretty[0:65]))
					window['-TXT_TITLE-'].set_tooltip(title)
				else:
					window['-TXT_TITLE-'].update('Title : {0}'.format(title_pretty))
					window['-TXT_TITLE-'].set_tooltip(title)

				window['-TXT_ARTIST-'].update('Artist : {0}'.format(artist_name))
				window['-TXT_UPLOAD-'].update('Uploaded : {0}'.format(upload_date))
				tags = ', '.join(map(str, tags))
				window['-TXT_TAGS-'].update(tags)
				window['-TXT_PAGES-'].update('Page(s) : {0}'.format(len(images_urls)))

				# showing the first image of the manga
				im = Image.open(requests.get(images_urls[0], stream=True).raw)
				im.thumbnail((600,600))
				bio = io.BytesIO()
				im.save(bio, format="PNG") # convert to PNG, somehow the element (image viewer element) not support JPG format
				window['-IMAGE-'].update(bio.getvalue())

				# window['next'].update(visible=True)
				# window['prev'].update(visible=True)
		else:
			sg.popup_error("Code not found or error occurred")


# terminate program
window.close()
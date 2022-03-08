from PIL import Image
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
	sauce_images		= doujin.image_urls	# list of image URL - Lists

	return sauce_title, sauce_title_pretty, sauce_artist_name, sauce_artist_url, sauce_tag, sauce_uploaddate, sauce_images


sg.theme("DarkAmber")
layout = [
	[sg.Text('Sauce'), sg.InputText(key='-CODE-'), sg.Button('Go')],
	[sg.Text('Title : ', key='-TX_TITLE-')],
	[sg.Text('Artist : ', key='-TX_ARTIST-')],
	[sg.Text('Uploaded : ', key='-TX_UPLOAD-')],
	[sg.Text('Tags: ')],
	[sg.Multiline(size=(55, 5), disabled=True, key='-TX_TAGS-')],
	[sg.Text('2022 Copyright Yoshi~')]

	# Image viewer
	# 2 button for navigate
]

window = sg.Window('Nuke Code Sneak Peek', layout)

while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED or event == 'Cancel':
		break
	
	if event == 'Go':
		if values['-CODE-'] == "":
			sg.popup_error("please provide the nuke code")
		elif sauce_exists(values['-CODE-']):
			title, title_pretty, artist_name, artist_url, tags, upload_date, images = sauce_info(values['-CODE-'])
			print(title)
			print(title_pretty)
			print(upload_date)
			print(artist_name)
			print(tags)

			# modif title text, if too long cut it so the main window not expanding
			if len(title_pretty) > 65:
				window['-TX_TITLE-'].update('Title: {0}'.format(title_pretty[0:65]))
				window['-TX_TITLE-'].set_tooltip(title)
			else:
				window['-TX_TITLE-'].update('Title: {0}'.format(title_pretty))
				window['-TX_TITLE-'].set_tooltip(title)


			window['-TX_ARTIST-'].update('Artist: {0}'.format(artist_name))
			window['-TX_UPLOAD-'].update('Uploaded: {0}'.format(upload_date))
			tags = ', '.join(map(str, tags))
			window['-TX_TAGS-'].update(tags)
		else:
			# print("sauce not exists")
			sg.popup_error("code not found or error occurred")


window.close()
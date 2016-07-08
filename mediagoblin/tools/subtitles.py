import os

def get_path(path):
	return eval(path)

def open_subtitle(path):
	temp = ['user_dev','media','public']
	path = list(get_path(path))
	file_path = os.path.abspath(__file__).split('/') # Path of current file as dictionary
	subtitle_path = file_path[:-3] + temp + path # Creating the absolute path for the subtitle file
	subtitle_path = "/" + os.path.join(*subtitle_path)
	subtitle = open(subtitle_path,"r") # Opening the file using the absolute path
	text = subtitle.read()
	return text
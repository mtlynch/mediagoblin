import os

def get_path(path):
	temp = ['user_dev','media','public']
	path = list(eval(path))
	file_path = os.path.abspath(__file__).split('/') # Path of current file as dictionary
	subtitle_path = file_path[:-3] + temp + path # Creating the absolute path for the subtitle file
	subtitle_path = "/" + os.path.join(*subtitle_path)
	return subtitle_path

def open_subtitle(path):
	subtitle_path = get_path(path)
	subtitle = open(subtitle_path,"r") # Opening the file using the absolute path
	text = subtitle.read()
	return text

def save_subtitle(path,text):
	subtitle_path = get_path(path)
	subtitle = open(subtitle_path,"w") # Opening the file using the absolute path
	subtitle.write(text)
import ast,os

def get_path(path):
	"""
    Converting the path of the form
    x = u'[ "A","B","C" ," D"]'
    to
    x = ["A", "B", "C", "D"] 
    """
	return ast.literal_eval(path)

def open_subtitle(path):
	temp = ['user_dev','media','public']
	path = list(get_path(path))
	file_path = os.path.abspath(__file__).split('/') # Path of current file as dictionary
	"""
	Creating the absolute path for the subtitle file
	"""
	subtitle_path = file_path[:-3] + temp + path
	subtitle_path = "/" + os.path.join(*subtitle_path)
	"""
	Opening the file using the absolute path
	"""
	subtitle = open(subtitle_path,"r")
	text = subtitle.read()
	return text
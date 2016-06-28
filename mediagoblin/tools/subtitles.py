import ast

def get_path(path):
	"""
    Converting the path of the form
    x = u'[ "A","B","C" ," D"]'
    to
    x = ["A", "B", "C", "D"] 
    """
	return ast.literal_eval(path)
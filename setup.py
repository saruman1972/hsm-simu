from distutils.core import setup
import py2exe
import glob

setup(
	windows=[
		{"script":"HSMSim.py", "icon_resources":[(1,"icons/HSMSim.ico")]}, 
		{"script":"KeyTranslateDialog.py", "icon_resources":[(1,"icons/KeyTranslateDialog.ico")]}, 
		{"script":"MakeCardDialog.py", "icon_resources":[(1,"icons/MakeCardDialog.ico")]}
	], 
	console=["GenCrdData.py"], 
	data_files=[
		("icons", glob.glob("icons/*.ico")), 
		(".", ["KEY.txt"]), 
		(".", glob.glob("*.xml")), 
		("commands", glob.glob("commands/*.pyc"))
	]
)

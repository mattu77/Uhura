import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--clean',
    '--add-data=ui/*:./ui',
    '--name=Uhura',
    '--icon=icon.ico'
])
import requests, zipfile, io, os, shutil

print('Downloading new scripts')
url = 'https://github.com/Blounard/mkw-scripts/archive/refs/heads/main.zip'
r = requests.get(url)
print('Extracting scripts')
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall("script_update_temp")

source_folder = r'script_update_temp\mkw-scripts-main\scripts'

print('Replacing scripts')
for entry in os.scandir(source_folder):
    source_name = os.path.join(source_folder, entry.name)
    if os.path.isfile(source_name):
        shutil.copy(source_name, entry.name)
    else:
        shutil.copytree(source_name, entry.name, dirs_exist_ok=True)

shutil.rmtree("script_update_temp")

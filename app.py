from flask import Flask, render_template, request
import os
import pathlib
import shutil

def get_folder_size(folder_path):
    total_size = sum(file.stat().st_size for file in pathlib.Path(folder_path).rglob('*') if file.is_file())
    return total_size

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

dirData = []

def listDirData(size = True):
    dirData.clear()
    path = str(pathlib.Path.home())+'/AppData/Roaming'
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isdir(file_path):
            file_name = os.path.basename(file_path)
            if size:
                dirData.append({"Name":file_name,"Size":get_folder_size(file_path)})
            else:
                dirData.append({"Name":file_name})

@app.route('/api/listdir')
def listdir():
    listDirData()

    return dirData


@app.route('/api/delete', methods=['POST'])
def delete():
    path = int(request.form.get('path'))
    listDirData(False)
    shutil.rmtree(str(pathlib.Path.home())+'/AppData/Roaming/'+dirData[path]['Name'])
    return 'OK'


if __name__ == '__main__':
    app.run(debug=False)
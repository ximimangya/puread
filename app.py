from flask import Flask, render_template, request
import os
import pathlib
import shutil
import requests
import time
import json


for directory in ['/rules']:
    if not os.path.exists(os.getcwd() + directory):
        os.makedirs(os.getcwd() + directory)


def get_folder_size(folder_path):
    total_size = sum(file.stat().st_size for file in pathlib.Path(folder_path).rglob('*') if file.is_file())
    return total_size

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

dirData = []

def listDirData(size = True,dir = 'Roaming'):
    dirData.clear()
    path = str(pathlib.Path.home())+'/AppData/'+dir
    files = os.listdir(path)
    for file in files:
        file_path = os.path.join(path, file)

        if os.path.isdir(file_path):
            file_name = os.path.basename(file_path)
            if size:
                dirData.append({"Name":file_name,"Size":get_folder_size(file_path), "Rule":getRule(file_name,dir)})
            else:
                dirData.append({"Name":file_name, "Rule":getRule(file_name,dir)})

@app.route('/api/listdir')
def listdir():
    dir = request.args.get('dir')
    if dir == None or dir == '':
        dir = 'Roaming'
    listDirData(True,dir)

    return dirData


@app.route('/api/delete', methods=['POST'])
def delete():
    item = eval(request.form.get('item'))
    for i in item:
        shutil.rmtree(str(pathlib.Path.home())+'/AppData/Roaming/'+i['name'])
    listDirData(False)
    return 'OK'


@app.route('/api/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword')
    dir = request.form.get('dir')
    listDirData(False,dir)
    result = []
    for i in dirData:
        if keyword.lower() in i['Name'].lower():
            result.append({"Name":i['Name'],"Size":get_folder_size(str(pathlib.Path.home())+'/AppData/Roaming/'+i['Name']), "Rule":getRule(i['Name'],dir)})
    return result


@app.route('/api/import', methods=['POST'])
def import_rule():
    adress = request.form.get('rule')
    try:
        r = requests.get(adress)
    except:
        return 'Invalid adress'
    if isJson(r.text) == False:
        return 'Invalid json'
    if json.loads(r.text).get('Info') is None:
        return 'Invalid rule'
    with open(os.getcwd()+'/rules/'+str(int(time.time()))+'.json', 'w') as f:
        f.write(r.text)
    return 'OK'


def getRule(filename,dir = 'Roaming'):
    path = os.getcwd()+'/rules'
    for file in os.listdir(path):
        with open(path+'/'+file, 'r', encoding='utf-8') as f:
            rule = json.loads(f.read())
            if rule.get(dir) is not None:
                for i in rule[dir]:
                    if i['name'] == filename:
                        return {"Intro":i['intro'],"Suggestion":i['suggestion']}
    return {}


def isJson(data):
    try:
        json.loads(data)
    except ValueError:
        return False
    return True


@app.route('/api/getrules', methods=['GET'])
def getrules():
    result = []
    path = os.getcwd()+'/rules'
    for file in os.listdir(path):
        with open(path+'/'+file, 'r', encoding='utf-8') as f:
            rule = json.loads(f.read())
            result.append({"Name":rule['Info']['Name'],"Author":rule['Info']['Author'],"Version":rule['Info']['Version'], "Description":rule['Info']['Description'], "SourceName":file})
    return result


@app.route('/api/getrule', methods=['POST'])
def getrule():
    item = eval(request.form.get('item'))
    result = 'Output of rules:'
    try:
        for i in item:
            with open(os.getcwd()+'/rules/'+i['sourceName'], 'r', encoding='utf-8') as f:
                result = result +'\n\n'+ f.read()
    except:
        return 'rule not found'
    return result


@app.route('/api/deleterule', methods=['POST'])
def deleterule():
    item = eval(request.form.get('item'))
    for i in item:
        os.remove(os.getcwd()+'/rules/'+i['sourceName'])
    return 'OK'


@app.route('/api/submitrule', methods=['POST'])
def submitrule():
    sourceName = request.form.get('sourceName')
    rule = request.form.get('rule')
    if isJson(rule) == False:
        return 'Invalid json'
    if json.loads(rule).get('Info') is None:
        return 'Invalid rule'
    if sourceName is not None:
        with open(os.getcwd()+'/rules/'+sourceName, 'w', encoding='utf-8') as f:
            f.write(rule)
    else:
        with open(os.getcwd()+'/rules/'+str(int(time.time()))+'.json', 'w', encoding='utf-8') as f:
            f.write(rule)
    return 'OK'


if __name__ == '__main__':
    app.run(debug=False)
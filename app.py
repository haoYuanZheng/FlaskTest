from flask import Flask, request, render_template, redirect, url_for, jsonify
# 确保文件线程安全
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
# 最大文件限制目前为3M
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
# 上传文件允许类型
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])
# 存储地址
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# 标签文件开头地址
app.config['LABEL_FILE_HEAD'] = '/images/'
# 编码问题
app.config['JSON_AS_ASCII'] = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # 多文件上传先遍历
        for file in request.files.getlist('file'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'] + "images/", filename))
                # 当为post请求时保存文件并刷新页面
            else:
                return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、jpg、jpeg、gif"})
        return redirect(url_for('upload'))
    else:
        return render_template('upload.html')


@app.route("/view", methods=['POST'])
def view():
    # 项目系统目录，防止放入镜像时路径错误
    rootdir = app.root_path + "/static/uploads/images"
    picutres = {}
    for filenames in os.walk(rootdir):
        if filenames is not None:
            names = filenames[2]
            break
    if names is not None:
        for name in names:
            picutres[name] = "static/uploads/images/" + name
    return json.dumps(picutres)


@app.route("/viewTwo", methods=['POST'])
def viewTwo():
    # 项目系统目录，防止放入镜像时路径错误
    rootdir = app.root_path + "/static/uploads"
    labels = {}
    for filenames in os.walk(rootdir):
        if filenames is not None:
            names = filenames[2]
            break
    if names is not None:
        for name in names:
            fileType = name.split(".")[1]
            if fileType == "txt":
                labels['label_file_name'] = name
            elif fileType == "class":
                labels['class_file_name'] = name
    return json.dumps(labels)


@app.route("/saveLabel", methods=['POST'])
def saveLabel():
    class_set = set()
    returnDic = {}
    rootAddress = app.config['LABEL_FILE_HEAD']
    data = json.loads(request.form.get('data'))
    labelName = json.loads(request.form.get('labelName'))
    labelFileName = json.loads(request.form.get("labelFileName"))
    classFileName = json.loads(request.form.get("classFileName"))
    hasClassFile = json.loads(request.form.get("hasClassFile"))
    if data[0] is not None:
        data[0] = rootAddress + data[0]
    try:
        # 读取原先的内容
        if hasClassFile == 1:
            with open(app.config['UPLOAD_FOLDER'] + classFileName, 'r') as f1:
                old = f1.read().split("\n")
                for o in old:
                    class_set.update(o)
        else:
            pass
        # 新提交的内容
        for label in labelName:
            class_set.update(label)
        with open(app.config['UPLOAD_FOLDER'] + classFileName, 'w') as f3:
            for c in sorted(class_set):
                f3.write(c + '\n')
        with open(app.config['UPLOAD_FOLDER'] + labelFileName, 'a+') as f2:
            content = "".join(data) + "\n"
            f2.write(content)
    finally:
        f3.close()
        f2.close()
    returnDic['label'] = labelFileName
    returnDic['class'] = classFileName
    return json.dumps(returnDic)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

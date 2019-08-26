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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # 当为post请求时保存文件并刷新页面
            else:
                return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、jpg、jpeg、gif"})
        return redirect(url_for('upload'))
    else:
        return render_template('upload.html')


@app.route("/view", methods=['POST'])
def view():
    # 项目系统目录，防止放入镜像时路径错误
    rootdir = app.root_path + "/static/uploads"
    picutres = {}
    for filenames in os.walk(rootdir):
        if filenames is not None:
            names = filenames[2]
            break
    if names is not None:
        for name in names:
            # picutres[name] = rootdir + "/" + name
            picutres[name] = "static/uploads/" + name
    return json.dumps(picutres)


@app.route("/saveLabel", methods=['POST'])
def saveLabel():
    realData = []
    rootAddress = app.root_path + "/static/uploads/"
    data = json.loads(request.form.get('data'))
    for d in data:
        d = rootAddress + d
        realData.append(d)
    # 此处用w+无法实现读取，只能先r读取后再w
    try:
        with open('label_list.json', 'r') as f1:
            oldData = f1.read()
            if oldData is not None and oldData != "":
                old = json.loads(oldData)
                for o in old:
                    realData.append(o)
    finally:
        f1.close()
    try:
        with open('label_list.json', 'w') as f2:
            content = json.dumps(realData)
            f2.write(content)
    finally:
        f2.close()
    return json.dumps(realData)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

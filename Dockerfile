FROM python:3.7

WORKDIR /Users/zhenghaoyuan/PycharmProjects/PictureHandle

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python", "app.py"]
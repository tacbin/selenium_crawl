FROM tacbin123/selenium_crawl:1.0

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

ENV TZ Asia/Shanghai

#CMD tail -f /dev/null
CMD chmod +x ./geckodriver && \
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    python3 main.py
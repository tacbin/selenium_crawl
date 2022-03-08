FROM tacbin123/selenium_crawl:1.0

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

#CMD tail -f /dev/null
CMD pip3 install -r requirements.txt && \
    python3 main.py
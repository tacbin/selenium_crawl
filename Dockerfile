FROM ubuntu:bionic

RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    python3 python3-pip \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip wget \
    xvfb

# install geckodriver and firefox
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.23.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin/ &&  \
    chmod +x /usr/local/bin/geckodriver

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP

# install phantomjs
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar -jxf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs && \
    rm phantomjs-2.1.1-linux-x86_64.tar.bz2

#RUN pip

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

#CMD tail -f /dev/null
CMD pip3 install -r requirements.txt && \
    python3 main.py
FROM tacbin123/selenium_crawl:1.0

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

# 在安装tzdata之前最好先update和upgrade，以防apt-get获取不到tzdata
RUN apt-get update -y && apt-get upgrade -y
# 安装，中国用户填写[Asia/Shanghai] ，表示亚洲/上海 ，东八区
RUN apt update \
    && apt install -y tzdata \
    && ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

#CMD tail -f /dev/null
CMD chmod +x ./geckodriver && \
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    python3 main.py
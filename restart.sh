#crontab -e
# 每天10:30执行
#30 10 * * * restart.sh
docker container stop selenium-crawler && docker container rm selenium-crawler && d docker run -d -p 5000:5000 --restart unless-stopped --name  selenium-crawler tacbin-docker.pkg.coding.net/town/tacbin-docker/selenium-crawl:master-ac7400ffeb3d2c84edc9c7f1ca50c502bb1482a5
sudo apt install python3.12-venv
python3 -m venv venv
source venv/bin/activate
pip install beautifulsoup4
pip install requests
pip install woocommerce
pip install selenium
pip install webdriver-manager

docker install
create network
docker run -d -p 4444:4444 --net selenium-grid-network --name selenium-hub selenium/hub:4.25.0
docker run -d --net selenium-grid-network --shm-size="2g" \ -e SE_EVENT_BUS_HOST="selenium-hub" \ -e SE_EVENT_BUS_PUBLISH_PORT="4442" \ -e SE_EVENT_BUS_SUBSCRIBE_PORT="4443" \ selenium/node-chrome:4.25.0

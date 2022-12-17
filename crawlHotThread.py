import os
import json
import sys
from datetime import datetime, tzinfo
import pytz

from seleniumwire import webdriver  # Import from seleniumwire
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire.utils import decode

type = sys.argv[1]
if type not in ['now', 'daily', 'weekly']:
    raise ValueError("Please include [now], [daily] or [weekly] as argument")

print(f"Crawl type: {type}")

chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--remote-debugging-port=9222",
    "user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0" # fake user agent
]
for option in options:
    chrome_options.add_argument(option)

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

url = f'https://lihkg.com/category/2?type={type}'

print(f"url: {url}")

# Go to the Google home page
driver.get(url)

# Access requests via the `requests` attribute
for request in driver.requests:
    print(request.url)
    if "/thread/hot" in request.url and request.response:
        # Get current datetime in UTC
        utc_now_dt = datetime.now(tz=pytz.UTC).strftime("%Y%m%d_%H%M%S")
        print(f"Request: {request.url}")
        print(f"Response code: {request.response.status_code}, current time: {utc_now_dt}")
        
        # decode an encoded response body
        decoded_body = decode(
            request.response.body,
            request.response.headers.get('Content-Encoding', 'identity'))

        # decode bytes object to a string
        json_str = decoded_body.decode('utf-8')

        # convert json string to dictionary
        data = json.loads(json_str)
        print(f"Response decoded successful")

        file_name = os.path.join(type, f'{utc_now_dt}.json')
        dirname = os.path.dirname(file_name)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False))

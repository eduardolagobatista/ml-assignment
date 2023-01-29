
from threading import Thread
import requests
import time
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--pay-size', help='Number of records on each request', default=1, type=int)
parser.add_argument('--num-req', help='Number of requests to make to the endpoint', default=100, type=int)
parser.add_argument('--sleep', help='Interval to wait between requests', default=0.05, type=float)
args = parser.parse_args()

API_URL = "http://127.0.0.1:9527/translation"
PAYLOAD_SIZE = args.pay_size
NUM_REQUESTS = args.num_req
SLEEP_COUNT = args.sleep
RES_TIME = []
SUCCESS_REQUESTS = []


def call_predict_endpoint(n):
    payload = {"payload": {"fromLang": "ja","records": [{"id": "125","text": "人生はチョコレートの箱のようなものだ。"}]*PAYLOAD_SIZE,"toLang": "en"}}
    headers = {'content-type': 'application/json'}
    st = time.time()
    r = requests.post(API_URL, data=json.dumps(payload), headers=headers)
    if r.status_code == 200 and len(r.json()['result'])==PAYLOAD_SIZE:
        print("[INFO] thread {} OK".format(n), r.json())
        RES_TIME.append(time.time()-st)
        SUCCESS_REQUESTS.append(1)
    else:
        print("[INFO] thread {} FAILED".format(n))

threads = [Thread(target=call_predict_endpoint, args=(i,)) for i in range(NUM_REQUESTS)]
for t in threads:
    t.start()
    time.sleep(SLEEP_COUNT)
for t in threads:
    t.join()

print(f'{len(SUCCESS_REQUESTS)/args.num_req*100:.2f}% of requests were successfull with average of {sum(RES_TIME)/len(RES_TIME):.2f}s, minimum of {min(RES_TIME):.2f}s and maximum of {max(RES_TIME):.2f}s response time')
import time
import json
import redis

if __name__ == "__main__":
    r = redis.StrictRedis()
    while True:
        r.publish('channelName', json.dumps({'field1': 1, 'field2': '2'}).encode('utf-8'))
        time.sleep(1)

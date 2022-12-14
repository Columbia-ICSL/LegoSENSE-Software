import json
import threading
import redis

class Listener(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.redis = redis.StrictRedis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.psubscribe('*')  # "*" to subscribe everything

    def run(self):
        for m in self.pubsub.listen():
            if 'pmessage' != m['type']:
                continue
            ch_name = m["channel"].decode('utf-8')
            ch_data = m['data'].decode('utf-8')
            print(f'[{ch_name}] {ch_data}')

if __name__ == "__main__":
    r = redis.StrictRedis()
    client = Listener()
    client.start()

    # r.publish('channel1', 'message1')
    # r.publish('channel2', 'message2')
    # r.publish('channel1', 'message3')

    # r.publish('__admin__', 'shutdown')
    # print('Main ended.')
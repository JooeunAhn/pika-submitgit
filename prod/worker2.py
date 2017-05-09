import os
import pika
import time
import json
import requests as rq

_secrets = {}
_secret_path = os.path.join(os.path.dirname(__file__), 'secret.json')

if os.path.exists(_secret_path):
    with open(_secret_path) as f:
        _secrets = json.loads(f.read())

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=_secrets["QUEUE_NAME"], durable=True)
print('worker [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print("worker [x] Received %r" % body)
    data = json.loads(body)
    res = rq.post(_secrets["EUROPA_2_URL"], data=data)
    res_data = json.loads(res.text)
    res_api = rq.post(_secrets["SERVER_API_URL"], data=res_data)
    print("worker [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=_secrets["QUEUE_NAME"])

channel.start_consuming()

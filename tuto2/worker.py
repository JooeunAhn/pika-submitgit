import pika
import time
import json

import requests as rq

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print('worker [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print("worker [x] Received %r" % body)
    time.sleep(body.count(b'.'))
    print("worker [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()

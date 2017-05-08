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
    data = json.loads(body)
    res = rq.post("http://52.79.205.59/compile/", data=data)
    res_data = json.loads(res.text)
    res_api = rq.post("http://submitgit-stella.ap-northeast-2.elasticbeanstalk.com/api/v1/test/", data=res_data)
    print("worker [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()

import os
import pika
import json

_secrets = {}
_secret_path = os.path.join(os.path.dirname(__file__), 'secret.json')
if os.path.exists(_secret_path):
    with open(_secret_path) as f:
        _secrets = json.loads(f.read())

credential = pika.PlainCredentials(_secrets['RQ_ID'], _secrets['RQ_PASSWORD'])
parameters = pika.ConnectionParameters(_secrets['RQ_IP'],
                                       5672,
                                       '/',
                                       credential)

connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.queue_declare(queue=_secrets['QUEUE_NAME'], durable=True)

# message = ' '.join(sys.argv[1:]) or "Hello World!"
data = {"id": 3, "code": "print 'Hello112!'", "language": 0,
        "stdin": "", "time": 2,
        "is_test": 'True', 'output': "Hello112!\n"}


message = json.dumps(data)

channel.basic_publish(exchange='',
                      routing_key=_secrets['QUEUE_NAME'],
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2,  # make message persistent
                      ))
print(" [x] Sent %r" % (message))

connection.close()

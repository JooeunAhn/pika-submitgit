import pika
import sys
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

#message = ' '.join(sys.argv[1:]) or "Hello World!"
data={"id": 3, "code": "print 'Hello12!'", "language": 0, "stdin": "", "time": 2, 
      "is_test": 'True', 'output': "Hello12!\n"}


message = json.dumps(data)

channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % (message))

connection.close()

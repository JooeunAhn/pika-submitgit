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


check_time_out = lambda limit_t, actual_t: limit_t >= actual_t


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=_secrets["QUEUE_NAME"], durable=True)
print('worker [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print("worker [x] Received %r" % body)
    origin_data = json.loads(body)

    europa_post_data = {}
    europa_post_data["language"] = origin_data['language']
    europa_post_data["code"] = origin_data['code']
    europa_post_data["stdin"] = origin_data["stdin"]
    europa_post_data["time"] = origin_data["time"]

    europa_res = rq.post(_secrets["EUROPA_1_URL"], data=europa_post_data)
    europa_res_data = json.loads(europa_res.text)

    data = {}
    
    data["langid"] = europa_res_data["langid"]
    data["code"] = europa_res_data["code"]
    data["output"] = europa_res_data["output"]
    data["time"] = europa_res_data["time"]

    if "errors" in europa_res_data:
        data['errors'] = europa_res_data['errors']
    else:
        data['errors'] = "Execution Timed Out!!"
   
    data['has_error'] = check_time_out(origin_data['time'],
                                       data['time'])
    
    if data['errors'] != '':
        data['has_error'] = True

    if origin_data['is_test']:
        if (origin_data['output'] == data["output"]) and (not data['has_error']):
            data['is_passed'] = True
    else:
        if data['has_error'] is False:
            data['is_passed'] = True 
    
    data['is_working'] = False
     
    res_api = rq.patch(_secrets["SERVER_API_URL"]+"%d/" % origin_data['id'], 
                      data=data,
                      headers={"Authorization": _secrets["SERVER_ADMIN_TOKEN"]})
    print(res_api.text)
    print("worker [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue=_secrets["QUEUE_NAME"])

channel.start_consuming()

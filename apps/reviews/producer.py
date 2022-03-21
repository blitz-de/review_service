try:
    import pika

except Exception as e:
    print("Some Modules are missings {}".format_map(e))

import json
class MetaClass(type):

    _instance ={}

    def __call__(cls, *args, **kwargs):

        """ Singelton Design Pattern  """

        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class RabbitmqConfigure(metaclass=MetaClass):
# publish to user_profiles
    def __init__(self, queue='user_profiles', host='amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj?heartbeat=300',
                 routingKey='user_profiles', exchange=''):
        """ Configure Rabbit Mq Server  """
        self.queue = queue
        self.host = host
        self.routingKey = routingKey
        self.exchange = exchange


class RabbitMq():

    def __init__(self):

        # self.server = server

        self._connection = pika.BlockingConnection(pika.URLParameters
        ('amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj?heartbeat=300'))
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue="profiles")
    # def publish(method, body):
    def publish(self, method, body):
        properties = pika.BasicProperties(method)
        self._channel.basic_publish(exchange="",
                                    routing_key="profiles",
                                    body=json.dumps(body), properties=properties)

        print("Published Message: {}".format(body), "--> ", properties.content_type)
        # self._connection.close()


if __name__ == "__main__":
    server = RabbitmqConfigure(queue='profiles',
                               host='amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj?heartbeat=300',
                               routingKey='review_service',
                               exchange='')

    rabbitmq = RabbitMq()
    # rabbitmq.publish()


# # amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj
# import json
#
# import pika
#
# params = \
#     pika.URLParameters('amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj')
#
# connection = pika.BlockingConnection(params)
#
# channel = connection.channel()
# channel.queue_declare(queue='review_service')
#
# def publish(method, body):
#     properties = pika.BasicProperties(method)
#     # routing key, for the consumer to know whom it's coming from
#     channel.basic_publish(exchange='', routing_key='review_service',
#                           body=json.dumps(body), properties=properties)

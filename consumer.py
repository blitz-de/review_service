try:
    import pika, json, os, django
    import ast

except Exception as e:
    print("Some modules are missings {}".format(e))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "review_service.settings.development")
django.setup()

from apps.reviews.models import Rater, RatedUser


class MetaClass(type):

    _instance ={}

    def __call__(cls, *args, **kwargs):

        """ Singelton Design Pattern  """

        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class RabbitMqServerConfigure(metaclass=MetaClass):

    def __init__(self, host='amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj',
                 queue='review_service'):

        """ Server initialization   """

        self.host = host
        self.queue = queue




def change_logged_status(is_signed):
    return is_signed

class rabbitmqServer():

    def __init__(self, server):

        """
        :param server: Object of class RabbitMqServerConfigure
        """
        self.server = server
        self._connection = pika.BlockingConnection(pika.URLParameters(self.server.host))
        self._channel = self._connection.channel()
        self._tem = self._channel.queue_declare(queue=self.server.queue)
        print("Server started waiting for Messages ")
    #
    # def __init__(self):
    #     self.signed_status = ""

    @staticmethod
    def callback(ch,method, properties, body):
        print('Received in review_service')
        print("####################@##########################################")
        # print(body) --> this will print b'"\\"UUID"
        data = json.loads(body)
        print(data)

        print("!!!!!!!!!!", data['username'])
        # id = uuid.UUID(data['id']).hex
        print("!!%!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("14$!%%$%%@%#%!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!@%!: ", properties.content_type)
        if properties.content_type == 'profile_created':
            print("Information about the id and username: Id:", data['id'], " username: ", data['username'])
            # user_profile = data['id']
            user_exists = Rater.objects.filter(username=data['username']).exists()

            if user_exists == False:
                rater = Rater.objects \
                    .create(username=data['username'])
                # rated_user = RatedUser.objects\
                #     .create( username=data['username'])
                rater.save()
                # rated_user.save()
                print("Rater and rated user Profiles have been created")
            else:
                print("User already saved")

        if properties.content_type == 'user_signed':
            print("User just signed in !!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # add email address
            print("The username should be: ", data['username'])
            rater = Rater.objects.get(username=data['username'])
            print("33424 ", data['logged_status'] )
            if data['logged_status'] == "False":
                rater.is_signed = False
                rater.save()

                ch.change_logged_status("False")


                print("Rater just signed out")
            elif data['logged_status'] == "True":
                rater.is_signed = True
                rater.save()
                ch.change_logged_status("False")
                print("Rater just signed in")
            # add email to model

        # if user signs out rater.is_signed = False

    def startserver(self):
        self._channel.basic_consume(
            queue=self.server.queue,
            on_message_callback=rabbitmqServer.callback,
            auto_ack=True)
        self._channel.start_consuming()


if __name__ == "__main__":
    serverconfigure = RabbitMqServerConfigure(host='amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj',
                                              queue='review_service')

    server = rabbitmqServer(server=serverconfigure)
    server.startserver()



# # amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj
# import functools
# import json, django, os, pika, threading
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "review_service.settings.development")
# django.setup()
#
# from apps.reviews.models import UserProfile
#
# params = pika.URLParameters('amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj')
#
# connection = pika.BlockingConnection(params)
#
# channel = connection.channel()
#
#
# # queue --> review_service
# channel.queue_declare(queue='review_service')
#
# def callback(ch, method, properties, body):
#     print('Received in review_service')
#     print("####################@##########################################")
#     # print(body) --> this will print b'"\\"UUID"
#     data = json.loads(body)
#     print(data)
#
#     print("!!!!!!!!!!", data['id'])
#     # id = uuid.UUID(data['id']).hex
#     if properties.content_type == 'profile_created':
#         print("Information about the id and username: Id:", data['id'], " username: ", data['username'])
#         # user_profile = data['id']
#
#         user_profile = UserProfile.objects.create(id=data['id'],
#                                                   username=data['username'])
#         user_profile.save()
#
#         print("Users Profile created")
#
#
# channel.basic_consume(queue='review_service', on_message_callback=callback, auto_ack=True)
# channel.start_consuming()
#
# print('Started Consuming')
#
# channel.close()
#

from review_service.settings.base import env

try:
    import pika, json, os, django
    import ast

except Exception as e:
    print("Some modules are missings {}".format(e))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "review_service.settings.development")
django.setup()

from apps.reviews.models import Rater


class MetaClass(type):

    _instance ={}

    def __call__(cls, *args, **kwargs):

        """ Singelton Design Pattern  """

        if cls not in cls._instance:
            cls._instance[cls] = super(MetaClass, cls).__call__(*args, **kwargs)
            return cls._instance[cls]


class RabbitMqServerConfigure(metaclass=MetaClass):

    def __init__(self, host=env("RABBITMQ_HOST"),
                 queue='review_service'):

        """ Server initialization   """

        self.host = host
        self.queue = queue


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


    @staticmethod
    def callback(ch,method, properties, body):
        print('Received in review_service')
        data = json.loads(body)
        print(data)

        if properties.content_type == 'profile_created':
            print("Information about the id and username: Id:", data['id'], " username: ", data['username'])
            user_exists = Rater.objects.filter(username=data['username']).exists()

            if data['username'].startswith('test'):
                print("A test user has been received. It won't be saved")
            else:
                if user_exists == False:
                    rater = Rater.objects \
                        .create(username=data['username'])
                    if data['is_admin'] == 'True':
                        rater.is_admin = True
                        rater.save()
                        print('Rater has been created and is an admin user')
                    rater.save()
                    print("Rater and rated user Profiles have been created")
                else:
                    print("User already saved")

        if properties.content_type == 'user_signed':
            print("User ", data['username'], "just signed in")
            rater = Rater.objects.get(username=data['username'])

            if data['logged_status'] == "False":
                rater.is_signed = False
                rater.save()
                print("Rater just signed out")

            elif data['logged_status'] == "True":
                if rater.is_signed == True:
                    print ("User is already signed. You must logout first")
                rater.is_signed = True
                rater.save()
                print("Rater just signed in")

        if properties.content_type == 'user_deleted':
            rater = Rater.objects.get(username=data['username'])
            rater.delete()
            print("User ", data['username'], "has been deleted")

    def startserver(self):
        self._channel.basic_consume(
            queue=self.server.queue,
            on_message_callback=rabbitmqServer.callback,
            auto_ack=True)
        self._channel.start_consuming()


if __name__ == "__main__":
    serverconfigure = RabbitMqServerConfigure(host=env("RABBITMQ_HOST"),
                                              queue='review_service')

    server = rabbitmqServer(server=serverconfigure)
    server.startserver()

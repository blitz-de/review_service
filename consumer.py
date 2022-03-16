# amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj
import functools
import json, django, os, pika, threading

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "review_service.settings.development")
django.setup()

from apps.reviews.models import UserProfile

params = pika.URLParameters('amqps://dowzsxzj:UT7_s888elZ3FCRdD1CjiHY9S9aQPI81@cow.rmq2.cloudamqp.com/dowzsxzj')

connection = pika.BlockingConnection(params)

channel = connection.channel()


# queue --> review_service
channel.queue_declare(queue='review_service')

def callback(ch, method, properties, body):
    print('Received in review_service')
    print("####################@##########################################")
    # print(body) --> this will print b'"\\"UUID"
    data = json.loads(body)
    print(data)

    print("!!!!!!!!!!", data['id'])
    # id = uuid.UUID(data['id']).hex
    if properties.content_type == 'profile_created':
        print("Information about the id and username: Id:", data['id'], " username: ", data['username'])
        # user_profile = data['id']

        user_profile = UserProfile.objects.create(id=data['id'],
                                                  username=data['username'])
        user_profile.save()

        print("Users Profile created")


channel.basic_consume(queue='review_service', on_message_callback=callback, auto_ack=True)
channel.start_consuming()

print('Started Consuming')

channel.close()


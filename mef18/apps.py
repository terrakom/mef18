from django.apps import AppConfig
import wapps.mef18.kafka_utils as kafka_utils

class Mef18Config(AppConfig):
    name = 'mef18'
    server = "localhost:9092"
    group_id = "warrior"
    topics = ["test"]
    consumer = kafka_utils.start_consumer(server, group_id, topics)

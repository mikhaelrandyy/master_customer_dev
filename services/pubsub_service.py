# Publish to Pub/Sub
from google.cloud import pubsub_v1
import json
from configs.config import settings
from google.oauth2 import service_account
import crud
import asyncio

class PubSubService:
    __projectId: str

    def __init__(self, projectId: str = settings.PROJECT_NAME):
        self.__projectId = projectId

    def publish_to_pubsub(self, topic_name, message, action):
        try:
            # message.updated_at = None
            # message.created_at = None
            if topic_name != "master-customerdevgroup":
                delattr(message, "updated_at")
                delattr(message, "created_at")
            message_dict = message.dict()
            message_dict['action'] = action
            if topic_name != "master-customerdevgroup":
                message_dict['id'] = message.id
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(
                self.__projectId, topic_name + settings.PUBSUB_SUFFIX)
            message_data = json.dumps(
                message_dict, indent=4, sort_keys=True, default=str).encode("utf-8")
            future = publisher.publish(topic_path, data=message_data)
            print(f"Published message ID: {future.result()}")
        except Exception as e:
            print(e)


pubSubService = PubSubService()

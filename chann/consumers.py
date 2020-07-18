import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'users',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'users',
            self.channel_name
        )

        pass

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=json.dumps({
            'message': "hello"
        }))

    def new_pixel(self, content):
        self.send(text_data=json.dumps(content['content'].decode("utf-8")))

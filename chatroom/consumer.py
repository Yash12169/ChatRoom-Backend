# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save the message to the database or handle it as needed
        # Then send the message back to other clients
        await self.send(text_data=json.dumps({'message': message}))

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({'message': message}))


def send_realtime_message(sender, receiver, content):
    channel_layer = get_channel_layer()
    room_name = f"chat_{receiver.id}"

    async def send():
        await channel_layer.group_send(
            room_name,
            {
                'type': 'chat.message',
                'message': json.dumps({'sender': sender.id, 'content': content}),
            }
        )

    async_to_sync(send)()

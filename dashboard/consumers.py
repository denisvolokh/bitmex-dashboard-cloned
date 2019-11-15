from django.conf import settings
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer

import asyncio
import json
from asgiref.sync import async_to_sync
import channels.layers

class TicksSyncConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("[+] Web Socket Connected!")

        await self.accept()

        # Join ticks group
        # async_to_sync(self.channel_layer.group_add)(
        #     settings.TICKS_GROUP_NAME,
        #     self.channel_name
        # )

    # async def websocket_disconnect(self, event):
        # print("[+] Web Socket Disconnected!", event)

    async def notify(self, event):
        await self.send_json(event["content"])

    async def receive_json(self, content, **kwargs):
        print("[+] Web Socket Receive!", content)

        if "subscribe" in content:
            group_name = content["subscribe"]

            self.groups.append(group_name)
            await self.channel_layer.group_add(
                group_name,
                self.channel_name,
            )

        print(f"[+] Adding group: {group_name} Channel: {self.channel_name}")

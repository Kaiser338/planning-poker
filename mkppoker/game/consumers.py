import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .game_group_manager import GameGroupManager
from .event_types import EventType

class GameConsumer(GameGroupManager, AsyncWebsocketConsumer):
    """
    WebSocket consumer for managing game-related communication.

    This consumer extends both the GameManager and AsyncWebsocketConsumer classes
    to handle game-specific functionality and WebSocket communication.

    Attributes:
        - `game_id`: An identifier for the game.
        - `game_group_name`: The name of the WebSocket group associated with the game.
        - `channel_name`: The name of the channel associated with the WebSocket connection.

    Methods:
        - `connect`: Connect to the game group, add the channel to the group, and accept the connection.
        - `disconnect`: Remove the channel from the group upon disconnection.
        - `receive`: Receive a message from the WebSocket, process it, and broadcast it to the game group.
    """

    # Connect to the game group, add the channel to the group and accept the connection
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.game_group_name = f"game_{self.game_id}"

        self.create_group(self.game_group_name, self.channel_name)

        await self.channel_layer.group_add(self.game_group_name, self.channel_name)
        await self.accept()

    # Remove the channel from the group
    async def disconnect(self, close_code):
        player_list = await self.leave_group(self.game_group_name, self.channel_name, self.game_id)

        if player_list and len(player_list) > 0:
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    "type": "game.leave",
                    "data": {'players': player_list},
                    "username": "None",
                    "isOwner": False,
                    "channel_name": self.channel_name,
                },
            )

        await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    # Receive a message from the WebSocket
    async def receive(self, text_data):
        event = json.loads(text_data)

        username = event["username"]
        data = event["data"]
        event_type = event["type"]

        if event_type == EventType.GAME_JOIN.value:
            self.join_group(self.game_group_name, self.channel_name, username)

        is_owner = self.is_user_owner_of_group(
            self.game_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.game_group_name,
            {
                "type": event_type,
                "data": data,
                "username": username,
                "isOwner": is_owner,
                "channel_name": self.channel_name,
            },
        )

    # Event for joining the game
    async def game_join(self, event):
        type = event["type"]
        players_cards = self.get_players_cards(self.game_group_name)

        await self.send(text_data=json.dumps({
            "type": type,
            "data": {'players': players_cards}
        }))

    # Event for leaving the game
    async def game_leave(self, event):
        type = event["type"]
        players_cards = self.get_players_cards(self.game_group_name)

        await self.send(text_data=json.dumps({
            "type": type,
            "data": {'players': players_cards}
        }))

    # Event for starting the game
    async def game_start(self, event):
        type = event["type"]
        players_cards = self.get_players_cards(self.game_group_name)
        isOwner = event["isOwner"]

        if isOwner:
            await self.send(text_data=json.dumps({
                "type": type,
            }))

    # Event for ending the game
    async def game_end(self, event):
        type = event["type"]
        self.set_all_cards_not_selected(self.game_group_name)
        players_cards = self.get_players_cards(self.game_group_name)
        isOwner = event["isOwner"]

        if isOwner:
            await self.send(text_data=json.dumps({
                "type": type,
                "data": players_cards
            }))

    # Event for selecting a card
    async def select_card(self, event):
        type = event["type"]
        username = event["username"]
        card_value = event["data"]
        self.set_player_card_selected(
            self.game_group_name, event["channel_name"], card_value)
        players_cards = self.get_players_cards(self.game_group_name)

        await self.send(text_data=json.dumps({
            "type": type,
            "username": username,
            "data": players_cards
        }))

    # Event for revealing the cards
    async def reveal_cards(self, event):
        type = event["type"]
        players_cards = self.get_players_cards(self.game_group_name)
        if self.are_all_cards_selected(self.game_group_name):
            await self.send(text_data=json.dumps({
                "type": type,
                "data": players_cards
            }))

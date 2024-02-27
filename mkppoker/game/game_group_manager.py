import json
from .models import Game
from channels.db import database_sync_to_async


class GameGroupManager:
    """
    Class for managing game groups and players.

    This class provides functionality for creating, joining, and managing game groups,
    as well as checking the status of a group and handling ownership.

    Attributes:
        - `groups`: A dictionary containing information about active game groups.

    Methods:
        - `create_group`: Create a new game group if it doesn't exist.
        - `join_group`: Add a player to the game group and set the owner if the group is empty.
        - `leave_group`: Remove a player from the game group.
        - `is_user_owner_of_group`: Check if the user is the owner of the game group.
        - `is_group_empty`: Check if the game group has any players.
        - `remove_group`: Remove a game group from the dictionary.
    """

    groups = {}

    # Create a group if it doesn't exist
    def create_group(self, game_group_name, channel_name):
        if game_group_name not in self.groups:
            self.groups[game_group_name] = {
                "owner": channel_name,
                "owner_name": None,
                "players": {},
                "gameStatus": "waiting",
            }
            return True
        return False

    # Add a player to the group and set the owner if it's empty
    def join_group(self, game_group_name, channel_name, username):
        group_info = self.groups.get(game_group_name)

        if group_info and group_info["owner_name"] is None:
            group_info["owner_name"] = username

        group_info["players"][channel_name] = {
            "username": username,
            "cardSelected": None,
        }


    @database_sync_to_async
    def delete_game(self, game_id):
        Game.objects.filter(game_id=game_id).delete()

    # Remove a player from the group
    async def leave_group(self, game_group_name, channel_name, game_id):
        group_info = self.groups.get(game_group_name)
        group_removed = False

        if group_info:
            group_info["players"].pop(channel_name, None)
            if self.is_group_empty(game_group_name):
                self.remove_group(game_group_name)
                group_removed = True
                await self.delete_game(game_id)
        if not group_removed:
            return self.get_player_list(game_group_name)

    # Check if the user is the owner of the group
    def is_user_owner_of_group(self, game_group_name, channel_name):
        return self.groups[game_group_name]["owner"] == channel_name

    # Check if is there any player in the group
    def is_group_empty(self, game_group_name):
        return len(self.groups[game_group_name]["players"]) == 0

    # Remove a group from the dictionary
    def remove_group(self, game_group_name):
        self.groups.pop(game_group_name, None)

    # Get the list of players in the group
    def get_player_list(self, game_group_name):
        group_info = self.groups.get(game_group_name)
        player_list = [player["username"]
                       for player in group_info["players"].values()]
        return player_list

    # Set player card value
    def set_player_card_selected(self, game_group_name, channel_name, card_value):
        group_info = self.groups.get(game_group_name)
        group_info["players"][channel_name]["cardSelected"] = card_value

    # Set all cards to not selected by players
    def set_all_cards_not_selected(self, game_group_name):
        group_info = self.groups.get(game_group_name)
        for player in group_info["players"].values():
            player["cardSelected"] = None

    # Check if all players have selected a card
    def are_all_cards_selected(self, game_group_name):
        group_info = self.groups.get(game_group_name)
        return all(player["cardSelected"] for player in group_info["players"].values())

    # Get the cards selected by the players
    def get_players_cards(self, game_group_name):
        group_info = self.groups.get(game_group_name)
        return {player["username"]: player["cardSelected"] for player in group_info["players"].values()}

import pytest
from game.game_group_manager import GameGroupManager
from game.consumers import GameConsumer
from django.utils.crypto import get_random_string
from .models import Game
from channels.testing import WebsocketCommunicator
from game.consumers import GameConsumer

# Consumer Tests

# Test if the consumer is connected, sends a message and receives a response
@pytest.mark.asyncio
@pytest.mark.django_db
async def test_gameconsumer():
    communicator = WebsocketCommunicator(
        GameConsumer.as_asgi(), "/ws/game/1234/")
    communicator.scope["url_route"] = {"kwargs": {"game_id": "1234"}}
    connected, subprotocol = await communicator.connect()
    assert connected

    # Test sending text
    await communicator.send_json_to({
        "type": "game.join",
        "data": "join_game",
        "username": "test_user"
    })

    response = await communicator.receive_json_from()
    assert response

    await communicator.disconnect()

# Group Tests


@pytest.fixture
def game_manager():
    return GameGroupManager()


@pytest.fixture
def game_consumer(game_manager):
    return GameConsumer()

# Test if the group is created
async def test_create_group(game_manager):
    assert game_manager.create_group("test_group", "test_channel")
    assert not game_manager.create_group("test_group", "test_channel")

# Test if the user is in group after joining it
async def test_join_group(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    assert game_manager.groups["test_group"]["players"]["test_channel"]["username"] == "test_user"

# Test if the user is in group after leaving it
async def test_leave_group(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    game_manager.leave_group("test_group", "test_channel", "123")
    assert "test_channel" not in game_manager.groups

# Test if the user is the owner of the group after creating it
async def test_is_user_owner_of_group(game_manager):
    game_manager.create_group("test_group", "test_channel")
    assert game_manager.is_user_owner_of_group("test_group", "test_channel")

# Test if the group is not empty after adding a player
async def test_is_not_group_empty(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    assert not game_manager.is_group_empty("test_group")


# Test if the group is empty after removing the player
async def test_remove_group(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.remove_group("test_group")
    assert "test_group" not in game_manager.groups

# Model Tests


@pytest.mark.django_db
def test_create_game_with_generated_id():
    # Check if a new Game object is created with a generated game_id
    game = Game.objects.create(password='test_password')
    assert game.game_id is not None
    assert len(game.game_id) == 10  # game_id has a length of 10

# Check if a game can be created with a specified game_id
@pytest.mark.django_db
def test_create_game_with_specific_id():
    specific_id = get_random_string(10, 'abcdefghijklmnoprstuwxyz0123456789')
    game = Game.objects.create(game_id=specific_id, password='test_password')
    assert game.game_id == specific_id

# Check if game_id is unique
@pytest.mark.django_db
def test_unique_game_id():
    game1 = Game.objects.create(password='test_password_1')
    game2 = Game.objects.create(password='test_password_2')
    assert game1.game_id != game2.game_id

# Check if the save method generates game_id if not provided
@pytest.mark.django_db
def test_save_method_generates_game_id():
    game = Game(password='test_password')
    game.save()
    assert game.game_id is not None
    assert len(game.game_id) == 10

# Check if the save method does not change game_id if already provided
@pytest.mark.django_db
def test_save_method_does_not_change_existing_game_id():
    specific_id = get_random_string(10, 'abcdefghijklmnoprstuwxyz0123456789')
    game = Game(game_id=specific_id, password='test_password')
    game.save()
    assert game.game_id == specific_id

# Game Manager Test
    
# Test card selection    
async def test_set_player_card_selected(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    game_manager.set_player_card_selected("test_group", "test_channel", 1)
    assert game_manager.groups["test_group"]["players"]["test_channel"]["cardSelected"] == 1

# Test setting all cards to not selected
async def test_set_all_cards_not_selected(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    game_manager.set_player_card_selected("test_group", "test_channel", 1)
    game_manager.set_all_cards_not_selected("test_group")
    assert game_manager.groups["test_group"]["players"]["test_channel"]["cardSelected"] == None

# Test if all cards are selected
async def test_are_all_cards_selected(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    game_manager.set_player_card_selected("test_group", "test_channel", 1)
    assert game_manager.are_all_cards_selected("test_group")

# Test getting the card selected by the player
async def test_get_players_cards(game_manager):
    game_manager.create_group("test_group", "test_channel")
    game_manager.join_group("test_group", "test_channel", "test_user")
    game_manager.set_player_card_selected("test_group", "test_channel", 1)
    assert game_manager.get_players_cards("test_group") == {"test_user": 1}

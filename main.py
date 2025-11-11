from entities.Player import Player
from entities.Location import Location
from entities.Conversation import Question
from entities.Room import Room
from managers.GameManager import GameManager
import random

def print_menu(player: Player, current_room: Room):
    print(f"You are in the {current_room.name}")
    print(f"{current_room.description}")
    print(f"Your current level of suspicion is: {player.suspicion}")
    print("press 1 to ask question: ")
    print("press 2 to accuse: ")
    print("press 3 to see players in this room")
    print("press 4 to move to another room")
    print("press 0 to quit game")
    
def print_player_list(players: list[Player], show_suspicion: bool = True):
    print("\nPlayers in the room:")
    for idx, player in enumerate(players):
        if show_suspicion:
            print(f"{idx}. {player.name} (Suspicion: {player.suspicion})")
        else:
            print(f"{idx}. {player.name}")
            
def get_player_choice(players: list[Player], action: str) -> Player:
    while True:
        try:
            choice = int(input(f"Select player to {action} (0-{len(players)-1}): "))
            if 0 <= choice < len(players):
                return players[choice]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")
            
def get_room_choice(rooms: list[Room]) -> Room:
    while True:
        try:
            choice = int(input(f"Select room to move to (0-{len(rooms)-1}): "))
            if 0 <= choice < len(rooms):
                return rooms[choice]
            else:
                print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a number.")


def register_user_player(location: Location) -> Player:
    print(f"Welcome to {location.name}")
    print(f"{location.description}\n")
    name = input("What do you wish to be called?\n:> ")
    #the user player will have id 0 and always be the first in the list in phase 1 and 2
    return Player(0, name, 0)

def generate_location() -> Location:
    location_names_with_descriptions = {
        "Haunted Manor": "An old manor at the edge of the city, surrounded by dead trees with pre-victorian furniture. While the outside looks fairly unkempt the inside is clean and luxurious."
    }
    event_descriptions = ["You were called here by a friend for a masked ball. When you get here, you find commotion, and a man has been killed. You must find out what has happened and who did it."]
    
    possible_rooms = [
        Room("Entrance", "A luxurious hallway, which serves as the place where people may leave their clothes before entering the house proper."),
        Room("Ball Room", "A beautiful room with large hanging candelabras. Music is coming from a pickup in the corner. The room has columns ornate with marble roses, and the flooring is made of golden marble."),
        Room("Garder", "A rose Garden with a large labyrinth and marble statues of wemen, soldiers and hystorical figures.")
    ]
    real_location_name, real_location_description = random.choice(list(location_names_with_descriptions.items()))
    location_event = random.choice(event_descriptions)
    # in the future I would like there to be more rooms
    location = Location(real_location_name, real_location_description, 10, location_event, possible_rooms)
    return location

def run_game(game_manager: GameManager):

    while game_manager.game_state_manager.is_game_active():
        print_menu(game_manager.user_player, game_manager.get_current_room())
        choice = input("Enter your choice: ")
        if choice == "0":
            print("Quitting game.")
            break
        elif choice == "1":
            
            print("Asking question...")
            print("Who to ask?: ")  
            players = game_manager.player_manager.get_other_players_in_room(game_manager.get_current_room(), game_manager.user_player)
            print_player_list(players, show_suspicion=True)
            selected_player = get_player_choice(players, "question")
            
            question = input("Enter your question:> ")
            
            conversation: Question = Question(
                game_manager.user_player,
                selected_player,
                question,
            )
            response, suspicion_change_speaker, suspicion_change_listener = game_manager.strike_conversation(conversation)
            print(f"\n{selected_player.name} says: {response}")
            if suspicion_change_speaker != 0 or suspicion_change_listener != 0:
                print("\nSuspicion changes:")
                if suspicion_change_speaker != 0:
                    change_text = "increased" if suspicion_change_speaker > 0 else "decreased"
                    print(f"  Your suspicion {change_text} by {abs(suspicion_change_speaker)}")
                if suspicion_change_listener != 0:
                    change_text = "increased" if suspicion_change_listener > 0 else "decreased"
                    print(f"  {selected_player.name}'s suspicion {change_text} by {abs(suspicion_change_listener)}")
                            
        elif choice == "2":
            print("Accusing player...")
            print("Who to accuse?: ")
            players = game_manager.player_manager.get_other_players_in_room(game_manager.get_current_room(), game_manager.user_player)
            print_player_list(players, show_suspicion=True)
            accused = get_player_choice(players, "accuse")
            if game_manager.accuse_player(game_manager.user_player, accused):
                print(f"Correct! {accused.name} was the murderer!")
                print("You solved the mystery!")
            else:
                print(f"Wrong accusation! {accused.name} is not the murderer.")
                print("Your suspicion has increased massively!")
            
        elif choice == "3":
            players = game_manager.player_manager.get_other_players_in_room(game_manager.get_current_room(), game_manager.user_player)
            print_player_list(players, show_suspicion=True)
        
        elif choice == "4":
            print("Moving to another room")
            rooms = game_manager.get_rooms()
            room_choice = get_room_choice(rooms)
            game_manager.move_player(game_manager.user_player, room_choice)
            
        else:
            print("Invalid choice, please try again.")

def main():
    location: Location = generate_location()
    user_player: Player = register_user_player(location)
    game_manager: GameManager = GameManager(location, user_player)
    run_game(game_manager)

if __name__ == "__main__":
    main()
from entities.Player import Player
from entities.Location import Location
from entities.Conversation import Question
from managers.GameManager import GameManager
import random

def print_menu():
    print("press 1 to ask question: ")
    print("press 2 to accuse: ")
    print("press 3 to see players")
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


def register_user_player(location: Location) -> Player:
    print(f"Welcome to {location.name}")
    print(f"{location.description}\n")
    name = input("What do you wish to be called?\n:> ")
    #the user player will have id 0 and always be the first in the list in phase 1 and 2
    return Player(0, name, 0)

def run_game(game_manager: GameManager):

    while game_manager.game_state.game_active:
        print_menu()
        choice = input("Enter your choice: ")
        if choice == "0":
            print("Quitting game.")
            break
        elif choice == "1":
            
            print("Asking question...")
            print("Who to ask?: ")  
            players = game_manager.get_other_players_in_room(game_manager.get_current_room())
            print_player_list(players, show_suspicion=True)
            selected_player = get_player_choice(players, "question")
            
            question = input("Enter your question:> ")
            
            conversation: Question = Question(
                game_manager.user_player,
                selected_player,
                question,
            )
            response, suspicion_change = game_manager.strike_conversation(conversation)
            game_manager.conversation_history.append(conversation)
            print(f"\n{selected_player.name} says: {response}")
            if suspicion_change != 0:
                change_text = "increased" if suspicion_change > 0 else "decreased"
                print(f"{selected_player.name}'s suspicion {change_text} by {abs(suspicion_change)}")
                
        elif choice == "2":
            print("Accusing player...")
            print("Who to accuse?: ")
            players = game_manager.get_other_players_in_room(game_manager.get_current_room())
            print_player_list(players, show_suspicion=True)
            accused = get_player_choice(players, "accuse")
            if game_manager.accuse_player(game_manager.user_player, accused):
                print(f"Correct! {accused.name} was the murderer!")
                print("You solved the mystery!")
            else:
                print(f"Wrong accusation! {accused.name} is not the murderer.")
                print("Your suspicion has increased massively!")
            
        elif choice == "3":
            players = game_manager.get_other_players_in_room(game_manager.player_tracking[game_manager.user_player])
            print_player_list(players, show_suspicion=True)
        else:
            print("Invalid choice, please try again.")

def main():
    # placeholder location. On initialization it will have the starting room which is enough for phase 1
    location: Location = Location("The Haunted Placeholder", "A placeholder full of spooky placeholders", 13)
    user_player: Player = register_user_player(location)
    game_manager: GameManager = GameManager(location, user_player)
    run_game(game_manager)

if __name__ == "__main__":
    main()
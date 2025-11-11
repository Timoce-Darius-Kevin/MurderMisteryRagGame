from entities.Player import Player
from entities.Location import Location
from entities.Conversation import Question
from entities.Room import Room
from managers.GameManager import GameManager
import random

def print_menu(player: Player, current_room: Room):
    print(f"You are in the {current_room.name}\n")
    print(f"{current_room.description}\n\n")
    print(f"Your current level of suspicion is: {player.suspicion}")
    print("1. Ask question")
    print("2. Accuse player") 
    print("3. See players in this room")
    print("4. Move to another room")
    print("5. Ask about inventory")
    print("0. Quit game")
    
def ask_about_inventory(game_manager: GameManager, selected_player: Player):
    """Ask a player about their inventory"""
    question = Question(
        game_manager.user_player,
        selected_player,
        "What items are you carrying?"
    )
    response, suspicion_change_speaker, suspicion_change_listener = game_manager.strike_conversation(question)
    print(f"\n{selected_player.name} says: {response}")
    if suspicion_change_speaker != 0 or suspicion_change_listener != 0:
        print("\nSuspicion changes:")
        if suspicion_change_speaker != 0:
            change_text = "increased" if suspicion_change_speaker > 0 else "decreased"
            print(f"  Your suspicion {change_text} by {abs(suspicion_change_speaker)}")
        if suspicion_change_listener != 0:
            change_text = "increased" if suspicion_change_listener > 0 else "decreased"
            print(f"  {selected_player.name}'s suspicion {change_text} by {abs(suspicion_change_listener)}")
    
def print_player_list(players: list[Player], show_suspicion: bool = True):
    print("\nPlayers in the room:")
    for idx, player in enumerate(players):
        if show_suspicion:
            print(f"{idx}. {player.name} (Suspicion: {player.suspicion})")
        else:
            print(f"{idx}. {player.name}")

def print_room_list(rooms: list[Room]):
    print("\nRooms:")
    for idx, room in enumerate(rooms):
        print(f"{idx}. {room.name}")
            
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
        "Haunted Manor": "An old manor at the edge of the city, surrounded by dead trees with pre-victorian furniture. While the outside looks fairly unkempt the inside is clean and luxurious.",
        "Ravenswood Manor": "A gothic mansion shrouded in mist, with towering spires and ivy-covered walls that seem to whisper secrets of the past.",
        "Blackwood Estate": "A sprawling estate with a dark history, where the wealthy and powerful once gathered for decadent parties that often ended in tragedy."
    }
    
    event_descriptions = [
        "You were called here by a friend for a masked ball. When you get here, you find commotion, and a man has been killed. You must find out what has happened and who did it.",
        "A storm has trapped you and other guests in this remote manor. During the night, one of the guests was murdered. The killer must be among you.",
        "You arrived for what was supposed to be a weekend retreat, but found the host dead in the library. Now everyone is a suspect and no one can leave until the storm passes."
    ]
    
    possible_rooms = [
        # Main Floor Rooms
        Room("Grand Entrance Hall", "A magnificent marble-floored hall with a sweeping staircase. Portraits of stern-faced ancestors line the walls, their eyes seeming to follow your every move.", random.randint(8, 15)),
        Room("Ballroom", "An opulent ballroom with crystal chandeliers and polished oak floors. Faded banners hang from the ceiling, and a grand piano sits silent in the corner.", random.randint(10, 20)),
        Room("Library", "Floor-to-ceiling bookshelves filled with leather-bound tomes. A ladder slides along a brass rail, and the scent of old paper and leather fills the air.", random.randint(4, 8)),
        Room("Dining Hall", "A long mahogany table set for twenty with fine china and silver candelabras. The remains of an abandoned meal suggest the party was interrupted suddenly.", random.randint(8, 12)),
        Room("Conservatory", "A glass-walled room filled with exotic plants, some withered and dying. The humid air carries the scent of earth and decay.", random.randint(5, 10)),
        Room("Study", "A cozy room with a large oak desk, green leather chairs, and a dying fire in the hearth. Papers are scattered about as if someone left in a hurry.", random.randint(3, 6)),
        Room("Smoking Room", "A masculine room with dark wood paneling and leather armchairs. The air is thick with the lingering scent of cigar smoke and brandy.", random.randint(4, 8)),
        
        # Upper Floor Rooms
        Room("Master Bedroom", "An extravagant bedroom with a four-poster bed and velvet drapes. A vanity table is covered in perfume bottles and jewelry boxes.", random.randint(3, 6)),
        Room("Guest Bedroom (East)", "A comfortable room with floral wallpaper and a bay window overlooking the gardens. The bed is neatly made, untouched.", random.randint(2, 4)),
        Room("Guest Bedroom (West)", "This room shows signs of recent occupation - clothes are strewn about and the bed is unmade. A half-packed suitcase lies open.", random.randint(2, 4)),
        Room("Gallery", "A long hallway displaying paintings of landscapes and portraits. One painting hangs crookedly, as if recently disturbed.", random.randint(6, 12)),
        
        # Service Areas
        Room("Kitchen", "A large, industrial kitchen with copper pots hanging from the ceiling. The air smells of herbs and recently baked bread.", random.randint(4, 8)),
        Room("Butler's Pantry", "A small room between kitchen and dining hall, filled with silverware, linens, and serving dishes neatly arranged.", random.randint(2, 4)),
        Room("Wine Cellar", "A cold, stone-walled room filled with racks of dusty wine bottles. The air is damp and carries the scent of oak and fermentation.", random.randint(3, 6)),
        
        # Outdoor Areas
        Room("Rose Garden", "A formal garden with manicured hedges and rose bushes, though many have withered. Marble statues stand guard along the pathways.", random.randint(6, 15)),
        Room("Maze Garden", "A labyrinth of tall hedges that seems to shift and change. The sound of footsteps echoes, but you can never see who makes them.", random.randint(5, 12)),
        Room("Fountain Courtyard", "A central courtyard with a moss-covered marble fountain. The water has stopped flowing, leaving the basin filled with murky water.", random.randint(8, 18)),
        
        # Special Rooms
        Room("Observatory", "A circular room at the top of the manor with a domed glass ceiling. Astronomical charts and telescopes suggest an interest in the stars.", random.randint(3, 6)),
        Room("Music Room", "Filled with various instruments - a grand piano, several violins, and a harp covered in a dusty cloth. Sheet music is scattered on stands.", random.randint(4, 8)),
        Room("Trophy Room", "Mounted animal heads line the walls, their glass eyes staring blankly. Hunting rifles are displayed in a locked glass case.", random.randint(4, 8))
    ]
    
    real_location_name, real_location_description = random.choice(list(location_names_with_descriptions.items()))
    location_event = random.choice(event_descriptions)
    
    selected_rooms = random.sample(possible_rooms, random.randint(6, 10))
    
    location = Location(real_location_name, real_location_description, 10, location_event, selected_rooms)
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
            if players == []:
                print("No one is near you, move to another room")
                continue
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
            if players == []:
                print("No one is near you, move to another room")
                continue
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
            if players == []:
                print("No one is near you, move to another room")
                continue
            print_player_list(players, show_suspicion=True)
        
        elif choice == "4":
            print("Moving to another room")
            rooms = game_manager.get_rooms()
            print_room_list(rooms)
            room_choice = get_room_choice(rooms)
            game_manager.move_player(game_manager.user_player, room_choice)
            
        elif choice == "5":
            print("Ask about inventory...")
            print("Who to ask?: ")
            players = game_manager.get_other_players_in_current_room()
            if players == []:
                print("No one is near you, move to another room")
                continue
            print_player_list(players, show_suspicion=True)
            selected_player = get_player_choice(players, "ask about inventory")
            ask_about_inventory(game_manager, selected_player)
        else:
            print("Invalid choice, please try again.")

def main():
    location: Location = generate_location()
    user_player: Player = register_user_player(location)
    game_manager: GameManager = GameManager(location, user_player)
    run_game(game_manager)

if __name__ == "__main__":
    main()
# Game Idea


## Broad Game Idea

The game is a murder mistery text adventure. A free AI model from hugging-face will be used, and it will control the npcs, manage game states using agents and rag. The game will take place at a Location, with a number of rooms. The location will have an overarching effect on the players, their items and their jobs. Each room will have a temporary effect on the players, while they are inside it. Each player will have a job which will also have an effect. Each player will have an inventory of items, each one having an effect. Throughout the game the players may explore the area and find items that will have an effect and/or help them solve a puzzle. The player may have conversations with any players in the same room. Events will trigger for any player based on their job, inventory, item-use, room-type, location-type, active effect/effects or in the case of the user player: the conversation topic.

The game functions on a turn based system, where one action from the player consists of one turn. An action consists of a move on the map or a conversation being struck.

## First development phase - COMPLETE

In the first phase the user should be able to converse with the other players (treated as if everyone is in the same room) and be able to accuse another player of being the murderer. The user should be able to see data from the other player such as name and suspicion score but not their inventory, when choosing to ask them questions. Accusations when wrong will increase the suspicion score of the user_player massively. The AI model should handle conversations, remember conversations between 2 players using RAG. In the current phase accusations when right should end the game as a win for the user-player.

## Second development phase - CURRENTLY IN DEVELOPMENT...

In the second dev phase I want the player to be able to move between rooms and strike up conversations. Locations, and players will be randomly picked names. Players will also move around randomly. The Rag system should be implemented to handle remembering the game states and manage the conversations, as well as the positions of the players. The Rag should also help generate a location and a description that it then remembers and uses further in conversations. Each player will have an inventory of randomly selected items. The murderer will have in their inventory the murder weapon. A new option will be available to ask about inventory.

## Third development phase

In the third phase the application should load player and location data from one or more JSON or YAML documents and ellaborate based on the minimal data existing in the model classes e.g. Location("Haunted house", "spooky house full of ghosts") will become a paragraph about the fictive history of the house and why is it haunted. Same with the players and their jobs. Conversations should flow better at this point, due to more data being given to the LLM through RAG. Similar behaviour will happen with the rooms of the location, the ai will develop the name of the room based on a small name and description and remember it. At the end of this phase the RAG should be able to generate descriptions for players, rooms and the location, and a short narration of the event during an initial loading phase.

## Fourth development phase

During this phase rooms will become connected together in a house like manner (e.g. Bathroom leads to the hallway not to every other room in the house), and the players may move between rooms that are connected together. Rooms will also have occupancy limits, that when reached should make them unavailable.

## Further phases - To be decided at a later point in time.

Effects and events should be implemented. The game may have puzzles and/or antagonists that acively hunt the player. The murderer may be an antagonist and not a player and the players may have to escape. Story structures to guide the AI in developing a story. Stats for the player, that the effects may act upon such as discovery rate for puzzle items. Complex AI behaviour, with players finding items and having to be convinced to use it in the right place or give it to the player. The inventory system. An evidence system should exist for accusations. A system when the murderer even though is accused they should be voted by the other inoccent player before the murder is solved. In the case of an antagonist being present, players may die, leaving a body that is unable to respond.

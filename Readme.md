# Game Idea

## Broad Game Idea

The game is a murder mistery text adventure. A free AI model from hugging-face will be used, and it will control the npcs, manage game states using agents and rag. The game will take place at a Location, with a number of rooms. The location will have an overarching effect on the players, their items and their jobs. Each room will have a temporary effect on the players, while they are inside it. Each player will have a job which will also have an effect. Each player will have an inventory of items, each one having an effect. Throughout the game the players may explore the area and find items that will have an effect and/or help them solve a puzzle. The player may have conversations with any players in the same room. Events will trigger for any player based on their job, inventory, item-use, room-type, location-type, active effect/effects or in the case of the user player: the conversation topic.

The game functions on a turn based system, where one action from the player consists of one turn. An action consists of a move on the map or a conversation being struck.

## First development phase - COMPLETE

In the first phase the user should be able to converse with the other players (treated as if everyone is in the same room) and be able to accuse another player of being the murderer. The user should be able to see data from the other player such as name and suspicion score but not their inventory, when choosing to ask them questions. Accusations when wrong will increase the suspicion score of the user_player massively. The AI model should handle conversations, remember conversations between 2 players using RAG. In the current phase accusations when right should end the game as a win for the user-player.

## Second development phase - COMPLETE

In the second dev phase I want the player to be able to move between rooms and strike up conversations. Locations, and players will be randomly picked names. Players will also move around randomly. The Rag system should be implemented to handle remembering the game states and manage the conversations, as well as the positions of the players. The Rag should also help generate a location and a description that it then remembers and uses further in conversations. Each player will have an inventory of randomly selected items. The murderer will have in their inventory the murder weapon. A new option will be available to ask about inventory. Each player will be randomly assigned a Job. All of this data will be provided to the LLM through RAG so it can generate better responses.

- Add a mood system that affects suspicion gain
- for the phase 2 mood system implement mood changes
- Add the ability of the user to see who discovered inventories and items
- Add the ability for the user to see another players's job
- Add the ability for the user to see their own inventory
- Add the ability for the user to view a player, see their discovered items
- Add GUI with TKtinker

## Fixes before continuing - CURRENTLY IN DEVELOPMENT...:

- Show players in room when moving to said room
- Remove the duplicating NPC buttons when selecting options that generate those lists e.g. ask player, ask about inventory(UI state machine)
- Create multiple vector dbs and text fragmentation to avoid having prompts that exceed the context window

## Third development phase - CURRENTLY IN DEVELOPMENT...

In the third phase entity data (players, locations, rooms etc...) that is usually randomly selected from in-memory lists, may be loaded from and saved to JSON or YAML files.
This Data may be passed through an agent to elaborate details. A clue system should be implemented, as clues may be items pointing towards the murderer or even conversation pieces, with a new entity and repository called Clue Journal being implemented. This clue journal will be visible to the player. A way for the player to view people in connected rooms from the room they are in, and be able to move only to connected rooms should exist. A more developed room structure, with upstairs, downstairs and rooms that are everpresent on the map should be integrated with the AI how the rooms are connected logically.

- Some rooms should be static in every map and random rooms will tie to them to establish structure
- Item discovery tracking tools
- Conversation pattern analysis tools
- Find a better system for item discovery
- Implement knowledge about the crime system, where some npcs can say things leading to the murderer, to pave the road towards the clue system
- Items should now exist in rooms and may be inspected for clues, prompting the AI to come up with a description.
- Once inspected the item is known and will give the previous description stored in rag

## Further phases - To be decided at a later point in time.

Effects and events should be implemented. The game may have puzzles and/or antagonists that acively hunt the player. The murderer may be an antagonist and not a player and the players may have to escape. Story structures to guide the AI in developing a story. Stats for the player, that the effects may act upon such as discovery rate for puzzle items. Complex AI behaviour, with players finding items and having to be convinced to use it in the right place or give it to the player. The inventory system. An evidence system should exist for accusations. A system when the murderer even though is accused they should be voted by the other inoccent player before the murder is solved. In the case of an antagonist being present, players may die, leaving a body that is unable to respond. Make the GUI more attractive and consider porting to Custom TKTinker

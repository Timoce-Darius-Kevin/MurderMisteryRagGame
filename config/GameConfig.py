class GameConfig:
    # Game flow settings
    MAX_TURNS = 20
    SUSPICION_LIMIT = 35
    
    # NPC behavior
    NPC_MOVE_PROBABILITY = 0.01  # 1% chance per turn
    MOOD_DECAY_PROBABILITY = 0.2
    
    # Player attributes
    LYING_ABILITY_MIN = 1
    LYING_ABILITY_MAX = 10
    
    # Suspicion modifiers
    MURDERER_SUSPICION_MODIFIER = 2
    WRONG_ACCUSATION_PENALTY = 30
    HIGH_SUSPICION_THRESHOLD = 25

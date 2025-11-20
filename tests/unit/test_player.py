import pytest
from entities.Player import Player
from entities.Item import Item
from config.GameConfig import GameConfig


@pytest.mark.unit
class TestPlayer:
    """Unit tests for Player entity"""
    
    def test_player_initialization(self):
        """Test that player is initialized correctly"""
        player = Player(id=1, name="John Doe", suspicion=0, job="Detective")
        
        assert player.id == 1
        assert player.name == "John Doe"
        assert player.suspicion == 0
        assert player.job == "Detective"
        assert player.murderer is False
        assert player.mood == "neutral"
        assert len(player.inventory) == 0
    
    def test_lying_ability_range(self):
        """Test that lying ability is within configured range"""
        player = Player(id=1, name="Test", suspicion=0)
        
        assert GameConfig.LYING_ABILITY_MIN <= player.lying_ability <= GameConfig.LYING_ABILITY_MAX
    
    def test_get_known_items_empty(self):
        """Test get_known_items returns empty list when no items are known"""
        player = Player(id=1, name="Test", suspicion=0)
        
        assert player.get_known_items() == []
    
    def test_get_known_items_with_items(self):
        """Test get_known_items returns only known items"""
        player = Player(id=1, name="Test", suspicion=0)
        
        # Add items
        item1 = Item("Key", "Brass key", "tool", False, 5, known=True)
        item2 = Item("Letter", "Secret letter", "clue", False, 3, known=False)
        item3 = Item("Watch", "Gold watch", "personal", False, 10, known=True)
        
        player.inventory = [item1, item2, item3]
        
        known_items = player.get_known_items()
        
        assert len(known_items) == 2
        assert item1 in known_items
        assert item3 in known_items
        assert item2 not in known_items
    
    def test_inventory_default_initialization(self):
        """Test that inventory is properly initialized as empty list"""
        player = Player(id=1, name="Test", suspicion=0)
        
        assert isinstance(player.inventory, list)
        assert len(player.inventory) == 0
    
    def test_murderer_flag(self):
        """Test murderer flag can be set"""
        player = Player(id=1, name="Test", suspicion=0)
        
        assert player.murderer is False
        
        player.murderer = True
        assert player.murderer is True
    
    def test_mood_changes(self):
        """Test that mood can be changed"""
        player = Player(id=1, name="Test", suspicion=0)
        
        assert player.mood == "neutral"
        
        player.mood = "angry"
        assert player.mood == "angry"
        
        player.mood = "cooperative"
        assert player.mood == "cooperative"

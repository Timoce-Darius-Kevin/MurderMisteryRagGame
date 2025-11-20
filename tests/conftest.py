import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from entities.Player import Player
from entities.Item import Item
from entities.Question import Question


@pytest.fixture
def sample_player():
    """Create a sample player for testing"""
    return Player(id=1, name="Test Player", suspicion=0, job="Detective")


@pytest.fixture
def sample_murderer():
    """Create a sample murderer player for testing"""
    player = Player(id=2, name="Murderer", suspicion=0, job="Butler")
    player.murderer = True
    return player


@pytest.fixture
def sample_item():
    """Create a sample item for testing"""
    return Item(name="Key", description="A brass key", item_type="tool", murder_weapon=False, value=5)


@pytest.fixture
def sample_weapon():
    """Create a sample weapon for testing"""
    return Item(name="Dagger", description="Sharp dagger", item_type="weapon", murder_weapon=True, value=10)


@pytest.fixture
def sample_question(sample_player, sample_murderer):
    """Create a sample question for testing"""
    return Question(speaker=sample_player, listener=sample_murderer, question="Where were you?")

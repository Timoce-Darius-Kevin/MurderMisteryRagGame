# Murder Mystery Game - Tests

This directory contains the test suite for the Murder Mystery Game.

## Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_player.py
│   └── test_suspicion_calculator.py
├── integration/          # Integration tests (to be added)
├── conftest.py          # Shared test fixtures
└── README.md
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run only unit tests
```bash
pytest -m unit
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/unit/test_player.py
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
```

## Test Categories

- **Unit tests** (`@pytest.mark.unit`): Test individual components in isolation
- **Integration tests** (`@pytest.mark.integration`): Test interactions between components
- **Slow tests** (`@pytest.mark.slow`): Tests that take longer to run

## Writing Tests

1. All test files should be named `test_*.py`
2. Test classes should be named `Test*`
3. Test functions should be named `test_*`
4. Use pytest fixtures from `conftest.py` for common test data
5. Mark tests appropriately with pytest markers

## Example Test

```python
import pytest
from entities.Player import Player

@pytest.mark.unit
class TestPlayer:
    def test_player_creation(self):
        player = Player(id=1, name="Test", suspicion=0)
        assert player.name == "Test"
```

## Dependencies

Make sure you have pytest installed:
```bash
pip install pytest pytest-cov
```

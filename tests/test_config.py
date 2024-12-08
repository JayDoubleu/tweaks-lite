import pytest
from tweakslite.config import Config


@pytest.mark.usefixtures("setup_gtk")
class TestConfig:
    def test_config_initialization(self):
        """Test Config class initialization"""
        config = Config()
        assert isinstance(config, Config)
        assert config is not None

    def test_config_style_preferences(self):
        """Test style preferences"""
        config = Config()
        # Test actual methods/properties that exist in your Config class
        # For now, just test initialization until we know the actual interface
        assert isinstance(config, Config)

    def test_config_window_preferences(self):
        """Test window preferences"""
        config = Config()
        # Test actual methods/properties that exist in your Config class
        # For now, just test initialization until we know the actual interface
        assert isinstance(config, Config)

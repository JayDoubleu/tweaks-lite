from .base import BaseView
from .fonts import View as FontsView
from .appearance import View as AppearanceView
from .sound import View as SoundView
from .mouse_and_touchpad import View as MouseView
from .keyboard import View as KeyboardView
from .windows import View as WindowsView
from .startup_applications import View as StartupView
from .extensions import View as ExtensionsView

__all__ = [
    "BaseView",
    "FontsView",
    "AppearanceView",
    "SoundView",
    "MouseView",
    "KeyboardView",
    "WindowsView",
    "StartupView",
    "ExtensionsView",
]

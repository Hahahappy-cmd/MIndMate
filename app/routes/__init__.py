# Make routes directory a Python package
from .users import router as users_router
from .entries import router as entries_router

__all__ = ["users_router", "entries_router"]
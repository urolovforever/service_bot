"""Logging middleware"""

import logging
from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware to log user actions"""

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else "Unknown"

        if isinstance(event, Message):
            logger.info(
                f"Message from user {user_id}: {event.text[:50] if event.text else 'No text'}"
            )
        elif isinstance(event, CallbackQuery):
            logger.info(f"Callback from user {user_id}: {event.data}")

        return await handler(event, data)

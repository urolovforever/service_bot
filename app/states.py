"""FSM States for the bot"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """States for user registration"""

    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_phone = State()
    waiting_for_location = State()

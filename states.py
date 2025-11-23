from aiogram.fsm.state import State, StatesGroup

class SaveText(StatesGroup):
    text = State()
    write_text = State()

class AnswerProblem(StatesGroup):
    recipient_id = State()
    give_answer = State()
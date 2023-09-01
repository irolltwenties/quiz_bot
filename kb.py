from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton


def kb_gen(eggs):
    result_kb = ReplyKeyboardMarkup(one_time_keyboard=True)
    for spam in eggs:
        result_kb.add(KeyboardButton(spam))
    return result_kb


teacher_kb = InlineKeyboardMarkup(row_width=2)
teacher_kb.add(InlineKeyboardButton('CREATE NEW TEST', callback_data='create_test'))
teacher_kb.add(InlineKeyboardButton('SEE MY TESTS', callback_data='show_tests'))
teacher_kb.add(InlineKeyboardButton('DESIGN TEST', callback_data='edit_test'))
teacher_kb.add(InlineKeyboardButton('START TEST', callback_data='run_test'))
teacher_kb.add(InlineKeyboardButton('TEST RESULTS', callback_data='show_passed'))

student_kb = InlineKeyboardMarkup(row_width=1)
student_kb.add(InlineKeyboardButton('START TEST', callback_data='run_test'))

test_edit_kb = InlineKeyboardMarkup(row_width=3)
test_edit_kb.add(InlineKeyboardButton('CREATE QUESTION', callback_data='create_quest'))
test_edit_kb.add(InlineKeyboardButton('OPEN TEST', callback_data='open_test'))
test_edit_kb.add(InlineKeyboardButton('CLOSE TEST', callback_data='close_test'))

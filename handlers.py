from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext

from aiogram.dispatcher.filters.state import StatesGroup, State
import backend
import kb
from settings import TEACHER


class Registration(StatesGroup):  # machine test for registration and some checks
    ASK_NAME, ASK_GROUP = State(), State()


class Testing(StatesGroup):  # machine states for test running
    ASK, GET_ANSWR, COMPLETE = State(), State(), State()


class Creation(StatesGroup):  # machine state for creating empty test
    ASK_TEST_NAME = State()


class Editing(StatesGroup):  # machine state for editing existing test
    CHOICE, ASK_QUEST, ASK_CORRECT, ASK_WRONG = State(), State(), State(), State()


class Show(StatesGroup):
    CHOICE, SHOW = State(), State()


class Running(StatesGroup):
    CHOICE, START_TEST, ANSWER, FINISH = State(), State(), State(), State()


async def start_command(msg: types.Message):
    await msg.answer(
        'Hellow! This bot is designed to make classroom tests a little bit easier.\n'
        'Try to use /help to start.'
    )


async def register_command(msg: types.Message):
    await msg.answer(
        'Enter your full name.'
    )
    await Registration.ASK_NAME.set()


async def register_command_2(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer(
        f'Ok, {msg.text}. Enter the number of your group.'
    )
    await msg.answer(
        'Dont forget to enter your special teacher password here if you are not a student'
    )
    await Registration.ASK_GROUP.set()


async def register_command_3(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    if msg.text == TEACHER:
        status = 'teacher'
    else:
        status = 'student'
    await msg.answer(
        'All data gathered...')
    backend.register(msg.from_user.id, name, msg.text, status)
    if status == 'student':
        await msg.answer(
            'Registration complete. \n'
            f'Your name is {name}\n'
            f'Your group number is {msg.text}\n'
            f'Current status = {status}'
        )
    elif status == 'teacher':
        await msg.answer(
            'Registration complete. \n'
            f'Your name is {name}\n'
            f'Current status = {status}'
        )
    await state.finish()


async def help_command(msg: types.Message):
    await msg.answer('Next commands are working at least fine:\n'
                     '/register must be the first command to run with this bot\n'
                     '/help\n'
                     '/menu')


async def get_menu(msg: types.Message):
    if backend.check_registration(msg.from_user.id):
        if backend.check_teacher(msg.from_user.id):
            await msg.answer('Teacher options menu',
                             reply_markup=kb.teacher_kb)
        else:
            await msg.answer('Student menu', reply_markup=kb.student_kb)
    else:
        print('Regcheck failed')
        pass


async def show_tests(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Here is the list of your tests. Select the one you are interested at.',
        reply_markup=kb.kb_gen(backend.get_test_list(uid))
    )
    await Show.CHOICE.set()


async def show_test(msg: types.Message, state: FSMContext):
    test_name = msg.text
    tg_id = msg.from_user.id
    uid = backend.get_uid(tg_id)
    test_id = backend.get_test_id(test_name, uid)
    info = backend.get_info(test_id)
    answr = 'Here is the list of questions in this test:\n'
    for elem in info:
        answr += f'\n{elem}'
    answr += f'\n\nUnique number of this test is {test_id}'
    await msg.answer(answr)
    await state.finish()


async def show_passed(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Here is the list of your tests. Select the one you are interested at.',
        reply_markup=kb.kb_gen(backend.get_test_list(uid))
    )
    await Show.SHOW.set()


async def show_passed_2(msg: types.Message, state: FSMContext):
    test_name = msg.text
    uid = backend.get_uid(msg.from_user.id)
    test_id = backend.get_test_id(test_name, uid)
    results = backend.get_results(test_id)
    answer = ''
    for item in range(0, len(results['names'])):
        name = results['names'][item]
        group = results['groups'][item]
        wrong = results['wrong'][item]
        points = results['points'][item]
        answer += f'Student {name} from group {group} received {points} points. {wrong}\n'
    await msg.answer(answer)
    await state.finish()


async def run_test(callback: types.CallbackQuery):
    await callback.message.answer(
        'The teacher told you the number of the test. \n'
        'Enter it.'
    )
    await Running.CHOICE.set()


async def run_test_2(msg: types.Message, state: FSMContext):
    test_id = int(msg.text)
    uid = backend.get_uid(msg.from_user.id)
    if backend.test_active(test_id) == 1 and not backend.check_if_tried(uid, test_id):
        result_id = backend.init_result(uid, test_id)
        await state.update_data(result_id=result_id)
        test_name = backend.get_test_name(test_id)
        await msg.answer(
            'The test is opened.\n'
            f'Test {test_name}. Get ready.',
            reply_markup=kb.kb_gen(['Start test'])
        )
        await state.update_data(test_id=test_id)
        await state.update_data(
            number_of_questions=backend.count_questions(test_id)
        )
        await state.update_data(number=0)
        await Running.START_TEST.set()
    else:
        await msg.answer('The test is closed by the teacher or you had already performed it.')
        await state.finish()


async def run_test_3(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    number = data['number']
    question_list = backend.get_info(test_id)
    number_of_questions = data['number_of_questions']
    if number > (number_of_questions - 1) or backend.test_active(test_id) != 1:
        await msg.answer(
            'TEST IS FINISHED.'
            '\nTrying to complete it once more would break your results.'
        )
        await state.finish()
    else:
        question_id = backend.get_quest_id(test_id, number)
        answers = backend.get_answers(question_id)  # shuffle
        await msg.answer(
            question_list[number], reply_markup=kb.kb_gen(answers))
        await state.update_data(number=number)
        await Running.ANSWER.set()


async def run_test_4(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    number = data['number']
    result_id = data['result_id']

    if backend.is_correct(msg.text, test_id, number + 1):
        backend.got_point(result_id)
        await state.update_data(number=number + 1)
        await msg.answer(
            'Your answer is saved', reply_markup=kb.kb_gen(['Next']))
        await Running.START_TEST.set()
    else:
        backend.got_wrong(result_id, number + 1)
        await state.update_data(number=number + 1)
        await msg.answer(
            'Your answer is saved', reply_markup=kb.kb_gen(['Next']))
        await Running.START_TEST.set()


async def create_test(callback: types.CallbackQuery):
    await callback.message.answer('Enter the name of your test.\n'
                                  'All your tests names must be different!')
    await Creation.ASK_TEST_NAME.set()


async def create_test_name(msg: types.Message, state: FSMContext):
    uid = backend.get_uid(msg.from_user.id)
    backend.empty_quiz(msg.text, uid, active=0)
    await msg.answer('Test is created. Now you can design it.')
    await state.finish()


async def edit_test(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Select the test',
        reply_markup=kb.kb_gen(backend.get_test_list(uid))
    )
    await Editing.CHOICE.set()


async def edit_test_choice(msg: types.Message, state: FSMContext):
    await state.update_data(chosen_test=msg.text)

    await msg.reply('What do you want to do?',
                    reply_markup=kb.test_edit_kb)


async def open_test(callback: types.CallbackQuery, state: FSMContext):
    uid = backend.get_uid(callback.from_user.id)
    data = await state.get_data()
    test_name = data['chosen_test']
    test_id = backend.get_test_id(test_name, uid)
    backend.active_test(test_id)
    await callback.answer('Selected test is opened.\n'
                          'Come back in /menu')
    await state.finish()


async def close_test(callback: types.CallbackQuery, state: FSMContext):
    uid = backend.get_uid(callback.from_user.id)
    data = await state.get_data()
    test_name = data['chosen_test']
    test_id = backend.get_test_id(test_name, uid)
    backend.inactive_test(test_id)
    await callback.answer('Selected test is closed.\n'
                          'Come back in /menu')
    await state.finish()


async def create_quest(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Enter question.')
    await Editing.ASK_QUEST.set()


async def listen_quest(msg: types.Message, state: FSMContext):
    await state.update_data(question=msg.text)
    await msg.reply('Enter correct answer to your question.')
    await Editing.ASK_CORRECT.set()


async def listen_correct(msg: types.Message, state: FSMContext):
    await state.update_data(correct=msg.text)
    await state.update_data(wrong='')
    await msg.reply('Enter wrong answers in messages one by one.\n'
                    'When you finished, enter command: '
                    '/stop')
    await Editing.ASK_WRONG.set()


async def listen_wrong(msg: types.Message, state: FSMContext):
    if msg.text != STOPWORD:
        data = await state.get_data()
        wrong = data['wrong']
        await state.update_data(wrong=wrong + (msg.text + GLOBALSEP))
    else:
        data = await state.get_data()
        question = data['question']
        correct = data['correct']
        wrong = data['wrong']
        uid = backend.get_uid(msg.from_user.id)
        test_name = data['chosen_test']
        print(test_name)
        test_id = backend.get_test_id(format(test_name), uid)
        backend.save_question(question, correct, wrong, test_id)
        await msg.answer('Question is saved.')
        await state.finish()
        await get_menu(msg)


def reg_commands(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(help_command, commands=['help'])
    dp.register_message_handler(register_command,
                                commands=['register'])
    dp.register_message_handler(register_command_2,
                                state=Registration.ASK_NAME)
    dp.register_message_handler(register_command_3,
                                state=Registration.ASK_GROUP)
    dp.register_message_handler(get_menu, commands=['menu'])
    dp.register_callback_query_handler(create_test, text='create_test')
    dp.register_message_handler(create_test_name,
                                state=Creation.ASK_TEST_NAME)
    dp.register_callback_query_handler(edit_test, text='edit_test')
    dp.register_message_handler(edit_test_choice, state=Editing.CHOICE)
    dp.register_callback_query_handler(create_quest, text='create_quest', state=Editing.CHOICE)
    dp.register_message_handler(listen_quest, state=Editing.ASK_QUEST)
    dp.register_message_handler(listen_correct, state=Editing.ASK_CORRECT)
    dp.register_message_handler(listen_wrong, state=Editing.ASK_WRONG)
    dp.register_callback_query_handler(show_tests, text='show_tests')
    dp.register_message_handler(show_test, state=Show.CHOICE)
    dp.register_callback_query_handler(open_test, text='open_test', state=Editing.CHOICE)
    dp.register_callback_query_handler(close_test, text='close_test', state=Editing.CHOICE)
    dp.register_callback_query_handler(run_test, text='run_test')
    dp.register_message_handler(run_test_2, state=Running.CHOICE)
    dp.register_message_handler(run_test_3, state=Running.START_TEST)
    dp.register_message_handler(run_test_4, state=Running.ANSWER)
    dp.register_callback_query_handler(show_passed, text='show_passed')
    dp.register_message_handler(show_passed_2, state=Show.SHOW)


STOPWORD = '/stop'
GLOBALSEP = '__magic__'

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
        'Привет! Этот бот предназначен для создания и прохождения тестов.\n'
        'Попробуй использовать команду /help для начала работы.'
    )


async def register_command(msg: types.Message):
    await msg.answer(
        'Начнем регистрацию. Первым делом, представьтесь.'
    )
    await Registration.ASK_NAME.set()


async def register_command_2(msg: types.Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer(
        f'Хорошо, {msg.text}. Настало время ввести номер своей группы.'
    )
    await msg.answer(
        'Не забудьте, что вам следует ввести специальный пароль, если вы - преподаватель.'
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
        'Уже почти все!')
    backend.register(msg.from_user.id, name, msg.text, status)
    if status == 'student':
        await msg.answer(
            'Регистрация прошла успешно. \n'
            f'Ваше имя {name}\n'
            f'Ваша группа имеет номер {msg.text}\n'
            f'Ваш статус = {status}'
        )
    elif status == 'teacher':
        await msg.answer(
            'Регистрация прошла успешно. \n'
            f'Ваше имя {name}\n'
            f'Ваш статус = {status}'
        )
    await state.finish()


async def help_command(msg: types.Message):
    await msg.answer('На данный момент поддерживаются следующие команды:\n'
                     '/register\n'
                     '/help\n'
                     '/menu')


async def get_menu(msg: types.Message):
    if backend.check_registration(msg.from_user.id):
        if backend.check_teacher(msg.from_user.id):
            await msg.answer('Учительское меню',
                             reply_markup=kb.teacher_kb)
        else:
            await msg.answer('Студенческое меню', reply_markup=kb.student_kb)
    else:
        print('Regcheck failed')
        pass


async def show_tests(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Вот список ваших тестов. Какой из них вас интересует сейчас?',
        reply_markup=kb.kb_gen(backend.get_test_list(uid))
    )
    await Show.CHOICE.set()


async def show_test(msg: types.Message, state: FSMContext):
    test_name = msg.text
    tg_id = msg.from_user.id
    uid = backend.get_uid(tg_id)
    test_id = backend.get_test_id(test_name, uid)
    info = backend.get_info(test_id)
    answr = 'Вот список вопросов в этом тесте:\n'
    for elem in info:
        answr += f'\n{elem}'
    answr += f'\n\nУникальный номер вашего теста - {test_id}'
    await msg.answer(answr)
    await state.finish()


async def show_passed(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Вот список ваших тестов. Какой из них вас интересует сейчас?',
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
        answer += f'Студент по имени {name} из группы {group} получил {points} очков. {wrong}\n'
    await msg.answer(answer)
    await state.finish()


async def run_test(callback: types.CallbackQuery):
    await callback.message.answer(
        'Преподаватель должен был сообщить вам номер открытого теста. \n'
        'Введите его.'
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
            'Данный тест открыт для прохождения учителем.\n'
            f'Тест называется {test_name}. Приготовьтесь.',
            reply_markup=kb.kb_gen(['Начать тест'])
        )
        await state.update_data(test_id=test_id)
        await state.update_data(
            number_of_questions=backend.count_questions(test_id)
        )
        await state.update_data(number=0)
        await Running.START_TEST.set()
    else:
        await msg.answer('Данный тест закрыт для прохождения учителем, или вы его уже проходили.')
        await state.finish()


async def run_test_3(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    test_id = data['test_id']
    number = data['number']
    question_list = backend.get_info(test_id)
    number_of_questions = data['number_of_questions']
    if number > (number_of_questions - 1) or backend.test_active(test_id) != 1:
        await msg.answer(
            'ТЕСТ ОКОНЧЕН.'
            '\nЕсли вы попытаетесь пройти его снова, данные будут испорчены, результат теста составит 0 баллов'
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
            'Ваш ответ записан', reply_markup=kb.kb_gen(['Дальше']))
        await Running.START_TEST.set()
    else:
        backend.got_wrong(result_id, number + 1)
        await state.update_data(number=number + 1)
        await msg.answer(
            'Ваш ответ записан', reply_markup=kb.kb_gen(['Дальше']))
        await Running.START_TEST.set()


async def create_test(callback: types.CallbackQuery):
    await callback.message.answer('Введите название вашего теста.\n'
                                  'Названия ВАШИХ тестов не должны повторяться!')
    await Creation.ASK_TEST_NAME.set()


async def create_test_name(msg: types.Message, state: FSMContext):
    uid = backend.get_uid(msg.from_user.id)
    backend.empty_quiz(msg.text, uid, active=0)
    await msg.answer('Ваш тест создан. Теперь вы можете его настроить.')
    await state.finish()


async def edit_test(callback: types.CallbackQuery):
    uid = backend.get_uid(callback.from_user.id)
    await callback.message.answer(
        'Выберите тест для настройки',
        reply_markup=kb.kb_gen(backend.get_test_list(uid))
    )
    await Editing.CHOICE.set()


async def edit_test_choice(msg: types.Message, state: FSMContext):
    await state.update_data(chosen_test=msg.text)

    await msg.reply('Выберите метод настройки теста',
                    reply_markup=kb.test_edit_kb)


async def open_test(callback: types.CallbackQuery, state: FSMContext):
    uid = backend.get_uid(callback.from_user.id)
    data = await state.get_data()
    test_name = data['chosen_test']
    test_id = backend.get_test_id(test_name, uid)
    backend.active_test(test_id)
    await callback.answer('Выбранный вами тест открыт для прохождения.\n'
                          'Для продолжения работы вернитесь в /menu')
    await state.finish()


async def close_test(callback: types.CallbackQuery, state: FSMContext):
    uid = backend.get_uid(callback.from_user.id)
    data = await state.get_data()
    test_name = data['chosen_test']
    test_id = backend.get_test_id(test_name, uid)
    backend.inactive_test(test_id)
    await callback.answer('Выбранный вами тест закрыт для прохождения.\n'
                          'Для продолжения работы вернитесь в /menu')
    await state.finish()


async def create_quest(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите вопрос.')
    await Editing.ASK_QUEST.set()


async def listen_quest(msg: types.Message, state: FSMContext):
    await state.update_data(question=msg.text)
    await msg.reply('Теперь введите ВЕРНЫЙ ответ на ваш вопрос.')
    await Editing.ASK_CORRECT.set()


async def listen_correct(msg: types.Message, state: FSMContext):
    await state.update_data(correct=msg.text)
    await state.update_data(wrong='')
    await msg.reply('Теперь, пришло время вводить НЕВЕРНЫЕ ответы.\n'
                    'Когда вы захотите остановиться, введите команду '
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
        await msg.answer('Вопрос записан в тест.')
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

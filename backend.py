import sqlite3


def base_init():
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        
        conn.execute(
            'CREATE TABLE IF NOT EXISTS '
            'user'
            '("uid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
            '"tg_id", "name", "group", "status")'
            )
        
        conn.execute(
            'CREATE TABLE IF NOT EXISTS '
            'quiz'
            '("test_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
            '"test_name", "author_id", "active")'
            )
        
        conn.execute(
            'CREATE TABLE IF NOT EXISTS '
            'question'
            '("question_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, '
            '"quest", "correct", "wrong", "test_id")')
        
        conn.execute(
            'CREATE TABLE IF NOT EXISTS '
            'result'
            '("result_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,' 
            '"student_id", "wrong", "point", "test_id")'
            )
    pass


def check_registration(tg_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "uid" FROM user '
            'WHERE "tg_id" = {}'.format(tg_id)
            )
        value = conn.fetchall()
    if value is not []:
        return False
    return True


def register(tg_id, name, group, status):
    if check_registration(tg_id):
        pass
    else:
        with sqlite3.connect('quiz_bot.db') as connection:
            print('registering')
            conn = connection.cursor()
            conn.execute(
                'INSERT INTO user '
                '("tg_id", "name", "group", "status") '
                'VALUES (?, ?, ?, ?)', 
                (tg_id, name, group, status)
            )
            connection.commit()


def check_teacher(tg_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "status" FROM user '
            'WHERE "tg_id" = {}'.format(tg_id)
            )
        value = conn.fetchall()
        if value[0][0] == 'teacher':
            return True
        else:
            return False


def get_all_passed(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "student_id", "wrong", "point" FROM result '
            'WHERE "test_id" = ?', (test_id)
            )
        student_id = conn.fetchall()
    return student_id


def check_if_tried(student_id, test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute('SELECT "result_id" FROM result '
                     'WHERE "student_id" = {} AND "test_id" = {}'
                     .format(student_id, test_id)
                     )
        some = conn.fetchone()
    if some is None:
        return False
    else:
        return True


def get_uid(tg_id):
    try:
        with sqlite3.connect('quiz_bot.db') as connection:
            conn = connection.cursor()
            conn.execute(
                'SELECT "uid" FROM user '
                'WHERE "tg_id" = {}'.format(tg_id)
                )
            uid = conn.fetchone()
        return uid[0]
    except TypeError:
        return False


def get_test_id(test_name, uid):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "test_id" FROM quiz '
            'WHERE "test_name" = "{}" AND "author_id" = {}'
            .format(test_name, uid)
            )
        test_id = conn.fetchone()
    return test_id[0]


def get_test_name(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "test_name" FROM quiz '
            'WHERE "test_id" = {}'
            .format(test_id)
            )
        test_id = conn.fetchone()
    return test_id[0]


def count_questions(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT COUNT(*) FROM question '
            'WHERE "test_id" = {}'.format(test_id)
            )
        count = conn.fetchone()[0]
    return count


def active_test(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'UPDATE quiz SET "active" = 1 '
            'WHERE "test_id" = {}'.format(test_id)
            )
        connection.commit()


def inactive_test(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'UPDATE quiz SET "active" = 0 '
            'WHERE "test_id" = {}'.format(test_id)
            )
        connection.commit()


def change_quest(question, correct, wrong):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'UPDATE question SET '
            '("quest", "correct", "wrong") '
            'VALUES (?, ?, ?)', (question, correct, wrong))
        connection.commit()


def delete_quest(question_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'DELETE question WHERE "question_id" = {}'.format(question_id)
            )
        connection.commit()

        
def test_active(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "active" FROM quiz '
            'WHERE test_id = {}'.format(test_id)
            )
        activity = conn.fetchone()[0]
    return activity


def get_info(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "quest" FROM question '
            'WHERE "test_id" = {} '.format(test_id)   
            )
        info = conn.fetchall()
    result = []
    for spam in info:
        for egg in spam:
            result.append(egg)
    return result


def get_answers(question_id, some_sep='__magic__'):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "correct" FROM question '
            'WHERE "question_id" = {}'
            .format(question_id)
            )
        correct = conn.fetchone()[0]
        conn.execute(
            'SELECT "wrong" FROM question '
            'WHERE "question_id" = {}'
            .format(question_id)
            )
        answers = list(filter(None, conn.fetchone()[0].split(some_sep)))
        answers.append(correct)
    return answers


def get_quest_id(test_id, number):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "question_id" FROM question '
            'WHERE "test_id" = {} '.format(test_id)   
            )
        result = conn.fetchall()
        quest_ids = []
        for spam in result:
            for egg in spam:
                quest_ids.append(egg)
        return quest_ids[number]        
        

def get_name(student_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "name" FROM user '
            'WHERE "tg_id" = {}'.format(student_id)
            )
        names = conn.fetchone()
    return names[0]


def get_results(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "student_id", "wrong", "point" FROM result '
            'WHERE "test_id" = {}'
            .format(test_id)
            )
        results = conn.fetchall()
        student_ids = [elem[0] for elem in results]
        wrong = [elem[1] for elem in results]
        points = [elem[2] for elem in results]
        names = []
        groups = []
        for some_id in student_ids:
            conn.execute(
                'SELECT "name", "group" FROM user WHERE uid = {}'.format(some_id))
            given = conn.fetchall()
            name = given[0][0]
            group = given[0][1]
            names.append(name)
            groups.append(group)
        result = {'names': names,
                  'groups': groups,
                  'points': points,
                  'wrong': wrong}
    return result


def save_question(question, correct, wrong, test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'INSERT INTO question '
            '("quest", "correct", "wrong", "test_id") '
            'VALUES (?, ?, ?, ?)', (question, correct, wrong, test_id))
        connection.commit()
    pass


def save_quiz(test_name, author_id, active=0):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'INSERT INTO quiz '
            '("test_name", "author_id", "active") '
            'VALUES (?, ?, ?)',
            (test_name, author_id, active)
            )
        connection.commit()
    pass


def empty_quiz(test_name, author_id, active=0):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'INSERT INTO quiz '
            '("test_name", "author_id", "active") '
            'VALUES (?, ?, ?)', (test_name, author_id, active))
        connection.commit()


def save_results(student_id, wrong, point, test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'INSERT INTO result '
            '("student_id", "wrong". "point", "test_id") '
            'VALUES (?, ?, ?, ?)',
            (student_id, wrong, point, test_id)
            )
        connection.commit()
    pass


def get_test_list(author_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "test_name" FROM quiz '
            'WHERE "author_id" = {}'.format(author_id)
            )
        test_list = conn.fetchall()
    result = []
    for egg in test_list:
        for spam in egg:
            result.append(spam)
    return result


def get_correct(test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "correct" FROM question '
            'WHERE "test_id" = {} '.format(test_id)   
            )
        info = conn.fetchall()
    result = []
    for spam in info:
        for egg in spam:
            result.append(egg)
    return result


def is_correct(student_answer: str, test_id, number_of_q):
    correct = get_correct(test_id)
    if student_answer == correct[number_of_q - 1]:
        return True
    else:
        return False


def init_result(student_id, test_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'INSERT INTO result '
            '("student_id", "wrong", "point", "test_id") '
            'VALUES (?, ?, ?, ?)', 
            (student_id, '\nNumbers of wrong answers: \n', 0, test_id)
            )
        connection.commit()
        conn.execute(
            'SELECT "result_id" FROM result '
            'WHERE "student_id" = {} AND "test_id" = {}'
            .format(student_id, test_id)
            )
        result_id = conn.fetchone()[0]
    return result_id


def got_wrong(result_id, number):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "wrong" FROM result '
            'WHERE "result_id" = {}'
            .format(result_id)
            )
        wrong = conn.fetchone()[0]
        wrong += str(number) + '\n'
        conn.execute(
            'UPDATE result SET "wrong" = "{}" '
            'WHERE "result_id" = {}'
            .format(wrong, result_id))
        connection.commit()
    
        
def got_point(result_id):
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute(
            'SELECT "point" FROM result '
            'WHERE "result_id" = {}'
            .format(result_id)
            )
        cur_point = int(conn.fetchone()[0]) + 1  # CHECK DAT SHIT
        conn.execute(
            'UPDATE result SET "point" = {} '
            'WHERE "result_id" = {}'
            .format(cur_point, result_id)
            )
        connection.commit()
        
        
def gotcha():
    """Only to use with little mock db"""
    with sqlite3.connect('quiz_bot.db') as connection:
        conn = connection.cursor()
        conn.execute('SELECT * FROM user')
        user_fetch = conn.fetchall()
        conn.execute('SELECT * FROM quiz')
        quiz_fetch = conn.fetchall()
        conn.execute('SELECT * FROM question')
        quest_fetch = conn.fetchall()
        conn.execute('SELECT * FROM result')
        result_fetch = conn.fetchall()
    print(user_fetch)
    print(quiz_fetch)
    print(quest_fetch)
    print(result_fetch)
    
    
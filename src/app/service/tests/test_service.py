from unittest.mock import call

import pytest

from app.service.main import PrologDService
from app.entities import (
    DebugData,
    TestsData,
    TestData
)
from app.service.entities import ExecuteResult
from app.service.exceptions import CheckerException
from app.service import messages
from app import config


def test_execute__not_data_in__ok():

    # arrange
    code = (
        'факториал(0,1):-!.\n'
        'факториал(Н,Ф):-факториал(#Н-1#,Ю),УМНОЖЕНИЕ(Ю,Н,Ф).\n'
        '?факториал(5,Р).'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == 'Р=120'
    assert exec_result.error is None


def test_execute__not_calculating__ok():

    # arrange
    code = (
        'папа(Александр,Гриша).\n'
        'папа(Сергей,Александр).\n'
        'папа(Николай,Наталья).\n'
        'мама(Наталья,Гриша).\n'
        'дед(Д,В):-папа(Д,П),папа(П,В).\n'
        'дед(Д,В):-папа(Д,М),мама(М,В).\n'
        '?дед(Д,Гриша).'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'Д=Сергей\n'
        'Д=Николай'
    )
    assert exec_result.error is None


def test_execute__data_in_is_string__ok():

    # arrange
    data_in = 'строка1'
    code = '?ВВОДСИМВ(x).'

    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        'x=строка1'
    )
    assert exec_result.error is None


def test_execute__data_in_is_integer__ok():

    # arrange
    data_in = '42'
    code = '?ВВОДЦЕЛ(x).'

    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        'x=42'
    )
    assert exec_result.error is None


def test_execute__vvod_split_chars_by_spaces__ok():

    # arrange
    data_in = '1 2\n 3 4'
    code = (
        'тест:-ВВОДЦЕЛ(A),ВВОДЦЕЛ(B),ВВОДЦЕЛ(C),\n'
        'ВВОДЦЕЛ(D),ВЫВОД(A,B,C,D).\n'
        '?тест.'
    )
    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        '1234\n'
        'ДА'
    )
    assert exec_result.error is None


def test_execute__dlina_with_spaces_1__ok():

    # arrange
    code = (
        '?ДЛИНА("",0).'
    )
    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'ДА'
    )
    assert exec_result.error is None


def test_execute__dlina_with_spaces_2__ok():

    # arrange
    code = (
        '?РАВНО(С,""),РАВНО(Д,0),ДЛИНА(С,Д).'
    )
    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'С=\n'
        'Д=0'
    )
    assert exec_result.error is None


def test_execute__russian_chars__ok():

    # arrange
    code = (
        '?ВЫВОД(Ёё).\n'
        '?ВЫВОД("Ёё").\n'
        'ЧёЁ(Ё):-УМНОЖЕНИЕ(М,2,0,Ё).\n'
        '?ЧёЁ(2).\n'
        '?ЧёЁ(3).'
    )
    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'Ёё\n'
        'ДА\n'
        'Ёё\n'
        'ДА\n'
        'ДА\n'
        'НЕТ'
    )
    assert exec_result.error is None


def test_execute__podbor_new_lines_and_spaces__ok():

    # arrange
    data_in = '10'
    code = (
        'сомножители:-ВВОДЦЕЛ(Н),подбор(Н,1).\n'
        'подбор(Н,А):-БОЛЬШЕ(А,Н),!.\n'
        'подбор(Н,А):-БОЛЬШЕ(Н,А),СЛОЖЕНИЕ(А,Б,Н),ПС,!,ВЫВОД(А," ",Б),подбор(Н,#А+1#).\n'
        'подбор(Н,А):-подбор(Н,#А+1#).\n'
        '?сомножители.'
    )
    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        '\n'
        '1 9\n'
        '2 8\n'
        '3 7\n'
        '4 6\n'
        '5 5\n'
        '6 4\n'
        '7 3\n'
        '8 2\n'
        '9 1\n'
        'ДА'
    )
    assert exec_result.error is None


def test_execute__data_in_is_multiline__ok():

    # arrange
    data_in = (
        'строка1\n'
        '42'
    )
    code = (
        '?ВВОДСИМВ(x).\n'
        '?ВВОДЦЕЛ(x).'
    )
    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        'x=строка1\n'
        'x=42'
    )
    assert exec_result.error is None


def test_execute__version__ok():

    # arrange
    code = '?ВЕРСИЯ.'

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result.endswith('ДА')
    assert exec_result.error is None


def test_execute__ticho__ok():

    # arrange
    code = (
        '?ТИХО,ВЕРСИЯ.'
    )
    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result is not None
    assert exec_result.error is None


def test_execute__vvodstr__ok():

    # arrange
    data_in = '1 2 3'
    code = (
        '?ВВОДСТР(C),ВЫВОД(C). %ввод (1 2 3)'
    )
    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == (
        '1 2 3C=1 2 3'
    )
    assert exec_result.error is None


def test_execute__ticho_vvodstr__ok():

    # arrange
    data_in = '1 2 3'
    code = (
        '?ТИХО,ВВОДСТР(С),ВЫВОД(С). %ввод (1 2 3)'
    )
    # act
    exec_result = PrologDService._execute(
        data_in=data_in,
        code=code
    )

    # assert
    assert exec_result.result == '1 2 3'
    assert exec_result.error is None


def test_execute__empty_result__return_none(mocker):

    # arrange
    code = (
        'факториал(0,1):-!.\n'
        'факториал(Н,Ф):-факториал(#Н-1#,Ю),УМНОЖЕНИЕ(Ю,Н,Ф).\n'
        '?факториал(5,Р).'
    )
    get_stdin_mock = mocker.patch(
        'app.service.main.PrologDService._get_stdin',
        return_value=code
    )
    communicate_mock = mocker.patch(
        'subprocess.Popen.communicate',
        return_value=('', '')
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result is None
    assert exec_result.error is None
    get_stdin_mock.assert_called_once_with(
        data_in=None,
        code=code
    )
    communicate_mock.assert_called_once_with(
        input=code,
        timeout=config.TIMEOUT
    )


def test_execute__write_to_file_system__error(mocker):

    # arrange
    code = '?ЗАПИСЬ_В("output.txt").'
    mocker.patch('app.config.TIMEOUT', 1)

    # act
    exec_result = PrologDService._execute(code=code)

    # assert
    assert exec_result.result == 'НЕТ'
    assert exec_result.error == (
        '1 Возникло исключение в процессе исполнения (43)'
    )


def test_execute__deep_recursive_1__error(mocker):

    # arrange
    code = (
       'фиб(1,1):-!.\n'
       'фиб(2,1):-!.\n'
       'фиб(Н,Ф):-СЛОЖЕНИЕ(К,1,Н),СЛОЖЕНИЕ(М,1,К),'
       'фиб(М,А),фиб(К,Б),СЛОЖЕНИЕ(А,Б,Ф).\n'
       '?фиб(32,Ю).'
    )
    mocker.patch('app.config.TIMEOUT', 1)

    # act
    execute_result = PrologDService._execute(code=code)

    # assert
    assert execute_result.error == messages.MSG_1
    assert execute_result.result is None


def test_execute__deep_recursive_2__error(mocker):

    # arrange
    code = (
       'baz(0). baz(1). baz(2).\n'
       'qux(X):-baz(X), baz(Z), baz(Z), qux(Z).\n'
       '?qux(X).'
    )
    mocker.patch('app.config.TIMEOUT', 1)

    # act
    execute_result = PrologDService._execute(code=code)

    # assert
    assert execute_result.error == messages.MSG_1
    assert execute_result.result is None


def test_execute__dob_for_fact__ok():

    # arrange
    code = (
        'тест3:-РАВНО(X,1),ТЕРМ(T,[node,1,[X]]),ДОБ(T,[],999).\n'
        '?тест3.\n'
        '?node(1,A).'
    )
    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'ДА\n'
        'A=[1]'
    )
    assert exec_result.error is None


def test_execute__dob_for_rule__ok():

    # arrange
    code = (
        'тест4:-ТЕРМ(П,[чёт,Н]),ТЕРМ(Р,[УМНОЖЕНИЕ,М,2,0,Н]),ТЕРМ(С,[!]),'
        'ТЕРМ(Т,[ВЫВОД,"Чёт"]),ДОБ(П,[Р,С,Т],1),ТЕРМ(У,[чёт,Н]),'
        'ТЕРМ(Ф,[ВЫВОД,"Нечет"]),ТЕРМ(Х,[ЛОЖЬ]),ДОБ(У,[Ф,Х],2).\n'
        '?тест4.\n'
        '?чёт(4).\n'
        '?чёт(5).'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == (
        'ДА\n'
        'Чёт\n'
        'ДА\n'
        'Нечет\n'
        'НЕТ'
    )
    assert exec_result.error is None


def test_execute__invalid_vvod__error():

    # arrange
    code = (
        'baz:-#2+2#.\n'
        '?baz.'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result is None
    assert exec_result.error == (
        '2 Prolog failure'
    )


def test_execute__copy__ok():

    # arrange
    code = (
        '?КОПИЯ(идиотизм,Х,1,"и"). % Х=1\n'
        '?КОПИЯ(идиотизм,Х,-1,"и"). % Х=6'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == 'Х=1\nХ=6'
    assert exec_result.error is None


def test_execute__stack_ordering__ok():

    # arrange
    code = (
        'Фиб(1,1).\n'
        'Фиб(2,1).\n'
        'Фиб(Н,Ф):-БОЛЬШЕ(Н,2),Фиб(#Н-2#,А),Фиб(#Н-1#,Б),СЛОЖЕНИЕ(А,Б,Ф).\n'
        '?Фиб(20,Ф). % Ф=6765'
    )

    # act
    exec_result = PrologDService._execute(
        code=code
    )

    # assert
    assert exec_result.result == 'Ф=6765'
    assert exec_result.error is None


def test_check__true__ok():

    # arrange
    value = 'some value'
    right_value = 'some value'
    checker_func = (
        'def checker(right_value: str, value: str) -> bool:'
        '  return right_value == value'
    )

    # act
    check_result = PrologDService._check(
        checker_func=checker_func,
        right_value=right_value,
        value=value
    )

    # assert
    assert check_result is True


def test_check__false__ok():

    # arrange
    value = 'invalid value'
    right_value = 'some value'
    checker_func = (
        'def checker(right_value: str, value: str) -> bool:'
        '  return right_value == value'
    )

    # act
    check_result = PrologDService._check(
        checker_func=checker_func,
        right_value=right_value,
        value=value
    )

    # assert
    assert check_result is False


def test_check__invalid_checker_func__raise_exception():

    # arrange
    checker_func = (
        'def my_checker(right_value: str, value: str) -> bool:'
        '  return right_value == value'
    )

    # act
    with pytest.raises(CheckerException) as ex:
        PrologDService._check(
            checker_func=checker_func,
            right_value='value',
            value='value'
        )

    # assert
    assert ex.value.message == messages.MSG_2


def test_check__checker_func_no_return_instruction__raise_exception():

    # arrange
    checker_func = (
        'def checker(right_value: str, value: str) -> bool:'
        '  result = right_value == value'
    )

    # act
    with pytest.raises(CheckerException) as ex:
        PrologDService._check(
            checker_func=checker_func,
            right_value='value',
            value='value'
        )

    # assert
    assert ex.value.message == messages.MSG_3


def test_check__checker_func_return_not_bool__raise_exception():

    # arrange
    checker_func = (
        'def checker(right_value: str, value: str) -> bool:'
        '  return None'
    )

    # act
    with pytest.raises(CheckerException) as ex:
        PrologDService._check(
            checker_func=checker_func,
            right_value='value',
            value='value'
        )

    # assert
    assert ex.value.message == messages.MSG_4


def test_check__checker_func__invalid_syntax__raise_exception():

    # arrange
    checker_func = (
        'def checker(right_value: str, value: str) -> bool:'
        '  include(invalid syntax here)'
        '  return True'
    )

    # act
    with pytest.raises(CheckerException) as ex:
        PrologDService._check(
            checker_func=checker_func,
            right_value='value',
            value='value'
        )

    # assert
    assert ex.value.message == messages.MSG_5
    assert ex.value.details == 'invalid syntax (<string>, line 1)'


def test_debug__ok(mocker):

    # arrange
    execute_result = ExecuteResult(
        result='some execute code result',
        error='some compilation error'
    )
    execute_mock = mocker.patch(
        'app.service.main.PrologDService._execute',
        return_value=execute_result
    )
    data = DebugData(
        code='some code',
        data_in='some data_in'
    )

    # act
    debug_result = PrologDService.debug(data)

    # assert
    assert debug_result.result == execute_result.result
    assert debug_result.error == execute_result.error
    execute_mock.assert_called_once_with(
        code=data.code,
        data_in=data.data_in
    )


def test_testing__ok(mocker):

    # arrange
    execute_result = ExecuteResult(
        result='some execute code result',
        error='some compilation error'
    )
    execute_mock = mocker.patch(
        'app.service.main.PrologDService._execute',
        return_value=execute_result
    )
    check_result = mocker.Mock()
    check_mock = mocker.patch(
        'app.service.main.PrologDService._check',
        return_value=check_result
    )
    test_1 = TestData(
        data_in='some test input 1',
        data_out='some test out 1'
    )
    test_2 = TestData(
        data_in='some test input 2',
        data_out='some test out 2'
    )

    data = TestsData(
        code='some code',
        checker='some checker',
        tests=[test_1, test_2]
    )

    # act
    testing_result = PrologDService.testing(data)

    # assert
    tests_result = testing_result.tests
    assert len(tests_result) == 2
    assert tests_result[0].result == execute_result.result
    assert tests_result[0].error == execute_result.error
    assert tests_result[0].ok == check_result
    assert tests_result[1].result == execute_result.result
    assert tests_result[1].error == execute_result.error
    assert tests_result[1].ok == check_result
    assert execute_mock.call_args_list == [
        call(
            code=data.code,
            data_in=test_1.data_in
        ),
        call(
            code=data.code,
            data_in=test_2.data_in
        )
    ]
    assert check_mock.call_args_list == [
        call(
            checker_func=data.checker,
            right_value=test_1.data_out,
            value=execute_result.result
        ),
        call(
            checker_func=data.checker,
            right_value=test_2.data_out,
            value=execute_result.result
        )
    ]

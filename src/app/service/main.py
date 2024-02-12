import os
import re
import subprocess
from typing import Optional
from app.entities import (
    DebugData,
    TestsData
)
from app import config
from app.service import exceptions
from app.service.entities import ExecuteResult
from app.service import messages
from app.utils import clean_str


class PrologDService:

    @classmethod
    def _preexec_fn(cls):
        def change_process_user():
            os.setgid(config.SANDBOX_USER_UID)
            os.setuid(config.SANDBOX_USER_UID)
        return change_process_user()

    @classmethod
    def _get_stdin(
        cls,
        code: str,
        data_in: Optional[str] = None
    ) -> str:

        """ Remove empty lines in code
            Encode input lines with prefix $
            Then union input and code in one string """

        code = re.sub(r'(?:[\t ]*(?:\r?\n|\r))+', '\n', code)
        if data_in:
            stdin = '$' + data_in.strip()
            if stdin.find('\n') > 0:
                stdin = stdin.replace('\n', '\n$')
            return f'{stdin}\n{code.strip()}'
        else:
            return code.strip()

    @classmethod
    def _execute(
        cls,
        code: str,
        data_in: Optional[str] = None
    ) -> ExecuteResult:

        """ Передает компилятору код программы и входные данные
            возвращает результат работы программы, либо ошибку компиляции """

        proc = subprocess.Popen(
            args=['prologd', '-d=import/pld'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=cls._preexec_fn,
            text=True
        )
        try:
            result, error = proc.communicate(
                input=cls._get_stdin(data_in=data_in, code=code),
                timeout=config.TIMEOUT
            )
        except subprocess.TimeoutExpired:
            result, error = None, messages.MSG_1
        except Exception as ex:
            raise exceptions.ExecutionException(details=str(ex))
        finally:
            proc.kill()
        return ExecuteResult(
            result=clean_str(result or None),
            error=clean_str(error or None)
        )

    @classmethod
    def _validate_checker_func(cls, checker_func: str):
        if not checker_func.startswith(
            'def checker(right_value: str, value: str) -> bool:'
        ):
            raise exceptions.CheckerException(messages.MSG_2)
        if checker_func.find('return') < 0:
            raise exceptions.CheckerException(messages.MSG_3)

    @classmethod
    def _check(cls, checker_func: str, **checker_func_vars) -> bool:
        cls._validate_checker_func(checker_func)
        try:
            exec(
                checker_func + '\nresult = checker(right_value, value)',
                globals(),
                checker_func_vars
            )
        except Exception as ex:
            raise exceptions.CheckerException(
                message=messages.MSG_5,
                details=str(ex)
            )
        else:
            result = checker_func_vars['result']
            if not isinstance(result, bool):
                raise exceptions.CheckerException(messages.MSG_4)
            return result

    @classmethod
    def debug(cls, data: DebugData) -> DebugData:
        exec_result = cls._execute(
            code=data.code,
            data_in=data.data_in
        )
        data.result = exec_result.result
        data.error = exec_result.error
        return data

    @classmethod
    def testing(cls, data: TestsData) -> TestsData:
        for test in data.tests:
            exec_result = cls._execute(
                code=data.code,
                data_in=test.data_in
            )
            test.result = exec_result.result
            test.error = exec_result.error
            test.ok = cls._check(
                checker_func=data.checker,
                right_value=test.data_out,
                value=test.result
            )
        return data

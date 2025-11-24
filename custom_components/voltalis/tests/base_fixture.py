import json
from io import BytesIO, StringIO
from typing import Any, Generic, TypeVar

from dictdiffer import diff
from pydantic import BaseModel

from custom_components.voltalis.tests.utils.pretty_dict_differ import pretty_dictdiffer

T = TypeVar("T", bound=Any)


class BaseFixture(Generic[T]):
    """Base fixture for tests"""

    def __init__(self) -> None:
        """Set up before all tests"""
        self._result: T | list[T]
        self._exception: Exception

    def after_all(self) -> None:
        """Clean up after all tests"""

    def before_each(self) -> None:
        """Set up before each test"""

        del self._result
        del self._exception
        self._current_user = None

    def after_each(self) -> None:
        """Clean up after each test"""

    # --------------------------------------
    # Assert success
    # --------------------------------------
    def then_result_should_be(self, expected_result: T) -> None:
        """Assert the result is the expected one"""
        __tracebackhide__ = True

        assert hasattr(self, "_result"), self._exception
        assert isinstance(self._result, type(expected_result)), self._result

        self.compare_data(self._result, expected_result)

    def then_results_should_be(self, expected_results: list[T]) -> None:
        """Assert the results are the expected ones"""
        __tracebackhide__ = True

        assert hasattr(self, "_result"), self._exception
        assert isinstance(self._result, type(expected_results)), self._result

        self.compare_lists(self._result, expected_results)

    # --------------------------------------
    # Assert errors
    # --------------------------------------
    def then_exception_type_should_be(self, expected_exception_type: type[Exception]) -> None:
        """Assert the exception type is the expected one"""
        __tracebackhide__ = True

        assert hasattr(self, "_exception"), self._result

        self.compare_exception_type(self._exception, expected_exception_type)

    def then_exception_should_be(self, expected_exception: Exception) -> None:
        """Assert the exception is the expected one"""
        __tracebackhide__ = True

        assert hasattr(self, "_exception"), self._result

        self.compare_exception_type(self._exception, type(expected_exception))
        self.compare_data(self._exception.args[0], expected_exception.args[0])

    # --------------------------------------
    # Utils
    # --------------------------------------
    @classmethod
    def compare_exception_type(cls, exception: Exception, expected_exception_type: type[Exception]) -> None:
        assert type(exception) is expected_exception_type, f"{type(exception)}\n\n{expected_exception_type}"

    @classmethod
    def compare_exception(cls, exception: Exception, expected_exception: Exception) -> None:
        cls.compare_exception_type(exception, type(expected_exception))
        assert str(exception) == str(expected_exception), f"{exception}\n\n{expected_exception}"

    @classmethod
    def compare_data(cls, data: Any, expected_data: Any) -> None:
        """Compare two Any type"""
        __tracebackhide__ = True

        # Check if one of the data is None
        assert not (expected_data is not None and data is None), "data should not be None"
        assert not (expected_data is None and data is not None), "data should be None"

        # If the expected data is a list, compare the list
        if isinstance(expected_data, list):
            cls.compare_lists(data, expected_data)
            return

        # If the expected data is a BytesIO or StringIO, compare the bytes
        if isinstance(expected_data, (BytesIO, StringIO)):
            cls.compare_bytes(data, expected_data)
            return

        # If the expected data is a tuple, compare the tuple
        if isinstance(expected_data, tuple):
            cls.compare_tuples(data, expected_data)
            return

        # If the expected data is an Exception, compare the exception
        if isinstance(expected_data, Exception):
            cls.compare_exception(data, expected_data)
            return

        # Check if both data are the same type
        assert isinstance(data, type(expected_data)), f"Types do not match: {type(data)} != {type(expected_data)}"

        # If the data is a BaseModel, compare the model_dump
        if isinstance(expected_data, BaseModel):
            expected_data = expected_data.model_dump()
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # If the dict contains exceptions, separate the exceptions from the data
        # The diff function does not support exceptions
        # TODO: Find a better way to compare exceptions
        expected_data_exceptions: dict = {}
        data_exceptions: dict = {}
        if isinstance(expected_data, dict):
            expected_data_exceptions = {
                key: value for key, value in expected_data.items() if isinstance(value, Exception)
            }
            expected_data = {key: value for key, value in expected_data.items() if not isinstance(value, Exception)}

        if isinstance(data, dict):
            data_exceptions = {key: value for key, value in data.items() if isinstance(value, Exception)}
            data = {key: value for key, value in data.items() if not isinstance(value, Exception)}

        cls.compare_lists(list(data_exceptions.keys()), list(expected_data_exceptions.keys()))
        cls.compare_lists(list(data_exceptions.values()), list(expected_data_exceptions.values()))

        # Compare the data
        diff_list = list(diff(expected_data, data, tolerance=1e-5))

        # Get the data id or codename if available for easier debugging
        __ids_columns = ["id", "codename", "product_id", "env_id", "organization_codename"]
        data_id = None
        data_id_col = None
        if isinstance(data, dict):
            for key in __ids_columns:
                if key in data:
                    data_id_col = key
                    data_id = data[key]
                    break
        data_id_text = f" ({data_id_col}={data_id})" if data_id is not None else ""
        assert len(diff_list) == 0, (
            f"Output are different from the expected ones{data_id_text}:\n{pretty_dictdiffer(diff_list)}"
        )

    @classmethod
    def compare_tuples(cls, data: tuple, expected_data: tuple) -> None:
        """Compare two tuples"""

        # Check if both tuples have the same length
        assert len(data) == len(expected_data), f"data is {len(data)} and expected_data is {len(expected_data)}"

        # Compare each element of the tuples
        for index in range(len(data)):
            cls.compare_data(data[index], expected_data[index])

    @classmethod
    def compare_bytes(cls, data: bytes | BytesIO | StringIO, expected_data: bytes | BytesIO | StringIO) -> None:
        """Compare two bytes"""

        if isinstance(data, bytes) and isinstance(expected_data, bytes):
            assert data == expected_data
        elif isinstance(data, BytesIO) and isinstance(expected_data, BytesIO):
            assert data.getvalue() == expected_data.getvalue()
        elif isinstance(data, StringIO) and isinstance(expected_data, StringIO):
            rvalue = data.getvalue()
            evalue = expected_data.getvalue()

            # Parse JSON to compare the content
            try:
                rdict: list = json.loads(rvalue)
                edict: list = json.loads(evalue)

                for index, expected_product in enumerate(edict):
                    assert not (
                        ddiff := list(
                            diff(
                                expected_product,
                                rdict[index],
                            )
                        )
                    ), f"Output are different from the expected ones (index={index}):\n{pretty_dictdiffer(ddiff)}"
            except json.JSONDecodeError:
                assert rvalue == evalue, f"Output are different from the expected ones:\n{evalue}\n\n{rvalue}"
        else:
            assert False, f"Expected {type(expected_data)} but got {type(data)}"

    @classmethod
    def compare_lists(cls, lst: list[Any], expected_lst: list[Any]) -> None:
        """Compare two lists of any type"""
        __tracebackhide__ = True

        # Compare the length of the lists
        assert len(lst) == len(expected_lst), f"lst is {len(lst)} and expected_lst is {len(expected_lst)}"

        # Compare each element of the lists
        for index in range(len(lst)):
            cls.compare_data(lst[index], expected_lst[index])

    @classmethod
    def compare_dicts(cls, data: dict, expected_data: dict) -> None:
        """Compare two dicts"""

        # Check if both dicts have the same keys
        assert set(data.keys()) == set(expected_data.keys()), (
            f"Keys do not match: {data.keys()} != {expected_data.keys()}"
        )

        # Compare each element of the dicts
        for key in data.keys():
            cls.compare_data(data[key], expected_data[key])

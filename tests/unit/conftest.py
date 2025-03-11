from unittest import mock

import pytest


@pytest.fixture
def session_mock():
    return mock.Mock()


@pytest.fixture
def internal_session_mock():
    return mock.Mock()


@pytest.fixture
def context_manager_mock_factory():
    def factory(obj):
        class mockedcontextmanager:
            def __enter__(self, *args, **kwargs):
                return obj

            def __exit__(self, *args, **kwargs):
                return

        return mockedcontextmanager()

    return factory


@pytest.fixture
def session_factory_mock(internal_session_mock, context_manager_mock_factory):
    return mock.Mock(return_value=context_manager_mock_factory(internal_session_mock))

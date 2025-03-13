import functools
import logging
from dataclasses import fields
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from django.db.models import Model  # type:ignore[import-untyped]
from sqlalchemy import Row

from dbrepos.core.exceptions import BaseRepoException
from dbrepos.core.types import ORM

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    TDataclass = TypeVar("TDataclass", bound=DataclassInstance)
else:
    TDataclass = TypeVar("TDataclass")


def strict(func: Callable | None = None) -> Callable:
    """Decorator that handles `strict` parameter

    Args:
        func (Callable | None, optional): Function to decorate.
            Defaults to None

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            strict_ = kwargs.get("strict", True)
            try:
                return func(*args, **kwargs)
            except BaseRepoException:
                if strict_:
                    raise
                return None

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def handle_error(
    func: Callable | None = None,
    *,
    logger: logging.Logger = logger,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that handles any error and logs this error to specified logger

    Args:
        func (Callable | None, optional): Function to decorate.
            Defaults to None
        logger (logging.Logger, optional): Logger for errors.
            Defaults to common_logger
        exceptions (Tuple[Type[Exception], ...], optional): Exceptions to catch.
            Defaults to (Exception,)

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.debug(str(e))
                logger.error(
                    f"Expected error - {str(e)}",
                    exc_info=e,
                )
                raise
            except Exception as e:
                logger.debug(str(e))
                logger.critical(
                    f"Unexpected error - {str(e)}",
                    exc_info=e,
                )
                raise

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


def session(func: Callable | None = None) -> Callable:
    """Decorator that injects session as `session` kwarg

    If session already in kwargs, new session will not be injected

    Args:
        func (Callable): Function to decorate

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            factory = getattr(self, "session_factory", None)
            if factory is None:
                raise BaseRepoException("Cannot locate session_factory attribute.")

            if kwargs.get("session", None) is not None:
                return func(self, *args, **kwargs)

            with factory() as session:
                kwargs["session"] = session
                return func(self, *args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)


def convert(
    func: Callable | None = None,
    *,
    many: bool = False,
    orm: ORM | None = None,
) -> Callable:
    """Decorator that converts function result
        item(s) to passed in `convert_to` dataclass

    Args:
        func (Callable | None, optional): Function to decorate.
            Defaults to None
        many (bool, optional): Flag that marks function return type as a collection.
            Defaults to False
        orm (ORM | None, optional): Used ORM inside a function.
            Defaults to None

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            convert_to: Type | None = kwargs.get("convert_to", None)
            if convert_to is None:
                if (
                    not many
                    and orm is not None
                    and orm == "alchemy"
                    and isinstance(result, Sequence)
                    and result
                    and isinstance(result[0], Iterable)
                ):
                    # unpack (imho, weird) alchemy single-row
                    # [(value, value, value)] to (value, value, value)
                    return result[0]
                return result

            def as_one(instance):
                if isinstance(instance, Sequence):
                    if instance and isinstance(instance[0], Iterable):
                        return convert_to(*instance[0])
                    return convert_to(*instance)
                if isinstance(instance, Row):
                    return convert_to(*instance[0])
                if isinstance(instance, Model):
                    return convert_to(
                        **{
                            field.name: getattr(instance, field.name)
                            for field in fields(convert_to)
                        }
                    )
                return instance

            if not many:
                return as_one(result)

            if not isinstance(result, Iterable):
                return result

            return [as_one(instance) for instance in result]

        return wrapper

    if func is None:
        return decorator

    return decorator(func)

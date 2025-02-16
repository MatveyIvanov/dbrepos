import functools
import logging
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger(__name__)


def strict(func: Callable | None = None) -> Callable:
    def outer(func: Callable) -> Callable:
        def inner(*args: Any, **kwargs: Any) -> Any:
            strict_ = kwargs.get("strict", True)
            try:
                return func(*args, **kwargs)
            except Exception:  # TODO
                if strict_:
                    raise
                return None

        return inner

    if func is None:
        return outer

    return outer(func)


def handle_error(
    func: Callable | None = None,
    *,
    logger: logging.Logger = logger,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator that handles any error and logs this error to specified logger

    Args:
        func (Callable | None, optional): Function to decorate.
            Defaults to None
        logger (logging.Logger, optional): Logger for errors.
            Defaults to common_logger
        exception (Tuple[Type[Exception], ...], optional): Exceptions to catch.
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
                logging.debug(str(e))
                logger.error(
                    f"Unexpected error - {str(e)}",
                    exc_info=e,
                )
                raise

        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


def session(func: Callable | None = None) -> Callable:
    """
    Decorator that injects session as `session` kwarg.
    If session already in kwargs, new session will not be injected

    Args:
        func (Callable): Function to decorate

    Returns:
        Callable: Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            if (
                factory := getattr(self, "session_factory", None)
            ) is None or "session" in kwargs.keys():
                return func(*args, **kwargs)

            with factory() as session:
                kwargs["session"] = session
                return func(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator

    return decorator(func)

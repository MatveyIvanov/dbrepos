from inspect import isawaitable
import logging
from contextlib import contextmanager, asynccontextmanager
from typing import Callable, Iterator, AsyncIterator, Type

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlalchemy.ext.asyncio as aorm
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("sqlalchemy")


metadata = sa.MetaData()


AlchemyTable = sa.Table(
    "table",
    metadata,
    sa.Column("id", sa.BigInteger, primary_key=True),
    sa.Column("name", sa.String(100)),
    sa.Column("is_deleted", sa.Boolean),
)


class AlchemyDatabase:
    """
    Database class for client management
    """

    def __init__(
        self,
        db_url: str,
        create_engine: Callable[..., sa.Engine | aorm.AsyncEngine],
        scoped_session: Type[orm.scoped_session | aorm.async_scoped_session],
        session_maker: Type[orm.sessionmaker | aorm.async_sessionmaker],
        session_class: Type[orm.Session | aorm.AsyncSession],
        scope_func: Callable | None = None,
    ) -> None:
        self._engine = create_engine(db_url, future=True, echo=True)
        self._session_factory = scoped_session(
            session_maker(
                class_=session_class,
                autocommit=False,
                autoflush=True,
                bind=self._engine,
            ),
            scopefunc=scope_func,
        )
        self._async = False

        session: orm.Session | aorm.AsyncSession = self._session_factory()
        if isawaitable(session.close):
            self._async = True

    @contextmanager
    def session(self) -> Iterator[orm.Session]:
        """
        Context manager that produces sync session.
        Handles commits, rollbacks and session closing.
        """
        assert not self._async, "Async session configured, use `asession` instead."
        session: orm.Session = self._session_factory()
        try:
            logging.debug("YIELDING...")
            yield session
        except Exception as e:
            logging.debug("ROLLBACKING... ")
            session.rollback()
            logging.debug("ERROR... ", str(e))
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            raise
        else:
            logging.debug("EXPUNGING...")
            # we want all objects to be
            # usable outside of the session
            session.expunge_all()
            logging.debug("COMMITTING... ")
            try:
                session.commit()
            except SQLAlchemyError as e:
                logging.debug("ERROR COMMITTING...", str(e))
                session.rollback()
                logger.error(
                    f"Session rollback because of exception on commit - {str(e)}",
                    exc_info=e,
                )
        finally:
            logging.debug("CLOSING... ")
            session.close()

    @asynccontextmanager
    async def asession(self) -> AsyncIterator[aorm.AsyncSession]:
        """
        Context manager that produces async session.
        Handles commits, rollbacks and session closing.
        """
        assert self._async, "Sync session configured, use `session` instead."
        session: aorm.AsyncSession = self._session_factory()
        try:
            logging.debug("YIELDING...")
            yield session
        except Exception as e:
            logging.debug("ROLLBACKING... ")
            await session.rollback()
            logging.debug("ERROR... ", str(e))
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            raise
        else:
            logging.debug("EXPUNGING...")
            # we want all objects to be
            # usable outside of the session
            session.expunge_all()
            logging.debug("COMMITTING... ")
            try:
                await session.commit()
            except SQLAlchemyError as e:
                logging.debug("ERROR COMMITTING...", str(e))
                await session.rollback()
                logger.error(
                    f"Session rollback because of exception on commit - {str(e)}",
                    exc_info=e,
                )
        finally:
            logging.debug("CLOSING... ")
            await session.close()


AlchemySyncDatabase = AlchemyDatabase(
    db_url="sqlite:///test.db",
    create_engine=sa.create_engine,
    scoped_session=orm.scoped_session,
    session_maker=orm.sessionmaker,
    session_class=orm.Session,
    scope_func=None,
)
# AlchemyAsyncDatabase = AlchemyDatabase(
#     db_url="sqlite+aiosqlite://",
#     create_engine=aorm.create_async_engine,
#     scoped_session=aorm.async_scoped_session,
#     session_maker=aorm.async_sessionmaker,
#     session_class=aorm.AsyncSession,
#     scope_func=asyncio.current_task,
# )

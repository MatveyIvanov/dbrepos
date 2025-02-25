import pytest

from repo.core.exceptions import BaseRepoException

multi_repo_parametrize = pytest.mark.parametrize(
    "repo,runner",
    (
        ("django_repo", "django"),
        ("django_repo_soft_deletable", "django"),
        ("alchemy_repo", "alchemy"),
        ("alchemy_repo_soft_deletable", "alchemy"),
    ),
)


strictness_parametrize = (
    lambda field, value, bad_field_exc: pytest.mark.parametrize(  # noqa:E731
        "preload,name,value,strict,expected_preload_index,expected_error",
        (
            (
                ({"name": "name", "is_deleted": False},),
                f"{field}_unknown",
                value,
                False,
                None,
                bad_field_exc,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                f"{field}_unknown",
                value,
                True,
                None,
                bad_field_exc,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                f"{value}_unknown",
                False,
                None,
                None,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                f"{value}_unknown",
                True,
                None,
                BaseRepoException,
            ),
            (
                ({"name": "name", "is_deleted": False},),
                field,
                value,
                False,
                0,
                None,
            ),
            (
                ({"name": "name", "is_deleted": True},),
                field,
                value,
                True,
                0,
                None,
            ),
        ),
    )
)

strictness_by_pk_parametrize = lambda value: pytest.mark.parametrize(  # noqa:E731
    "preload,value,strict,expected_preload_index,expected_error",
    (
        (
            ({"name": "name", "is_deleted": False},),
            value + 1,
            False,
            None,
            None,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            value + 1,
            True,
            None,
            BaseRepoException,
        ),
        (
            ({"name": "name", "is_deleted": False},),
            value,
            False,
            0,
            None,
        ),
        (
            ({"name": "name", "is_deleted": True},),
            value,
            True,
            0,
            None,
        ),
    ),
)

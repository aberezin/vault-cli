import pytest

from vault_cli import environment


def test_exec_command(mocker):
    execvpe = mocker.patch("os.execvpe")

    environment.exec_command(["a", "b"], {"c": "d"})

    execvpe.assert_called_with("a", ("a", "b"), {"c": "d"})


@pytest.mark.parametrize(
    "base_path, path, prefix, expected",
    [
        ("", "a", None, "A_MYATTR"),
        ("a", "a", None, "A_MYATTR"),
        ("", "a/b", None, "A_B_MYATTR"),
        ("a", "a/b", None, "A_B_MYATTR"),
        ("a/b", "a/b/c", None, "B_C_MYATTR"),
        ("", "a", "foo", "FOO_A_MYATTR"),
        ("a", "a", "foo", "FOO_MYATTR"),
        ("", "a/b", "foo", "FOO_A_B_MYATTR"),
        ("a", "a/b", "foo", "FOO_B_MYATTR"),
        ("a/b", "a/b/c", "foo", "FOO_C_MYATTR"),
    ],
)
def test_make_env_key(base_path, path, prefix, expected):
    assert (
        environment.make_env_key(
            base_path=base_path, path=path, name="myattr", prefix=prefix
        )
        == expected
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        ("a", "a"),
        (1, "1"),
        (1.2, "1.2"),
        (True, "true"),
        (None, "null"),
        ([1], "[1]"),
        ({"a": ["b"]}, '{"a": ["b"]}'),
    ],
)
def test_make_env_value(value, expected):
    assert environment.make_env_value(value=value) == expected

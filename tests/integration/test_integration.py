import os
import subprocess

import pytest

import vault_cli
from vault_cli import cli


def call(cli_runner, *args):
    call = cli_runner.invoke(cli.cli, *args)
    assert call.exit_code == 0, call.output
    return call


@pytest.fixture
def clean_vault(cli_runner):
    call(cli_runner, ["delete-all", "-f"])
    yield
    call(cli_runner, ["delete-all", "-f"])


def test_integration_cli(cli_runner, clean_vault):

    call(cli_runner, ["set", "a", "b"])

    assert call(cli_runner, ["get", "a", "--text"]).output == "b\n"

    assert call(cli_runner, ["get", "a"]).output == "b\n"

    assert call(cli_runner, ["get", "a", "--yaml"]).output == "--- b\n...\n"

    # Both testing it and using it to clean the vault
    call(cli_runner, ["delete-all", "--force"])

    assert call(cli_runner, ["list"]).output == "\n"

    call(cli_runner, ["set", "a", "b"])

    assert call(cli_runner, ["list"]).output == "a\n"

    call(cli_runner, ["set", "c/d", "e"])

    assert call(cli_runner, ["get", "c/d"]).output == "e\n"

    assert call(cli_runner, ["list"]).output == "a\nc/\n"

    assert call(cli_runner, ["list", "c"]).output == "d\n"

    assert call(cli_runner, ["get-all", ""]).output == (
        """---
a: b
c:
  d: e
"""
    )

    assert call(cli_runner, ["get-all", "--flat", ""]).output == (
        """---
a: b
c/d: e
"""
    )

    call(cli_runner, ["delete", "a"])

    assert call(cli_runner, ["list"]).output == "c/\n"

    call(cli_runner, ["delete-all", "--force"])

    assert call(cli_runner, ["list"]).output == "\n"

    assert call(cli_runner, ["lookup-token"]).output.startswith("---\nauth:")


def test_integration_lib(clean_vault):

    client = vault_cli.get_client()

    client.set_secret("a", "b")

    assert client.get_secret("a") == "b"

    assert "a" in list(client.delete_all_secrets(""))

    assert client.list_secrets("") == []

    client.set_secret("a", "b")

    assert client.list_secrets("") == ["a"]

    client.set_secret("c/d", "e")

    assert client.get_secret("c/d") == "e"

    assert client.list_secrets("") == ["a", "c/"]

    assert client.list_secrets("c") == ["d"]

    assert client.get_all_secrets("") == {"a": "b", "c": {"d": "e"}}

    client.delete_secret("a")

    assert client.list_secrets("") == ["c/"]

    assert list(client.delete_all_secrets("")) == ["c/d"]

    assert client.lookup_token()["data"]

    # Use hvac client directly in order to write values that are not in a "value" attribute
    client.client.write(
        client._build_full_path("novalue"), username="name", password="pass"
    )
    assert client.get_secret("novalue") == {"password": "pass", "username": "name"}


def test_env_var_config():
    # Test env var config
    os.environ["VAULT_CLI_TOKEN"] = "some-other-token"
    with pytest.raises(vault_cli.VaultAPIException):
        vault_cli.get_client().set_secret("a", "b")


def check_call(command):
    subprocess.check_call(
        command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


@pytest.fixture
def set_ACD(cli_runner):
    call(cli_runner, ["set", "A", "B"])
    call(cli_runner, ["set", "C/D", "E"])
    yield
    call(cli_runner, ["delete", "A"])
    call(cli_runner, ["delete", "C/D"])


def test_boostrap_env(clean_vault, set_ACD):
    env = subprocess.check_output("vault env -p A -p C -- env".split())

    assert b"A=B\n" in env
    assert b"D=E\n" in env

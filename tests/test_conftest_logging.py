import os
from unittest.mock import Mock

from conftest import pytest_sessionstart


def _simulate_configure_logging_logic(dotenv_values_return=None, existing_log_level=None, single_test_env=None):
    """Helper function to simulate the configure_logging logic for testing"""
    if dotenv_values_return is None:
        dotenv_values_return = {}

    dotenv_log_level = dotenv_values_return.get("LOG_LEVEL")

    if dotenv_log_level and not existing_log_level:
        return dotenv_log_level
    elif not existing_log_level:
        is_single_test = single_test_env == "1"
        if is_single_test:
            return "DEBUG"
        else:
            return "WARNING"
    else:
        return existing_log_level


class TestLoggingConfiguration:
    """Test the conditional logging behavior based on test count"""

    def test_pytest_sessionstart_single_test__sets_environment_variable(self):
        """
        Tests that pytest_sessionstart sets environment variable correctly for single test.
        """
        mock_session = Mock()
        mock_session.testscollected = 1

        mock_config = Mock()
        mock_config.args = [
            "tests/workflows/basic_emitter_workflow/tests/test_workflow.py::test_run_workflow__happy_path"
        ]
        mock_session.config = mock_config

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        pytest_sessionstart(mock_session)

        assert os.environ["_PYTEST_SINGLE_TEST"] == "1"

        del os.environ["_PYTEST_SINGLE_TEST"]

    def test_pytest_sessionstart_multiple_tests__sets_environment_variable(self):
        """
        Tests that pytest_sessionstart sets environment variable correctly for multiple tests.
        """
        mock_session = Mock()
        mock_session.testscollected = 5

        mock_config = Mock()
        mock_config.args = ["tests/workflows/basic_emitter_workflow/tests/test_workflow.py"]
        mock_session.config = mock_config

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        pytest_sessionstart(mock_session)

        assert os.environ["_PYTEST_SINGLE_TEST"] == "0"

        del os.environ["_PYTEST_SINGLE_TEST"]

    def test_logging_logic_single_test__returns_debug_level(self):
        """
        Tests that logging logic returns DEBUG level for single test.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level=None, single_test_env="1"
        )

        assert result == "DEBUG"

    def test_logging_logic_multiple_tests__returns_warning_level(self):
        """
        Tests that logging logic returns WARNING level for multiple tests.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level=None, single_test_env="0"
        )

        assert result == "WARNING"

    def test_logging_logic_existing_log_level__preserves_existing_value(self):
        """
        Tests that logging logic preserves existing LOG_LEVEL environment variable.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level="ERROR", single_test_env="1"
        )

        assert result == "ERROR"

    def test_logging_logic_dotenv_log_level__uses_dotenv_value(self):
        """
        Tests that logging logic uses LOG_LEVEL from .env file.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"}, existing_log_level=None, single_test_env="1"
        )

        assert result == "INFO"

    def test_logging_logic_dotenv_overrides_conditional__uses_dotenv_value(self):
        """
        Tests that dotenv LOG_LEVEL takes precedence over conditional logic.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"}, existing_log_level=None, single_test_env="0"
        )

        assert result == "INFO"

    def test_logging_logic_existing_env_overrides_dotenv__preserves_existing(self):
        """
        Tests that existing LOG_LEVEL env var takes precedence over dotenv.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"}, existing_log_level="ERROR", single_test_env="1"
        )

        assert result == "ERROR"

    def test_integration_pytest_hook_and_logging_single_test__debug_level(self):
        """
        Integration test: pytest hook + logging logic for single test results in DEBUG level.
        """
        mock_session = Mock()
        mock_session.testscollected = 1

        mock_config = Mock()
        mock_config.args = [
            "tests/workflows/basic_emitter_workflow/tests/test_workflow.py::test_run_workflow__happy_path"
        ]
        mock_session.config = mock_config

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        try:
            pytest_sessionstart(mock_session)

            result = _simulate_configure_logging_logic(
                dotenv_values_return={}, existing_log_level=None, single_test_env=os.environ.get("_PYTEST_SINGLE_TEST")
            )

            assert result == "DEBUG"

        finally:
            if "_PYTEST_SINGLE_TEST" in os.environ:
                del os.environ["_PYTEST_SINGLE_TEST"]

    def test_integration_pytest_hook_and_logging_multiple_tests__warning_level(self):
        """
        Integration test: pytest hook + logging logic for multiple tests results in WARNING level.
        """
        mock_session = Mock()
        mock_session.testscollected = 3

        mock_config = Mock()
        mock_config.args = ["tests/workflows/basic_emitter_workflow/tests/test_workflow.py"]
        mock_session.config = mock_config

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        try:
            pytest_sessionstart(mock_session)

            result = _simulate_configure_logging_logic(
                dotenv_values_return={}, existing_log_level=None, single_test_env=os.environ.get("_PYTEST_SINGLE_TEST")
            )

            assert result == "WARNING"

        finally:
            if "_PYTEST_SINGLE_TEST" in os.environ:
                del os.environ["_PYTEST_SINGLE_TEST"]

    def test_pytest_sessionstart_cli_tests__sets_cli_environment_variable(self):
        """
        Tests that pytest_sessionstart sets CLI environment variable when CLI tests are present.
        """
        mock_session = Mock()
        mock_session.testscollected = 5

        mock_config = Mock()
        mock_config.args = ["ee/vellum_cli/tests/test_ping.py::test_ping__happy_path"]
        mock_session.config = mock_config

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]
        if "_PYTEST_CLI_TESTS" in os.environ:
            del os.environ["_PYTEST_CLI_TESTS"]

        try:
            pytest_sessionstart(mock_session)

            assert "_PYTEST_SINGLE_TEST" not in os.environ
            assert os.environ["_PYTEST_CLI_TESTS"] == "1"

        finally:
            if "_PYTEST_SINGLE_TEST" in os.environ:
                del os.environ["_PYTEST_SINGLE_TEST"]
            if "_PYTEST_CLI_TESTS" in os.environ:
                del os.environ["_PYTEST_CLI_TESTS"]

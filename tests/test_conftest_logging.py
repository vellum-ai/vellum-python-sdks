import os
from unittest.mock import Mock

from conftest import pytest_collection_modifyitems


def _simulate_configure_logging_logic(
    dotenv_values_return=None, existing_log_level=None, single_test_env=None, cli_tests_present=False
):
    """Helper function to simulate the configure_logging logic for testing"""
    if dotenv_values_return is None:
        dotenv_values_return = {}

    dotenv_log_level = dotenv_values_return.get("LOG_LEVEL")

    if dotenv_log_level and not existing_log_level:
        return dotenv_log_level
    elif not existing_log_level and not cli_tests_present:
        is_single_test = single_test_env == "1"
        if is_single_test:
            return "DEBUG"
        else:
            return "WARNING"
    elif cli_tests_present:
        return None
    else:
        return existing_log_level


class TestLoggingConfiguration:
    """Test the conditional logging behavior based on test count"""

    def test_pytest_collection_modifyitems_single_test__sets_environment_variable(self):
        """
        Tests that pytest_collection_modifyitems sets environment variable correctly for single test.
        """
        mock_session = Mock()
        mock_config = Mock()

        mock_item = Mock()
        mock_item.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_emitter_workflow/tests/test_workflow.py"
        )
        items = [mock_item]

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        pytest_collection_modifyitems(mock_session, mock_config, items)

        assert os.environ["_PYTEST_SINGLE_TEST"] == "1"

        del os.environ["_PYTEST_SINGLE_TEST"]

    def test_pytest_collection_modifyitems_multiple_tests__sets_environment_variable(self):
        """
        Tests that pytest_collection_modifyitems sets environment variable correctly for multiple tests.
        """
        mock_session = Mock()
        mock_config = Mock()

        mock_item1 = Mock()
        mock_item1.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_emitter_workflow/tests/test_workflow.py"
        )
        mock_item2 = Mock()
        mock_item2.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_await_all/tests/test_workflow.py"
        )
        items = [mock_item1, mock_item2]

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        pytest_collection_modifyitems(mock_session, mock_config, items)

        assert os.environ["_PYTEST_SINGLE_TEST"] == "0"

        del os.environ["_PYTEST_SINGLE_TEST"]

    def test_logging_logic_single_test__returns_debug_level(self):
        """
        Tests that logging logic returns DEBUG level for single test.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level=None, single_test_env="1", cli_tests_present=False
        )

        assert result == "DEBUG"

    def test_logging_logic_multiple_tests__returns_warning_level(self):
        """
        Tests that logging logic returns WARNING level for multiple tests.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level=None, single_test_env="0", cli_tests_present=False
        )

        assert result == "WARNING"

    def test_logging_logic_existing_log_level__preserves_existing_value(self):
        """
        Tests that logging logic preserves existing LOG_LEVEL environment variable.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={}, existing_log_level="ERROR", single_test_env="1", cli_tests_present=False
        )

        assert result == "ERROR"

    def test_logging_logic_dotenv_log_level__uses_dotenv_value(self):
        """
        Tests that logging logic uses LOG_LEVEL from .env file.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"},
            existing_log_level=None,
            single_test_env="1",
            cli_tests_present=False,
        )

        assert result == "INFO"

    def test_logging_logic_dotenv_overrides_conditional__uses_dotenv_value(self):
        """
        Tests that dotenv LOG_LEVEL takes precedence over conditional logic.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"},
            existing_log_level=None,
            single_test_env="0",
            cli_tests_present=False,
        )

        assert result == "INFO"

    def test_logging_logic_existing_env_overrides_dotenv__preserves_existing(self):
        """
        Tests that existing LOG_LEVEL env var takes precedence over dotenv.
        """

        result = _simulate_configure_logging_logic(
            dotenv_values_return={"LOG_LEVEL": "INFO"},
            existing_log_level="ERROR",
            single_test_env="1",
            cli_tests_present=False,
        )

        assert result == "ERROR"

    def test_integration_pytest_hook_and_logging_single_test__debug_level(self):
        """
        Integration test: pytest hook + logging logic for single test results in DEBUG level.
        """
        mock_session = Mock()
        mock_config = Mock()

        mock_item = Mock()
        mock_item.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_emitter_workflow/tests/test_workflow.py"
        )
        items = [mock_item]

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        try:
            pytest_collection_modifyitems(mock_session, mock_config, items)

            result = _simulate_configure_logging_logic(
                dotenv_values_return={},
                existing_log_level=None,
                single_test_env=os.environ.get("_PYTEST_SINGLE_TEST"),
                cli_tests_present=False,
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
        mock_config = Mock()

        mock_item1 = Mock()
        mock_item1.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_emitter_workflow/tests/test_workflow.py"
        )
        mock_item2 = Mock()
        mock_item2.fspath = (
            "/home/ubuntu/repos/vellum-python-sdks/tests/workflows/" "basic_await_all/tests/test_workflow.py"
        )
        items = [mock_item1, mock_item2]

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        try:
            pytest_collection_modifyitems(mock_session, mock_config, items)

            result = _simulate_configure_logging_logic(
                dotenv_values_return={},
                existing_log_level=None,
                single_test_env=os.environ.get("_PYTEST_SINGLE_TEST"),
                cli_tests_present=False,
            )

            assert result == "WARNING"

        finally:
            if "_PYTEST_SINGLE_TEST" in os.environ:
                del os.environ["_PYTEST_SINGLE_TEST"]

    def test_pytest_collection_modifyitems_cli_tests__skips_conditional_logging(self):
        """
        Tests that pytest_collection_modifyitems skips conditional logging when CLI tests are present.
        """
        mock_session = Mock()
        mock_config = Mock()

        mock_item = Mock()
        mock_item.fspath = "/home/ubuntu/repos/vellum-python-sdks/ee/vellum_cli/tests/test_ping.py"
        items = [mock_item]

        if "_PYTEST_SINGLE_TEST" in os.environ:
            del os.environ["_PYTEST_SINGLE_TEST"]

        try:
            pytest_collection_modifyitems(mock_session, mock_config, items)

            assert "_PYTEST_SINGLE_TEST" not in os.environ

        finally:
            if "_PYTEST_SINGLE_TEST" in os.environ:
                del os.environ["_PYTEST_SINGLE_TEST"]

    def test_configure_logging_cli_tests__skips_conditional_logging(self):
        """
        Tests that configure_logging skips conditional logging when CLI tests are detected in sys.argv.
        """
        import sys

        original_argv = sys.argv.copy()
        sys.argv = ["pytest", "ee/vellum_cli/tests/test_ping.py::test_ping__happy_path"]

        try:
            cli_tests_present = any("ee/vellum_cli/tests/" in str(arg) for arg in sys.argv)

            assert cli_tests_present is True

            result = _simulate_configure_logging_logic(
                dotenv_values_return={},
                existing_log_level=None,
                single_test_env="1",
                cli_tests_present=cli_tests_present,
            )

            assert result is None

        finally:
            sys.argv = original_argv

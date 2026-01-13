import pytest
from unittest.mock import patch

from vellum.utils.vellum_client import create_vellum_client, create_vellum_environment


class TestCreateVellumClient:
    """Tests for create_vellum_client and create_vellum_environment."""

    @pytest.mark.parametrize(
        ["api_url", "predict_api_url", "expected_predict_url"],
        [
            (None, None, "https://predict.vellum.ai"),
            (None, "https://custom-predict.example.com", "https://custom-predict.example.com"),
            ("CUSTOM_API_URL", None, "https://predict.vellum.ai"),
            ("CUSTOM_API_URL", "https://custom-predict.example.com", "https://custom-predict.example.com"),
        ],
        ids=[
            "defaults_to_standard_predict_url",
            "predict_api_url_overrides_default",
            "api_url_env_var_does_not_affect_predict_when_not_set",
            "predict_api_url_takes_precedence_over_api_url",
        ],
    )
    def test_create_vellum_client__predict_url_resolution(self, api_url, predict_api_url, expected_predict_url):
        """Tests that predict_api_url is resolved correctly based on provided parameters."""

        # GIVEN no environment variables are set
        with patch.dict("os.environ", {}, clear=True):
            # WHEN creating a vellum client with the given parameters
            client = create_vellum_client(
                api_key="test-api-key",
                api_url=api_url,
                predict_api_url=predict_api_url,
            )

            # THEN the predict URL should be resolved correctly
            assert client._client_wrapper._environment.predict == expected_predict_url

    @pytest.mark.parametrize(
        ["env_vars", "predict_api_url", "expected_predict_url"],
        [
            ({"VELLUM_PREDICT_API_URL": "https://env-predict.example.com"}, None, "https://env-predict.example.com"),
            (
                {"VELLUM_PREDICT_API_URL": "https://env-predict.example.com"},
                "https://param-predict.example.com",
                "https://param-predict.example.com",
            ),
            ({"VELLUM_API_URL": "https://env-api.example.com"}, None, "https://env-api.example.com"),
            (
                {
                    "VELLUM_API_URL": "https://env-api.example.com",
                    "VELLUM_PREDICT_API_URL": "https://env-predict.example.com",
                },
                None,
                "https://env-predict.example.com",
            ),
        ],
        ids=[
            "env_var_predict_api_url_is_used",
            "param_predict_api_url_overrides_env_var",
            "env_var_api_url_fallback_for_predict",
            "env_var_predict_api_url_takes_precedence_over_api_url",
        ],
    )
    def test_create_vellum_client__predict_url_env_var_resolution(
        self, env_vars, predict_api_url, expected_predict_url
    ):
        """Tests that predict_api_url respects environment variables with correct precedence."""

        # GIVEN specific environment variables are set
        with patch.dict("os.environ", env_vars, clear=True):
            # WHEN creating a vellum client with the given parameters
            client = create_vellum_client(
                api_key="test-api-key",
                predict_api_url=predict_api_url,
            )

            # THEN the predict URL should be resolved correctly
            assert client._client_wrapper._environment.predict == expected_predict_url

    def test_create_vellum_environment__predict_api_url_does_not_affect_other_urls(self):
        """Tests that predict_api_url only affects the predict endpoint, not default or documents."""

        # GIVEN no environment variables are set
        with patch.dict("os.environ", {}, clear=True):
            # WHEN creating a vellum environment with a custom predict_api_url
            environment = create_vellum_environment(predict_api_url="https://custom-predict.example.com")

            # THEN the predict URL should be customized
            assert environment.predict == "https://custom-predict.example.com"

            # AND the default and documents URLs should remain unchanged
            assert environment.default == "https://api.vellum.ai"
            assert environment.documents == "https://documents.vellum.ai"

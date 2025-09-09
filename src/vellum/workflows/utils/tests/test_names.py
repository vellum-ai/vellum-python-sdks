import pytest

from vellum.workflows.utils.names import pascal_to_title_case


@pytest.mark.parametrize(
    ["input_str", "expected"],
    [
        ("MyPascalCaseString", "My Pascal Case String"),
        ("AnotherPascalCaseString", "Another Pascal Case String"),
        ("FetchDeploymentScheme", "Fetch Deployment Scheme"),
        ("CheckDeploymentExists", "Check Deployment Exists"),
        ("APINode", "API Node"),
        ("HTTPSConnection", "HTTPS Connection"),
        ("XMLParser", "XML Parser"),
        ("SimpleWord", "Simple Word"),
        ("A", "A"),
        ("AB", "AB"),
        ("ABCDef", "ABC Def"),
    ],
)
def test_pascal_to_title_case(input_str, expected):
    actual = pascal_to_title_case(input_str)
    assert actual == expected

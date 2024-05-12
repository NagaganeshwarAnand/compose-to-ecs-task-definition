import os
import sys
import pytest

if "__file__" in globals():
    current_dir = os.path.dirname(os.path.abspath(__file__))
else:
    current_dir = os.getcwd()
main_dir = os.path.abspath(os.path.join(current_dir, ".."))

sys.path.insert(0, main_dir)

from compose import fetch_compose_file


@pytest.mark.parametrize(
    (
        "file_path",
        "expected_values",
    ),
    [
        # Single test case to validate the fetch_compose_file function
        (
            "assets/compose.yml",
            [
                "nginx",
                "nginx:latest",
                256,
                512,
                [{"containerPort": 80, "protocol": "tcp"}],  # portMappings
                [
                    {"name": "DEBUG", "value": "true"},
                    {"name": "ENV", "value": "production"},
                    {"name": "LOG_LEVEL", "value": "info"},
                ],  # env variables
            ],
        ),
        # fetch from compose file with resource limits
        (
            "assets/compose_with_resource.yml",
            [
                "nginx",
                "nginx:latest",
                512,
                512,
                [{"containerPort": 8080, "protocol": "tcp"}],  # portMappings
                [],  # env variables
            ],
        ),
        # # fetch from compose file without container ports
        (
            "assets/compose_without_container_ports.yml",
            [
                "nginx",
                "nginx:latest",
                256,
                512,
                [],  # portMappings
                [],  # env variables
            ],
        ),
    ],
)
def test_fetch_compose_file(file_path, expected_values):
    fetched_content: dict = fetch_compose_file(file_path)
    assert isinstance(fetched_content, dict)
    assert "services" in fetched_content
    expected_keys = ["name", "image", "cpu", "memory", "portMappings", "environment"]
    # print(fetched_content["services"][0])
    assert all(key in fetched_content["services"][0] for key in expected_keys)
    assert list(fetched_content["services"][0].values()) == expected_values


def test_fetch_compose_file_with_multiple_services():
    fetched_content: dict = fetch_compose_file(
        "assets/compose_with_multiple_services.yml"
    )
    assert isinstance(fetched_content, dict)
    assert "services" in fetched_content
    service_output = {
        "services": [
            {
                "name": "nginx2",
                "image": "nginx:latest",
                "cpu": 256,
                "memory": 512,
                "portMappings": [{"containerPort": 80, "protocol": "tcp"}],
                "environment": [],
            },
            {
                "name": "db",
                "image": "mysql:latest",
                "cpu": 256,
                "memory": 512,
                "portMappings": [{"containerPort": 3306, "protocol": "tcp"}],
                "environment": [],
            },
        ]
    }
    assert fetched_content == service_output

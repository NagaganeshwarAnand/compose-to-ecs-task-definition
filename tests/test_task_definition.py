import json
import os
import sys

if "__file__" in globals():
    current_dir = os.path.dirname(os.path.abspath(__file__))
else:
    current_dir = os.getcwd()
main_dir = os.path.abspath(os.path.join(current_dir, "../src/"))

sys.path.insert(0, main_dir)

from task_definition import template_task_definition


def test_template_task_definition():

    compose_values = {
        "name": "nginx-name",
        "image": "nginx:latest",
        "cpu": 256,
        "memory": 512,
        "portMappings": json.dumps([{"containerPort": 80, "protocol": "tcp"}]),
        "environment": json.dumps(
            [
                {"name": "DEBUG", "value": "true"},
                {"name": "ENV", "value": "production"},
                {"name": "LOG_LEVEL", "value": "info"},
            ]
        ),
    }
    result = template_task_definition(compose_values)

    with open(
        f"{current_dir}/assets/expected_task_definition.txt",
        "r",
    ) as f:
        expected_result = f.read()

    assert result == expected_result

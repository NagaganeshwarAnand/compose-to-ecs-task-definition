import os
import sys
import pytest

if "__file__" in globals():
    current_dir = os.path.dirname(os.path.abspath(__file__))
else:
    current_dir = os.getcwd()
main_dir = os.path.abspath(os.path.join(current_dir, ".."))

sys.path.insert(0, main_dir)

from main import generate_task_definitions


@pytest.mark.parametrize(
    (
        "compose_file_path",
        "task_definitions",
    ),
    [
        (
            "assets/compose.yml",
            ["nginx_task_definition.json"],
        ),
        (
            "assets/compose_with_multiple_services.yml",
            ["nginx2_task_definition.json", "db_task_definition.json"],
        ),
    ],
)
def test_generate_task_definitions(compose_file_path, task_definitions):
    cwd = os.getcwd()
    target_path = os.path.join(cwd, "output")

    result = generate_task_definitions(compose_file_path, target_path)

    assert isinstance(result, list)
    assert len(result) > 0
    task_definition_output_file_paths = [
        os.path.join(cwd, f"output/{defs}") for defs in task_definitions
    ]

    assert set(task_definition_output_file_paths) == set(result)

    for task_definition_output_file_path in task_definition_output_file_paths:
        assert os.path.isfile(task_definition_output_file_path)
        assert os.path.getsize(task_definition_output_file_path) > 0
        assert os.path.basename(task_definition_output_file_path) in os.listdir(
            target_path
        )

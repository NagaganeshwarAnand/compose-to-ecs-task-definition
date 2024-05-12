from string import Template


def template_task_definition(compose_values: dict) -> str:
    with open(
        "/Users/naanand/sandboxes/git_repos/compose-to-ecs-task-definition/src/assets/task_definition.json.template",
        "r",
    ) as f:
        src = Template(f.read())
        result = src.substitute(compose_values)
        return result


def write_task_definition_to_file(
    task_definition: str, target_path: str, service_name: str
) -> str:
    file_path = f"{target_path}/{service_name}_task_definition.json"
    with open(file_path, "w") as f:
        f.write(task_definition)
    return file_path

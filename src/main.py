from typing import List
from compose import fetch_compose_file
from task_definition import template_task_definition, write_task_definition_to_file
import typer


app = typer.Typer()


@app.command()
def help_cmd(name: str):
    print(f"Hello {name}")


@app.command()
def generate_task_definitions(compose_file_path: str, target_path: str) -> List[str]:
    compose_content: dict = fetch_compose_file(compose_file_path)
    task_definition_files: List[str] = []
    for svc in compose_content.get("services", []):
        task_definition = template_task_definition(svc)
        task_definition_files.append(
            write_task_definition_to_file(
                task_definition, target_path, svc.get("name", "service")
            )
        )

    return task_definition_files


if __name__ == "__main__":
    # compose_file_path = "/Users/naanand/sandboxes/git_repos/compose-to-ecs-task-definition/src/assets/compose.yml"
    # target_path = "/Users/naanand/sandboxes/git_repos/compose-to-ecs-task-definition/src/tests/output"
    #
    # result = generate_task_definitions(compose_file_path, target_path)
    # typer.run(generate_task_definitions)
    app()

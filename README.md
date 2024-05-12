# compose-to-ecs-task-definition

## Convert Docker Compose to AWS ECS Task Definitions

This tool automates the conversion of Docker Compose files into ECS task definition JSON files. It's a straightforward utility that saves you from manually translating compose configurations.

### What it does

Parses a Docker Compose file and generates individual ECS task definition files for each service. It extracts:

- Container image and name
- Port mappings (converts `ports` to ECS `portMappings` format)
- Environment variables (restructures for ECS compatibility)
- CPU/memory limits from `deploy.resources.limits`
- Sets up CloudWatch logging (hardcoded to us-east-2)

### Installation

```bash
cd src/ && uv sync
```

### Usage

```bash
uv run main.py generate-task-definitions <compose-file> <output-dir>
```

Example:
```bash
uv run main.py generate-task-definitions assets/compose.yml output
```

Outputs: `{service_name}_task_definition.json` for each service.

### Reality check

This is a basic conversion tool that handles common use cases. For production deployments, you'll likely need to:
- Modify the generated JSON for your specific AWS setup
- Add proper IAM roles and security groups
- Configure networking and service discovery
- Set up proper monitoring and alerting
- Handle secrets management properly

It's a starting point, not a complete solution.
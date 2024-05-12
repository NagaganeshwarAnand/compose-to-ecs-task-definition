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
- **`<compose-file>`**: 
  ```yaml
  version: '3.8'

  services:
    nginx:
      image: nginx:latest
      ports:
        - "80:80"
      environment:
        - DEBUG=true
        - ENV=production
        - LOG_LEVEL=info
    db:
      image: mysql:latest
      ports:
        - "3306:3306"
  ```
- **`<output-dir>`**: Directory to save generated ECS task definition JSON files.
  Outputs: `{service_name}_task_definition.json` for each service.
  - Example: `nginx_task_definition.json`, `db_task_definition.json`
  - **nginx_task_definition.json**:
    ```json
    {
      "requiresCompatibilities": [
        "EC2"
      ],
      "containerDefinitions": [
        {
          "name": "nginx",
          "image": "nginx:latest",
          "memory": 512,
          "cpu": 256,
          "essential": true,
          "portMappings": [{"containerPort": 80, "protocol": "tcp"}],
          "environment": [{"name": "DEBUG", "value": "true"}, {"name": "ENV", "value": "production"}, {"name": "LOG_LEVEL", "value": "info"}],
          "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
              "awslogs-group": "awslogs-nginx-ecs",
              "awslogs-region": "us-east-2",
              "awslogs-stream-prefix": "nginx"
            }
          }
        }
      ],
      "volumes": [],
      "networkMode": "bridge",
      "placementConstraints": [],
      "family": "nginx"
    }
    ```
  - **db_task_definition.json**:
    ```json
    {
      "requiresCompatibilities": [
        "EC2"
      ],
      "containerDefinitions": [
        {
          "name": "db",
          "image": "mysql:latest",
          "memory": 512,
          "cpu": 256,
          "essential": true,
          "portMappings": [{"containerPort": 3306, "protocol": "tcp"}],
          "environment": [],
          "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
              "awslogs-group": "awslogs-db-ecs",
              "awslogs-region": "us-east-2",
              "awslogs-stream-prefix": "db"
            }
          }
        }
      ],
      "volumes": [],
      "networkMode": "bridge",
      "placementConstraints": [],
      "family": "db"
    }
    ```



### Reality check

This is a basic conversion tool that handles common use cases. For production deployments, you'll likely need to:
- Modify the generated JSON for your specific AWS setup
- Add proper IAM roles and security groups
- Configure networking and service discovery
- Set up proper monitoring and alerting
- Handle secrets management properly

It's a starting point, not a complete solution.
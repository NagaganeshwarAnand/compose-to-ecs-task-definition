import yaml


def fetch_compose_file(compose_file: str) -> dict:
    output = {}
    with open(compose_file, "r") as f:
        content = yaml.safe_load(f)
        services = []
        for service_name, service_details in content.get("services", {}).items():
            service_info = {
                "name": service_name,
                "image": service_details.get("image"),
                "cpu": int(
                    float(
                        service_details.get("deploy", {})
                        .get("resources", {})
                        .get("limits", {})
                        .get("cpus", "0.25")
                    )
                    * 1024
                ),
                "memory": int(
                    service_details.get("deploy", {})
                    .get("resources", {})
                    .get("limits", {})
                    .get("memory", "512M")
                    .strip("M")
                ),
                "portMappings": [],
            }
            ports = service_details.get("ports", [])
            service_info["environment"] = [
                {"name": v.split("=")[0], "value": v.split("=")[1]}
                for v in service_details.get("environment", [])
            ]
            # service_info["environment"] = service_details.get("environment", [])
            for port in ports:
                if isinstance(port, int):
                    service_info["portMappings"].append(
                        {"containerPort": port, "protocol": "tcp"}
                    )
                elif isinstance(port, str):
                    parts = port.split(":")
                    container_port = int(parts[-1])
                    service_info["portMappings"].append(
                        {"containerPort": container_port, "protocol": "tcp"}
                    )
            services.append(service_info)
        output["services"] = services
    return output

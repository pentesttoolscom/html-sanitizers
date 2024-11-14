import os
from dataclasses import dataclass, field
import docker
from jinja2 import Environment, FileSystemLoader
import click


@dataclass
class Backend:
    """A Backend represent a language for which we want to test an HTML sanitizer."""
    image: str
    """Name of the underlying Docker image"""
    slug: str
    """The path on which the backend server handles requests on the reverse Proxy.
    Example: for a slug `python`, we would send requests to `http://localhost/python`.
    """
    routes: list[str] = field(default_factory=list)
    """The routes this backend exposes."""

def build_backends() -> list[Backend]:
    """Builds a docker image for each backend server under ./docker/backends."""
    client = None
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        click.secho(f"Failed to start docker client. Is docker running?", fg='red')
        return []
    built_backends: list[Backend] = []
    with click.progressbar(os.listdir("./docker/backends")) as bar:
        for backend_dir in bar:
            click.secho(f"\nBuilding image for {backend_dir}!")
            name = f"html-sanitizer-{backend_dir}"
            try:
                client.images.build(path=f"./docker/backends/{backend_dir}", tag=name)
            except (docker.errors.BuildError, docker.errors.APIError) as exc:
                click.secho(f"Failed to build image {name}. Exception:\n{exc}", fg='red')
            else:
                backend = Backend(image=name, slug=backend_dir)
                try:
                    with open(f"./docker/backends/{backend_dir}/routes.txt") as f:
                        backend.routes.extend(f.readlines())
                except FileNotFoundError:
                    pass
                built_backends.append(backend)
    return built_backends

def build_nginx_image(backends: list[Backend], port: int) -> str:
    """Builds a Docker image for an nginx reverse proxy which forwards connections to the given backends.

    Args:
    - port: the port on which the Nginx reverse proxy will listen

    Returns:
    The name of the built docker image.
    """
    jinja_env = Environment(loader=FileSystemLoader("templates"))
    compose_file_template = jinja_env.get_template("nginx.conf.jinja")
    with open("docker/nginx/nginx.conf", "w") as f:
        f.write(compose_file_template.render(nginx_port=port, servers=[
            backend.slug for backend in backends
        ]))
    client = docker.from_env()
    click.secho(f"\nBuilding image for nginx!")
    tag = "html-sanitizer-nginx"
    client.images.build(path="./docker/nginx", tag=tag)
    click.secho("Succes!", fg="green")
    return tag

def generate_compose_file(backend_images, nginx_image, nginx_port):
    """Writes the Compose file for the infrastructure under the current working directory."""
    jinja_env = Environment(loader=FileSystemLoader("templates"))
    compose_file_template = jinja_env.get_template("docker-compose.yaml.jinja")
    with open("docker-compose.yaml", "w") as f:
        contents = compose_file_template.render(nginx_image=nginx_image, nginx_port=nginx_port, backend_services=backend_images)
        f.write(contents)

def main():
    nginx_port = 9090
    backends = build_backends()
    nginx_image_tag = build_nginx_image(backends, nginx_port)
    if not nginx_image_tag:
        return
    generate_compose_file(backends, nginx_image_tag, nginx_port)
    click.secho("Build finished successfully", fg='green')
    exposed_routes = "\n- ".join(
        f"http://localhost:{nginx_port}/{backend.slug}{route}" for backend in backends for route in backend.routes if backend.routes
    )
    click.secho(f"Backends will expose the following routes:\n- {exposed_routes}")
    click.secho("Run docker compose up -d")

if __name__ == "__main__":
    main()

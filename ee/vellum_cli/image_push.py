import json
import logging
import re
import subprocess
from typing import List, Optional

import docker
from docker import DockerClient
from dotenv import load_dotenv

from vellum.workflows.vellum_client import create_vellum_client, create_vellum_environment
from vellum_cli.logger import load_cli_logger

_SUPPORTED_ARCHITECTURE = "amd64"


def image_push_command(image: str, tags: Optional[List[str]] = None) -> None:
    load_dotenv()
    logger = load_cli_logger()
    vellum_client = create_vellum_client()

    # Check if we are self hosted by looking at our base url
    api_url = create_vellum_environment().default
    is_self_hosted = not api_url.endswith("vellum.ai") and "localhost:" not in api_url and "127.0.0.1" not in api_url
    if is_self_hosted:
        logger.info("Self hosted install detected...")

    if is_self_hosted and "/" not in image:
        logger.error(
            "For adding images to your self hosted install you must include the "
            "repository address in the provided image name. You must also have "
            "already pushed the image to the docker repository that your self "
            "hosted install is using."
        )
        exit(1)

    # We're using docker python SDK here instead of subprocess since it connects to the docker host directly
    # instead of using the command line so it seemed like it would possibly be a little more robust since
    # it might avoid peoples' wonky paths, unfortunately it doesn't support the manifest command which we need for
    # listing all of the architectures of the image instead of just the one that matches the machine. We can fall back
    # to using normal inspect which returns the machine image for this case though. And in the future we could figure
    # out how to call the docker host directly to do this.
    logger.info("Pre-validating image...")
    docker_client = docker.from_env()
    check_architecture(docker_client, image, logger)

    repo_split = image.split("/")
    tag_split = repo_split[-1].split(":")
    image_name = tag_split[0]
    main_tag = tag_split[1] if len(tag_split) > 1 else "latest"
    all_tags = [main_tag, *(tags or [])]

    if is_self_hosted:
        # Include the repo for self hosted since we skip pushing it to our internal repo and expect
        # the user the push it themselves and provide us with the repo name.
        image_name = image.split(":")[0]

        logger.info("Checking if image already exists in repository...")
        exists_result = subprocess.run(
            ["docker", "manifest", "inspect", image],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if exists_result.returncode != 0:
            logger.error(
                "Image does not exist in repository. Push the image to the "
                "repository your self hosted install is using and try again."
            )
            exit(1)
    else:
        logger.info("Authenticating...")
        auth = vellum_client.container_images.docker_service_token()

        docker_client.login(
            username="oauth2accesstoken",
            password=auth.access_token,
            registry=auth.repository,
        )

        for tag in all_tags:
            vellum_image_name = f"{auth.repository}/{image_name}:{tag}"

            docker_client.api.tag(image, vellum_image_name)

            push_result = docker_client.images.push(repository=vellum_image_name, stream=True)

            # Here were trying to mime the output you would get from a normal docker push, which
            # the python sdk makes as hard as possible.
            for raw_line in push_result:
                try:
                    for sub_line in raw_line.decode("utf-8").split("\r\n"):
                        line = json.loads(sub_line)
                        error_message = line.get("errorDetail", {}).get("message")
                        status = line.get("status")
                        id = line.get("id", "")

                        if error_message:
                            logger.error(error_message)
                            exit(1)
                        elif status == "Waiting":
                            continue
                        elif status:
                            logger.info(f"{id}{': ' if id else ''}{status}")
                        else:
                            logger.info(line)
                except Exception:
                    continue

    inspect_result = subprocess.run(
        ["docker", "inspect", "--format='{{index .RepoDigests 0}}'", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    sha = ""
    if inspect_result.returncode == 0:
        match = re.search(r"sha256[^']*", inspect_result.stdout.decode("utf-8"))
        if match and match.group(0):
            sha = match.group(0)

    if not sha:
        # Fallback to using docker client if command line fails, at least on some systems
        # this appears to give a bad sha.
        logger.warning(
            "Could not determine image hash with command line docker falling back to python docker client..."
        )

        image_details = docker_client.api.inspect_image(image)
        sha = image_details["Id"]

    logger.info(f"Updating Vellum metadata and validating image works in our system with image digest: {sha}...")

    vellum_client.container_images.push_container_image(
        name=image_name,
        sha=sha,
        tags=all_tags,
    )
    logger.info(f"Image successfully pushed as {image_name} to vellum with tags: {all_tags}.")


def check_architecture(docker_client: DockerClient, image: str, logger: logging.Logger) -> None:
    result = subprocess.run(
        ["docker", "manifest", "inspect", image],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    manifest_parse_failed = False
    architectures = []
    try:
        manifest = json.loads(result.stdout)
        architectures = [manifest_item["platform"]["architecture"] for manifest_item in manifest["manifests"]]
    except Exception:
        logger.debug("Error parsing manifest response")
        manifest_parse_failed = True

    # Fall back to inspect image if we errored out using docker command line
    if result.returncode != 0 or manifest_parse_failed:
        logger.debug(f"Error inspecting manifest: {result.stderr.decode('utf-8').strip()}")
        image_details = docker_client.api.inspect_image(image)

        if image_details["Architecture"] != _SUPPORTED_ARCHITECTURE:
            logger.error(f"Image must be built for {_SUPPORTED_ARCHITECTURE} architecture.")
            exit(1)
    else:
        if _SUPPORTED_ARCHITECTURE not in architectures:
            logger.error(f"Image must be built for {_SUPPORTED_ARCHITECTURE} architecture.")
            exit(1)

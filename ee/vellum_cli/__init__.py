from typing import List, Optional

import click

from vellum_cli.aliased_group import ClickAliasedGroup
from vellum_cli.image_push import image_push_command
from vellum_cli.pull import pull_command
from vellum_cli.push import push_command


@click.group(cls=ClickAliasedGroup)
def main() -> None:
    """Vellum SDK CLI"""
    pass


class PushGroup(ClickAliasedGroup):
    def get_command(self, ctx, cmd_name):
        # First try to get the command normally
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # If no command found, call our catch-all
        return push_module


@main.group(invoke_without_command=True, cls=PushGroup)
@click.pass_context
def push(
    ctx: click.Context,
) -> None:
    """Push Resources to Vellum"""

    if ctx.invoked_subcommand is None:
        push_command()


@main.group()
def workflows():
    """Operations related to Vellum Workflows"""
    pass


@workflows.command(name="push")
@click.argument("module", required=False)
@click.option("--deploy", is_flag=True, help="Deploy the Workflow after pushing it to Vellum")
@click.option("--deployment-label", type=str, help="Label to use for the Deployment")
@click.option("--deployment-name", type=str, help="Unique name for the Deployment")
@click.option("--deployment-description", type=str, help="Description for the Deployment")
@click.option("--release-tag", type=list, help="Release Tag for the Deployment", multiple=True)
def workflows_push(
    module: Optional[str],
    deploy: Optional[bool],
    deployment_label: Optional[str],
    deployment_name: Optional[str],
    deployment_description: Optional[str],
    release_tag: Optional[List[str]],
) -> None:
    """
    Push Workflows to Vellum. If a module is provided, only the Workflow for that module will be pushed.
    If no module is provided, the first configured Workflow will be pushed.
    """

    push_command(
        module=module,
        deploy=deploy,
        deployment_label=deployment_label,
        deployment_name=deployment_name,
        deployment_description=deployment_description,
        release_tags=release_tag,
    )


@push.command(name="*", hidden=True)
@click.pass_context
@click.option("--deploy", is_flag=True, help="Deploy the Resource after pushing it to Vellum")
@click.option("--deployment-label", type=str, help="Label to use for the Deployment")
@click.option("--deployment-name", type=str, help="Unique name for the Deployment")
@click.option("--deployment-description", type=str, help="Description for the Deployment")
@click.option("--release-tag", type=list, help="Release Tag for the Deployment", multiple=True)
def push_module(
    ctx: click.Context,
    deploy: Optional[bool],
    deployment_label: Optional[str],
    deployment_name: Optional[str],
    deployment_description: Optional[str],
    release_tag: Optional[List[str]],
) -> None:
    """Push a specific module to Vellum"""

    if ctx.parent:
        push_command(
            module=ctx.parent.invoked_subcommand,
            deploy=deploy,
            deployment_label=deployment_label,
            deployment_name=deployment_name,
            deployment_description=deployment_description,
            release_tags=release_tag,
        )


class PullGroup(ClickAliasedGroup):
    def get_command(self, ctx, cmd_name):
        # First try to get the command normally
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # If no command found, call our catch-all
        return pull_module


@main.group(invoke_without_command=True, cls=PullGroup)
@click.pass_context
@click.option(
    "--include-json",
    is_flag=True,
    help="""Include the JSON representation of each Resource in the pull response. \
Should only be used for debugging purposes.""",
)
@click.option(
    "--exclude-code",
    is_flag=True,
    help="""Exclude the code definition of each Resource from the pull response. \
Should only be used for debugging purposes.""",
)
@click.option(
    "--strict",
    is_flag=True,
    help="""Raises an error immediately if there are any issues with the pulling of the Resource.""",
)
@click.option(
    "--include-sandbox",
    is_flag=True,
    help="""Generates a runnable sandbox.py file containing test data from the Resource's sandbox. \
Helpful for running and debugging workflows locally.""",
)
def pull(
    ctx: click.Context,
    include_json: Optional[bool],
    exclude_code: Optional[bool],
    strict: Optional[bool],
    include_sandbox: Optional[bool],
) -> None:
    """Pull Resources from Vellum"""

    if ctx.invoked_subcommand is None:
        pull_command(
            include_json=include_json,
            exclude_code=exclude_code,
            strict=strict,
            include_sandbox=include_sandbox,
        )


@workflows.command(name="pull")
@click.argument("module", required=False)
@click.option(
    "--include-json",
    is_flag=True,
    help="""Include the JSON representation of the Workflow in the pull response. \
Should only be used for debugging purposes.""",
)
@click.option("--workflow-sandbox-id", type=str, help="Pull the Workflow from a specific Sandbox ID")
@click.option(
    "--workflow-deployment",
    type=str,
    help="""Pull the Workflow from a specific Deployment. Can use the name or the ID of the Deployment.""",
)
@click.option(
    "--exclude-code",
    is_flag=True,
    help="""Exclude the code definition of the Workflow from the pull response. \
Should only be used for debugging purposes.""",
)
@click.option(
    "--strict",
    is_flag=True,
    help="""Raises an error immediately if there are any issues with the pulling of the Workflow.""",
)
@click.option(
    "--include-sandbox",
    is_flag=True,
    help="""Generates a runnable sandbox.py file containing test data from the Resource's sandbox. \
Helpful for running and debugging workflows locally.""",
)
def workflows_pull(
    module: Optional[str],
    include_json: Optional[bool],
    workflow_sandbox_id: Optional[str],
    workflow_deployment: Optional[str],
    exclude_code: Optional[bool],
    strict: Optional[bool],
    include_sandbox: Optional[bool],
) -> None:
    """
    Pull Workflows from Vellum. If a module is provided, only the Workflow for that module will be pulled.
    If no module is provided, the first configured Workflow will be pulled.
    """

    pull_command(
        module=module,
        include_json=include_json,
        workflow_sandbox_id=workflow_sandbox_id,
        workflow_deployment=workflow_deployment,
        exclude_code=exclude_code,
        strict=strict,
        include_sandbox=include_sandbox,
    )


@pull.command(name="*")
@click.pass_context
@click.option(
    "--include-json",
    is_flag=True,
    help="""Include the JSON representation of the Resource in the pull response. \
Should only be used for debugging purposes.""",
)
@click.option(
    "--exclude-code",
    is_flag=True,
    help="""Exclude the code definition of the Resource from the pull response. \
Should only be used for debugging purposes.""",
)
@click.option(
    "--strict",
    is_flag=True,
    help="""Raises an error immediately if there are any issues with the pulling of the Resource.""",
)
@click.option(
    "--include-sandbox",
    is_flag=True,
    help="""Generates a runnable sandbox.py file containing test data from the Resource's sandbox. \
Helpful for running and debugging resources locally.""",
)
def pull_module(
    ctx: click.Context,
    include_json: Optional[bool],
    exclude_code: Optional[bool],
    strict: Optional[bool],
    include_sandbox: Optional[bool],
) -> None:
    """Pull a specific module from Vellum"""

    if ctx.parent:
        pull_command(
            module=ctx.parent.invoked_subcommand,
            include_json=include_json,
            exclude_code=exclude_code,
            strict=strict,
            include_sandbox=include_sandbox,
        )


@main.group(aliases=["images", "image"])
def images() -> None:
    """Vellum Docker Images"""
    pass


@images.command(name="push")
@click.argument("image", required=True)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    help="Tags the provided image inside of Vellum's repo. "
    "This field does not push multiple local tags of the passed in image.",
)
def image_push(image: str, tag: Optional[List[str]] = None) -> None:
    """Push Docker image to Vellum"""
    image_push_command(image, tag)


if __name__ == "__main__":
    main()

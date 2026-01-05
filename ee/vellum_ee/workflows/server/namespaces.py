"""Namespace utilities for workflow server."""

import random
import string


def get_random_namespace() -> str:
    """
    Generate a random namespace for virtual file loading.

    This generates a workflow_tmp_* namespace like vembda uses for loading
    workflows dynamically.

    Returns:
        A random namespace string in the format "workflow_tmp_{random_suffix}"
    """
    random_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    return f"workflow_tmp_{random_suffix}"

import ast
import logging
import re
from typing import Union
from typing_extensions import TypeGuard

import black
import isort


def merge_python_files(original_file_map: dict[str, str], generated_file_map: dict[str, str]) -> dict[str, str]:
    merged_file_map: dict[str, str] = {}

    for generated_file_name, generated_file_contents in generated_file_map.items():
        original_file_contents = original_file_map.get(generated_file_name)

        if original_file_contents:
            merged_file_map[generated_file_name] = merge_python_file(
                original_file_contents, generated_file_contents, generated_file_name
            )
        else:
            merged_file_map[generated_file_name] = generated_file_contents

    return merged_file_map


def merge_python_file(original_file_contents: str, generated_file_contents: str, file_name: str) -> str:
    merged_ast = ast.parse(original_file_contents)
    try:
        generated_ast = ast.parse(generated_file_contents)
    except Exception:
        return original_file_contents

    # Get the class node from the generated file
    generated_class_nodes = [node for node in generated_ast.body if isinstance(node, ast.ClassDef)]

    # Ignore empty files
    if len(generated_class_nodes) == 0:
        return generated_file_contents
    elif len(generated_class_nodes) > 1:
        raise ValueError(f"On {file_name}, expected 1 class node, got {len(generated_class_nodes)}")
    generated_class_node = generated_class_nodes[0]

    # Get the class node from the original file with the same name
    matching_class_nodes = [
        node for node in merged_ast.body if isinstance(node, ast.ClassDef) and node.name == generated_class_node.name
    ]
    if len(matching_class_nodes) != 1:
        raise ValueError(f"On {file_name}, expected 1 class node, got {len(matching_class_nodes)}")
    merged_class_node = matching_class_nodes[0]

    if merged_class_node.body and isinstance(merged_class_node.body[0], ast.Expr):
        first_constant = merged_class_node.body[0].value
        if isinstance(first_constant, ast.Constant) and isinstance(first_constant.value, str):
            # Delete the first docstring, since that's controlled by the UI and will be
            # controlled by the generated class node
            merged_class_node.body = merged_class_node.body[1:]

    # Delete the class attributes from the original class node that don't start with an underscore
    merged_class_node.body = [node for node in merged_class_node.body if not _is_public_assignment(node)]

    # Add the nodes from the generated class node to the original class node, overwriting existing attributes
    stmts_to_insert: list[Union[ast.Assign, ast.AnnAssign, ast.Expr]] = []

    for prev_generated_node, generated_node in zip([None, *generated_class_node.body], generated_class_node.body):
        if isinstance(generated_node, ast.Assign):
            stmts_to_insert.append(generated_node)
            continue
        if isinstance(generated_node, ast.AnnAssign):
            stmts_to_insert.append(generated_node)
            continue
        if isinstance(generated_node, ast.Expr):
            # It's still unclear to me how `ast` preserves the fact that hii
            stmts_to_insert.append(generated_node)
            continue
        if isinstance(generated_node, ast.Pass):
            continue

        for merged_node in merged_class_node.body:
            if _is_stmt_def(merged_node) and _is_stmt_def(generated_node) and merged_node.name == generated_node.name:
                merged_node.body = generated_node.body
                break

        else:
            if prev_generated_node is None:
                merged_class_node.body.insert(0, generated_node)
            else:
                if not hasattr(prev_generated_node, "name"):
                    prev_index = -1
                else:
                    prev_index = next(
                        (
                            i
                            for i, node in enumerate(merged_class_node.body)
                            if hasattr(node, "name") and node.name == prev_generated_node.name
                        ),
                        len(merged_class_node.body) - 1,
                    )
                merged_class_node.body.insert(prev_index + 1, generated_node)

    for stmt in reversed(stmts_to_insert):
        merged_class_node.body.insert(0, stmt)

    # Add imports from the generated file to the original file
    for node in generated_ast.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            merged_ast.body.insert(0, node)

    merged_code = ast.unparse(merged_ast)

    # Sort and deduplicate imports
    merged_code = isort.code(merged_code)

    try:
        merged_code = black.format_str(merged_code, mode=black.Mode())
    except black.parsing.InvalidInput:
        logging.exception("Black formatting failed for file: %s", file_name)

    # Remove empty lines after class and function definitions
    merged_code = re.sub(r":\n{2,}(\s+)", r":\n\1", merged_code)

    return merged_code


def _is_public_assignment(stmt: ast.stmt) -> bool:
    if isinstance(stmt, ast.Assign):
        for target_expr in stmt.targets:
            if isinstance(target_expr, ast.Name):
                return not target_expr.id.startswith("_")
        return True

    if isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name):
            return not stmt.target.id.startswith("_")
        return True

    return False


def _is_stmt_def(stmt: ast.stmt) -> TypeGuard[Union[ast.AsyncFunctionDef, ast.ClassDef, ast.FunctionDef]]:
    return isinstance(
        stmt,
        (
            ast.AsyncFunctionDef,
            ast.ClassDef,
            ast.FunctionDef,
        ),
    )

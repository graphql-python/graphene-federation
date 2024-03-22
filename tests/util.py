import inspect
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from graphql import graphql_sync


def file_handlers(
    path: Path,
) -> tuple[Callable[[Any, str], None], Callable[[str], str]]:
    curr_dir = path.parent
    file_name = path.name.replace(".py", "")

    try:
        os.mkdir(f"{curr_dir}/gql/{file_name}")
    except FileExistsError:
        pass

    def save_file(data, extra_path: str = ""):
        function_name = inspect.stack()[1].function
        with open(
            f"{curr_dir}/gql/{file_name}/{function_name}_{extra_path}.graphql", "w"
        ) as f:
            f.write(str(data))

    def open_file(extra_path: str = ""):
        function_name = inspect.stack()[1].function
        with open(
            f"{curr_dir}/gql/{file_name}/{function_name}_{extra_path}.graphql", "r"
        ) as f:
            return f.read()

    return save_file, open_file


def sdl_query(schema) -> str:
    query = "query { _service { sdl } }"
    result = graphql_sync(schema.graphql_schema, query)
    assert not result.errors
    return result.data["_service"]["sdl"]

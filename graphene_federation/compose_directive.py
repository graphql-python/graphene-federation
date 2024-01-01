from typing import Optional

from graphql import GraphQLDirective


def is_composable(directive: GraphQLDirective) -> bool:
    """
    Checks if the directive will be composed to supergraph.
    Validates the presence of _compose_import_url attribute
    """
    return hasattr(directive, "_compose_import_url")


def mark_composable(
    directive: GraphQLDirective, import_url: str, import_as: Optional[str] = None
) -> GraphQLDirective:
    """
    Marks directive with _compose_import_url and _compose_import_as
    Enables Identification of directives which are to be composed to supergraph
    """
    setattr(directive, "_compose_import_url", import_url)
    if import_as:
        setattr(directive, "_compose_import_as", import_as)
    return directive


def compose_directive_schema_extensions(directives: list[GraphQLDirective]):
    """
    Generates schema extends string for ComposeDirective
    """
    link_schema = ""
    compose_directive_schema = ""
    # Using dictionary to generate cleaner schema when multiple directives imports from same URL.
    links: dict = {}

    for directive in directives:
        # TODO: Replace with walrus operator when dropping Python 3.8 support
        if hasattr(directive, "_compose_import_url"):
            compose_import_url = getattr(directive, "_compose_import_url")
            if hasattr(directive, "_compose_import_as"):
                compose_import_as = getattr(directive, "_compose_import_as")
                import_value = (
                    f'{{ name: "@{directive.name}, as: "@{compose_import_as}" }}'
                )
                imported_name = compose_import_as
            else:
                import_value = f'"@{directive.name}"'
                imported_name = directive.name

            import_url = compose_import_url

            if links.get(import_url):
                links[import_url] = links[import_url].append(import_value)
            else:
                links[import_url] = [import_value]

            compose_directive_schema += (
                f' @composeDirective(name: "@{imported_name}")\n'
            )

    for import_url in links:
        link_schema += f' @link(url: "{import_url}", import: [{",".join(value for value in links[import_url])}])\n'

    return link_schema + compose_directive_schema

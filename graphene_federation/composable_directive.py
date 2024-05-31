from typing import Any, Callable, Collection, Dict, Optional

from graphene_directives import CustomDirective, DirectiveLocation, directive_decorator
from graphql import (
    DirectiveDefinitionNode,
    GraphQLArgument,
    GraphQLDirective,
)


class ComposableDirective(GraphQLDirective):
    def __init__(
        self,
        name: str,
        locations: Collection[DirectiveLocation],
        args: Optional[Dict[str, GraphQLArgument]] = None,
        is_repeatable: bool = False,
        description: Optional[str] = None,
        extensions: Optional[Dict[str, Any]] = None,
        ast_node: Optional[DirectiveDefinitionNode] = None,
        spec_url: str = None,
        add_to_schema_directives: bool = True,
    ) -> None:
        """
        Creates a Federation Supported GraphQLDirective

        :param name: (GraphQLDirective param)
        :param args: (GraphQLDirective param)
        :param is_repeatable: (GraphQLDirective param)
        :param description: (GraphQLDirective param)
        :param extensions: (GraphQLDirective param)
        :param ast_node: (GraphQLDirective param)

        :param spec_url: url of the directive to be set in url of @link
        :param add_to_schema_directives: Adds schema_directives @composeDirective and @link to schema automatically
        """
        if add_to_schema_directives:
            assert spec_url is not None, "ComposableDirective requires spec_url"

        self.spec_url = spec_url
        self.add_to_schema_directives = add_to_schema_directives

        self.graphene_directive = CustomDirective(
            name=name,
            locations=locations,
            args=args,
            is_repeatable=is_repeatable,
            description=description,
            extensions=extensions,
            ast_node=ast_node,
        )
        parent_attributes = {
            "name",
            "locations",
            "args",
            "is_repeatable",
            "description",
            "extensions",
            "ast_node",
        }
        parent_kwargs = {}

        # Copy attributes of graphene_directive
        for k, v in self.graphene_directive.__dict__.items():
            if k not in parent_attributes:
                setattr(self, k, v)
            else:
                parent_kwargs[k] = v

        super().__init__(**parent_kwargs)

    def decorator(self) -> Callable:
        return directive_decorator(self.graphene_directive)

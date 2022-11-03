from dataclasses import dataclass
from typing import Any, Optional, Type

from dbt.adapters.base.relation import BaseRelation, Self
from dbt.contracts.graph.parsed import ParsedSourceDefinition


@dataclass(frozen=True, eq=False, repr=False)
class DuckDBRelation(BaseRelation):
    external_location: Optional[str] = None

    @classmethod
    def create_from_source(
        cls: Type[Self], source: ParsedSourceDefinition, **kwargs: Any
    ) -> Self:

        # Some special handling here to allow sources that are external files to be specified
        # via a `external_location` meta field. If the source's meta field is used, we include
        # some logic to allow basic templating of the external location based on the individual
        # name or identifier for the table itself to cut down on boilerplate.
        ext_location = None
        if "external_location" in source.meta:
            ext_location = source.meta["external_location"]
        elif "external_location" in source.source_meta:
            # Use str.format here to allow for some basic templating outside of Jinja
            ext_location = source.source_meta["external_location"].format(
                name=source.name,
                identifier=source.identifier,
            )
        if ext_location:
            # If it's a function call or already has single quotes, don't add them
            if "(" not in ext_location and not ext_location.startswith("'"):
                ext_location = f"'{ext_location}'"
            kwargs["external_location"] = ext_location

        return super().create_from_source(source, **kwargs)  # type: ignore

    def render(self) -> str:
        if self.external_location:
            return self.external_location
        else:
            return super().render()

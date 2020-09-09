from typing import Dict, Tuple, Any, Optional
from pydantic.fields import FieldInfo

# Do NOT import from uvicore.support.pydantic.fields as it doesn't exist

class Field(FieldInfo):

    def __init__(self, column: str = None, *,
        primary: Optional[bool] = False,
        title: Optional[str] = None,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        required: bool = False,
        sortable: bool = False,
        searchable: bool = False,
        read_only: Optional[bool] = None,
        write_only: Optional[bool] = None,
        callback: Optional[Any] = None,
        has_one: Optional[Tuple] = None,
        properties: Optional[Dict] = None,
    ):
        self.column = column
        self.primary = primary
        self.title = title
        self.description = description
        self.default = default
        self.required = required
        self.sortable = sortable
        self.searchable = searchable
        self.read_only = read_only
        self.write_only = write_only
        self.callback = callback
        self.has_one = has_one
        self.properties = properties
        super().__init__(
            default=default,
            column=column,
            primary=primary,
            title=title,
            description=description,
            required=required,
            sortable=sortable,
            searchable=searchable,
            readOnly=read_only,
            writeOnly=write_only,
            callback=callback,
            has_one=has_one,
            properties=properties,
        )

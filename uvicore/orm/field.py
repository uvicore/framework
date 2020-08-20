from typing import Dict, Any, Optional
from pydantic.fields import FieldInfo


class Field(FieldInfo):

    def __init__(self, column: str = None, *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        required: bool = False,
        sortable: bool = False,
        searchable: bool = False,
        read_only: Optional[bool] = None,
        write_only: Optional[bool] = None,
        callback: Optional[Any] = None,
        properties: Optional[Dict] = None,
    ):
        self.column: str = column
        self.title: str = title
        self.description: str = description
        self.default: Any = default
        self.required: bool = required
        self.sortable: bool = sortable
        self.searchable: bool = searchable
        self.read_only: Optional[bool] = read_only
        self.write_only: Optional[bool] = write_only
        self.callback: Any = callback
        self.properties: Optional[Dict] = properties
        super().__init__(
            default=default,
            column=column,
            title=title,
            description=description,
            required=required,
            sortable=sortable,
            searchable=searchable,
            readOnly=read_only,
            writeOnly=write_only,
            callback=callback,
            properties=properties,
        )

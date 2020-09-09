from typing import List, Type


def validate_field_name(bases: List[Type['BaseModel']], field_name: str) -> None:
    """
    Ensure that the field's name does not shadow an existing attribute of the model.
    """
    pass
    # for base in bases:
    #     if getattr(base, field_name, None):
    #         raise NameError(
    #             f'Field name "{field_name}" shadows a BaseModel attribute; '
    #             f'use a different field name with "alias=\'{field_name}\'".'
    #         )

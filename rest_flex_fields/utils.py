from collections.abc import Iterable

from rest_flex_fields import EXPAND_PARAM, FIELDS_PARAM, OMIT_PARAM, WILDCARD_VALUES


def is_expanded(request, field: str) -> bool:
    """ Examines request object to return boolean of whether
        passed field is expanded.
    """
    expand_value = request.query_params.get(EXPAND_PARAM)
    expand_fields = []

    # first split on commas to get each expand
    for full in expand_value.split(","):
        # than split on dots to get each component that is expanded
        parts = full.split(".")
        for i in range(len(parts)):
            # add each prefix, as each prefix is epxanded, ie
            # a.b.c will add a, a.b and a.b.c to the expand_fields list
            # we do this to differentiate a.b from b
            expand_fields.append(".".join(parts[: i + 1]))

    # WILDCARD_VALUES only expands top level fields
    if "." not in field and any(field for field in expand_fields if field in WILDCARD_VALUES):
        return True

    return field in expand_fields


def is_included(request, field: str) -> bool:
    """ Examines request object to return boolean of whether
        passed field has been excluded, either because `fields` is
        set, and it is not among them, or because `omit` is set and
        it is among them.
    """
    sparse_value = request.query_params.get(FIELDS_PARAM)
    omit_value = request.query_params.get(OMIT_PARAM)
    sparse_fields, omit_fields = [], []

    if sparse_value:
        for f in sparse_value.split(","):
            sparse_fields.extend([_ for _ in f.split(".")])

    if omit_value:
        for f in omit_value.split(","):
            omit_fields.extend([_ for _ in f.split(".")])

    if len(sparse_fields) > 0 and field not in sparse_fields:
        return False

    if len(omit_fields) > 0 and field in omit_fields:
        return False

    return True


def split_levels(fields):
    """
        Convert dot-notation such as ['a', 'a.b', 'a.d', 'c'] into
        current-level fields ['a', 'c'] and next-level fields
        {'a': ['b', 'd']}.
    """
    first_level_fields = []
    next_level_fields = {}

    if not fields:
        return first_level_fields, next_level_fields

    assert isinstance(
        fields, Iterable
    ), "`fields` must be iterable (e.g. list, tuple, or generator)"

    if isinstance(fields, str):
        fields = [a.strip() for a in fields.split(",") if a.strip()]
    for e in fields:
        if "." in e:
            first_level, next_level = e.split(".", 1)
            first_level_fields.append(first_level)
            next_level_fields.setdefault(first_level, []).append(next_level)
        else:
            first_level_fields.append(e)

    first_level_fields = list(set(first_level_fields))
    return first_level_fields, next_level_fields

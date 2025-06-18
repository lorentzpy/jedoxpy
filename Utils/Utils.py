def format_id_string(ids: list) -> str:
    return ",".join(
        str(x) if not isinstance(x, list) else ":".join(map(str, x))
        for x in ids
    )
import databases


def get_db(_info) -> databases.Database:
    return _info.context['db']

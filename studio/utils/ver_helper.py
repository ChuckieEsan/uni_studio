from studio import r
def get_ver():
    return bytes.decode(r.get('studio_version'),encoding='utf-8')
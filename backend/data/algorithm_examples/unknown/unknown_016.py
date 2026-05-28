def build_url_16(base, params):
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    return base + '?' + query if query else base

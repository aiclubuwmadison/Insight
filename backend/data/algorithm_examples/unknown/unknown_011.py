def parse_config_11(lines):
    config = {}
    for line in lines:
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        config[key.strip()] = value.strip()
    return config

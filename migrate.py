from yaml import dump, safe_load, YAMLError


def move_config_center(config):
    if 'apisix' in config:
        apisix = config['apisix']
        if 'config_center' in apisix:
            create_deployment_if_needed(config)
            config['deployment']['config_provider'] = apisix['config_center']
            del apisix['config_center']


def move_etcd(config):
    if 'etcd' in config:
        create_deployment_if_needed(config)
        config['deployment']['etcd'] = config['etcd']
        del config['etcd']


def move_admin_keys(config):
    def move_admin_key(key, apisix, config):
        if key in apisix:
            create_admin_if_needed(config)
            config['deployment']['admin'][key] = apisix[key]
            del apisix[key]

    if 'apisix' in config:
        apisix = config['apisix']
        move_admin_key('admin_key', apisix, config)
        move_admin_key('enable_admin_cors', apisix, config)
        move_admin_key('allow_admin', apisix, config)
        move_admin_key('admin_listen', apisix, config)
        move_admin_key('https_admin', apisix, config)
        move_admin_key('admin_api_mtls', apisix, config)
        move_admin_key('admin_api_version', apisix, config)


def move_ssl(config):
    if 'apisix' in config:
        apisix = config['apisix']
        if 'ssl' in apisix:
            ssl = apisix['ssl']
            listen = {}
            if 'port' in ssl:
                listen['port'] = ssl['port']
                del ssl['port']
            if 'enable_http2' in ssl:
                listen['enable_http2'] = ssl['enable_http2']
                del ssl['enable_http2']
            if 'listen' not in ssl:
                ssl['listen'] = []
            ssl['listen'].append(listen)


def move_shared_dicts(config):
    if 'nginx_config' in config and 'http' in config['nginx_config']:
        if 'lua_shared_dicts' in config['nginx_config']['http']:
            config['nginx_config']['http']['custom_lua_shared_dict'] = config['nginx_config']['http'][
                'lua_shared_dicts']
            del config['nginx_config']['http']['lua_shared_dicts']


def move_healthcheck_retries(config):
    if 'deployment' in config and 'etcd' in config['deployment']:
        if 'health_check_retry' in config['deployment']['etcd']:
            config['deployment']['etcd']['startup_retry'] = config['deployment']['etcd']['health_check_retry']
            del config['deployment']['etcd']['health_check_retry']


def move_port_admin(config):
    if 'apisix' in config and 'port_admin' in config['apisix']:
        create_deployment_if_needed(config)
        deployment = config['deployment']
        if 'apisix' not in deployment:
            deployment['apisix'] = {}
            apisix = deployment['apisix']
            if 'admin_listen' not in apisix:
                apisix['admin_listen'] = {}
                admin_listen = apisix['admin_listen']
                admin_listen['port'] = config['apisix']['port_admin']
                del config['apisix']['port_admin']


def move_real_ip_header(config):
    if 'apisix' in config and 'real_ip_header' in config['apisix']:
        if 'nginx_config' not in config:
            config['nginx_config'] = {}
            nginx_config = config['nginx_config']
            if 'http' not in nginx_config:
                nginx_config['http'] = {}
                http = nginx_config['http']
                http['real_ip_header'] = config['apisix']['real_ip_header']
                del config['apisix']['real_ip_header']


def create_deployment_if_needed(config):
    if 'deployment' not in config:
        config['deployment'] = {}


def create_admin_if_needed(config):
    create_deployment_if_needed(config)
    if 'admin' not in config['deployment']:
        config['deployment']['admin'] = {}


with open('config.yaml', 'r') as stream:
    try:
        cfg = safe_load(stream)
        move_config_center(cfg)
        move_etcd(cfg)
        move_admin_keys(cfg)
        move_ssl(cfg)
        move_port_admin(cfg)
        print(dump(cfg))
    except YAMLError as e:
        print(e)

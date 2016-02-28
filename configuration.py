__author__ = 'rayer'

'''
This section stores data the same among all nodes.
'''

symbolic_link_map = (
    ('deploy.py', '/usr/bin/deploy'),
    ('version_list.py', '/usr/bin/version_list'),
    ('sesame2.py', '/usr/bin/sesame2'),
    ('vmmanage.py', '/usr/bin/vmmanage'),
    ('vmcluster.py', '/usr/bin/vmcluster'),
    ('deploy_private.py', '/usr/bin/deploy_private')

)

# This section indicates which application should be started
# First one is command, second one is demonized or not(will be run as 'nohup <app> &'
init_exec = (
    ('comm_server.py', True),
)

logger_config = {
    'log_dir': '/var/log/',
    'def_log_level': '',
}

interface_br = {
    'management': 'bridge0',
    'control': 'bridge1',
    'cluster': 'bridge1'
}

sesame_inf = {
    'def_serial': '',
    'def_sesame': ''
}

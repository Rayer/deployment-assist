Profiles = {
    'default': {
        'nic': 3,
        'nic_map': ('bridge0', 'bridge1', 'bridge1'),
        'cpu': 8,
        'memory': 16,
        'ipv6': False,
        'status': 'initialize'
    },
    'sz35_scg': {
        'inherit': 'default',
        'type': 'scg',
        'memory': 20
    }
}

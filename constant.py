__author__ = 'Rayer'

'''
Available resources. Please add this resource map while supporting new branches.
'''
resource_map = {
    'master': 'http://172.17.17.38:8081/nexus/content/groups/ruckus-public/ruckus/official/',
    'branches': {
        'ml': {
            'version': '3.4.0.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/ML/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/ML/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'

                },
                'vscg': {
                    'root': '{$master}vscg/ML/installer/',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }}
        },
        'sz3.2.1': {
            'version': '3.2.1.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/3.2.1.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/3.2.1.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/3.2.1.0/installer/',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.4_int': {
            'version': '3.4.0.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/sz34_int/ESPP/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/sz34_int/ESPP/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/sz34_int/ESPP/installer/',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.4_rel': {
            'version': '3.4.0.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/sz34_rel/3.4.0.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/sz34_rel/3.4.0.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/sz34_rel/3.4.0.0/installer/',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.1': {
            'version': '3.1.0.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/3.1/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/3.1/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/3.1/installer',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.1.1': {
            'version': '3.1.1.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/3.1.1/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/3.1.1/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/3.1.1/installer',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.1.2': {
            'version': '3.1.2.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/3.1.2.0/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/3.1.2.0/installer',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/3.1.2.0/installer',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        },
        'sz3.2': {
            'version': '3.2.0.0.{$build}',
            'variants': {
                'scg': {
                    'root': '{$master}scg/3.2.0.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scg-installer_{$version}.img'
                },
                'scge': {
                    'root': '{$master}scge/3.2.0.0/installer/',
                    'kernel': '{$root}/{$version}/vmlinuz',
                    'image': '{$root}/{$version}/scge-installer_{$version}.img'
                },
                'vscg': {
                    'root': '{$master}vscg/3.2.0.0/installer/',
                    'image': '{$root}/{$version}/vscg-{$version}.qcow2'
                }
            }
        }
    }

}

vm_storage_path = '/kvm_images/'
tmp_path = '/tmp/'

scg_manage_br = 'bridge0'
scg_cluster_br = 'bridge1'
scg_control_br = 'bridge1'

scg_default_serial = '00000089'
scg_default_saseme = 'L340thQyugjQZIzY3oEOcDiXh0QVLM0Kytu@ntb4UAj5TF@qJrLhUwESKaj'
scg_installation_wait_time = 180

type_attribute = {
    'scg': {'virtual': False},
    'scge': {'virtual': False},
    'vscg': {'virtual': True}
}

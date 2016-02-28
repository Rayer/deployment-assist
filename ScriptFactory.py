
import constant

__author__ = 'rayer'


class ScriptFactory:

    output = ''

    def __init__(self):
        pass

    @staticmethod
    # def __create_scg_factory(name, allocated_memory, nic_count, storage_path, image_path, kernel_path):
    def __create_scg_factory(scg_profile, local_files):
        print('Start creating SCG Script factory with parameter : ')
        print(scg_profile)
        print(local_files)
        s = ScriptFactory()
        s.__gen_basic_script(scg_profile)
        s.__gen_scg_template(scg_profile, local_files)
        s.__gen_nic_template(scg_profile)
        return s

    @staticmethod
    def __create_vscg_factory(scg_profile, local_files):
        print('Start creating VSCG Script factory with parameter : ')
        print(scg_profile)
        print(local_files)
        s = ScriptFactory()
        s.__gen_basic_script(scg_profile)
        s.__gen_vscg_template(scg_profile)
        s.__gen_nic_template(scg_profile)
        return s

    @staticmethod
    def create(scg_profile, local_files):

        scg_type = scg_profile['type']

        if scg_type == 'scg' or scg_type == 'scge':
            return ScriptFactory.__create_scg_factory(scg_profile, local_files)
        elif scg_type == 'vscg':
            return ScriptFactory.__create_vscg_factory(scg_profile, local_files)

    def __gen_basic_script(self, scg_profile):

        scg_profile.update({'memory_m': scg_profile['memory'] * 1024})
        self.output += 'virt-install --name %(name)s --ram %(memory_m)d --vcpus=%(cpu)d --os-type=linux \
        --os-variant=rhel6 --vnc --wait 0 ' % scg_profile

    # will done file operations before generating the script
    def __gen_scg_template(self, scg_profile, local_files):
        # gen storage script
        self.output += '--hvm --disk path=%(qcow2_path)s,device=disk,format=qcow2,size=50,bus=sata ' % local_files
        # gen kernel install script
        self.output += '--cdrom=/%s/ipxe.iso --boot cdrom,hd ' % constant.vm_storage_path

    # will done file operations before
    # generating the script
    def __gen_vscg_template(self, scg_profile):
        # gen disk script
        self.output += '--hvm --disk path=%s/%s.qcow2 ' % (constant.vm_storage_path, scg_profile['name'])
        # gen '--import' attribute
        self.output += '--import '

    def __gen_nic_template(self, scg_profile):
        # gen nic script, first one always is "bridge0" and remainings are "bridge1"
        for x in range(scg_profile['nic']):
            if x == scg_profile['nic'] - 1:
                self.output += '--network bridge=bridge0,model=virtio '
            else:
                self.output += '--network bridge=bridge1,model=virtio '

    def generate(self):
        return self.output

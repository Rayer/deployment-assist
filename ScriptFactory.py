
import constant

__author__ = 'rayer'


class ScriptFactory:

    output = ''

    def __init__(self):
        pass

    @staticmethod
    def _create_scg_factory(name, nic_count, storage_path, image_path, kernel_path):
        print('Starting creating SCG script factory, name : %s, image_path = %s, kernel_path = %s, nic = %s' % (name, image_path, kernel_path, nic_count))
        s = ScriptFactory()
        s._gen_basic_script(name)
        s._gen_scg_template(name, storage_path, kernel_path, image_path)
        s._gen_nic_template(nic_count)
        return s

    @staticmethod
    def _create_vscg_factory(name, nic_count, image_path):
        print('Starting creating VSCG script factory, name : %s, image_path = %s, nic = %s' % (name, image_path, nic_count))
        s = ScriptFactory()
        s._gen_basic_script(name)
        s._gen_vscg_template(name)
        s._gen_nic_template(nic_count)
        return s

    @staticmethod
    def create(scg_type, name, nic_count, storage_path, image_path='', kernel_path=''):
        if scg_type == 'scg' or scg_type == 'scge':
            return ScriptFactory._create_scg_factory(name, nic_count, storage_path, image_path, kernel_path)
        elif scg_type == 'vscg':
            return ScriptFactory._create_vscg_factory(name, nic_count, storage_path)

    def _gen_basic_script(self, name):
        self.output += 'virt-install --name %s --ram 16384 --vcpus=8 --os-type=linux --os-variant=rhel6 --vnc ' % name

    # will done file operations before generating the script
    def _gen_scg_template(self, name, storage_path, kernel_path, image_path):
        # gen storage script
        self.output += '--hvm --disk path=%s,device=disk,format=qcow2,size=50,bus=sata ' % storage_path
        # gen kernel install script
        self.output += '--cdrom=/kvm_images/ipxe.iso --boot cdrom,hd '

    # will done file operations before
    # generating the script
    def _gen_vscg_template(self, name):
        # gen disk script
        self.output += '--hvm --disk path=%s/%s.qcow2 ' % (constant.vm_storage_path, name)
        # gen '--import' attribute
        self.output += '--import '

    def _gen_nic_template(self, num):
        # gen nic script, first one always is "bridge0" and remainings are "bridge1"
        for x in range(num):
            if x == num - 1:
                self.output += '--network bridge=bridge0,model=virtio '
            else:
                self.output += '--network bridge=bridge1,model=virtio '

    def generate(self):
        return self.output

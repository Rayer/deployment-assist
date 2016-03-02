#!/usr/bin/env python
# Copyright 2013 Ruckus Wireless, Inc. All rights reserved.
#
# RUCKUS WIRELESS, INC. CONFIDENTIAL - This is an unpublished, proprietary work
# of Ruckus Wireless, Inc., and is fully protected under copyright and trade
# secret laws. You may not view, use, disclose, copy, or distribute this file or
# any information contained herein except pursuant to a valid license from
# Ruckus.

# This is a fork of original rks-ipxe-boot with necessary change for automatically installing SCG in KVM

import os
import subprocess
import sys
from SimpleHTTPServer import SimpleHTTPRequestHandler
from SocketServer import TCPServer
from StringIO import StringIO
from threading import Thread

import ipxe_server

TCPServer.allow_reuse_address = True


def ipxe_handler(kernel, initrd, kernel_cmdline):
    class MyHandler(SimpleHTTPRequestHandler):
        def send_head(self):
            if self.path == "/" or self.path == "/boot.txt":
                return self.send_ipxe()
            else:
                return SimpleHTTPRequestHandler.send_head(self)

        def send_ipxe(self):
            f = StringIO("""#!ipxe
kernel %(kernel)s %(cmd)s
initrd %(initrd)s
boot
""" % {"kernel": kernel, "initrd": initrd, "cmd": kernel_cmdline})
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            return f



    return MyHandler


def is_url(path):
    for scheme in ("http", "tftp", "https"):
        if path.startswith("%s://" % scheme):
            return True
    return False


def check_existence(files):
    for f in [f for f in files if not is_url(f)]:
        if not os.path.exists(f):
            print >> sys.stderr, "file %s does not exists" % f
            sys.exit(1)


def usage():
    print >> sys.stderr, """Usage: %(script)s <kernel> <initrd> [<port>] [<cmdline>...]
This utility will host the <kernel> and <initrd> at port <port> for iPXE boot
loader to boot from. <port> is default to 8080 if it is not
speicifed. Other arguments after <port> will be used as additional kernel command line parameters.

<kernel> and <initrd> could also be URLs.

Here is an example usage:
run this command
>%(script)s vmlinuz initrd.img
and inside iPXE, you should boot from this url:
http://<your-ip>:8080/

Another example adding additional kernel command line:
>%(script)s vmlinuz initrd.img 8080 console=ttyS0,115200
You might need the additional console parameter when you are installing a
SCG-100.
""" % {"script": os.path.basename(sys.argv[0])}


def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    port = 8080
    if len(sys.argv) >= 4:
        port = int(sys.argv[3])

    check_existence(sys.argv[1:3])

    httpd = TCPServer(("", port), ipxe_handler(sys.argv[1], sys.argv[2], " ".join(["stage2=initrd:"] + sys.argv[4:])))
    print "Serving at port %d" % port
    httpd.serve_forever()

ipxe_server_thread = None

def create_ipxe_thread():

    class IpxeServer(Thread):

        def __init__(self):
            print('Creating IPXE Thread...')
            Thread.__init__(self)
            self.httpd=None

        def run(self):
            port = 12000
            print('Starting iPXE Booting server at port %d ...' % port)
            # check_existence(['/tmp/vmlinuz', '/tmp/target.img'])
            self.httpd = TCPServer(("", port), ipxe_handler('vmlinuz', 'target.img', 'stage2=initrd:'))
            self.httpd.serve_forever()

        def stop(self):
            self.httpd.shutdown()

    # remove firewall policy
    print('Removing firewall policy')
    subprocess.check_output(['iptables', '--flush'])
    ipxe_server.ipxe_server_thread = IpxeServer()
    ipxe_server.ipxe_server_thread.start()


def cleanup_ipxe_thread():
    try:
        if ipxe_server.ipxe_server_thread is not None:
            ipxe_server.ipxe_server_thread.stop()
    except Exception as e:
        print('Error in shutdowning ipxe server')
        print(e.message)

if __name__ == "__main__":
    main()

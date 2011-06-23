'''
	@author: msune

	Ofelia XEN Agent settings file (Static settings) 
'''
##General Parameters

'''Base folder where vms and logs will be store.
All the rest of folder must be inside this folder'''
OXA_PATH="/opt/ofelia/oxa/"


'''Log folder. Must exist!'''
OXA_LOG="/opt/ofelia/oxa/log/"


'''XMLRPC over HTTPS server parameters'''
#XMLRPC_SERVER_LISTEN_HOST='127.0.0.1' # You should not use '' here, unless you have a real FQDN.
XMLRPC_SERVER_LISTEN_HOST='0.0.0.0' # You should not use '' here, unless you have a real FQDN.
XMLRPC_SERVER_LISTEN_PORT=9229

XMLRPC_SERVER_KEYFILE='security/certs/agent.key'    # Replace with your PEM formatted key file
XMLRPC_SERVER_CERTFILE='security/certs/agent.crt'  # Replace with your PEM formatted certificate file

##FileHD driver settings
'''Enable/disable file-type Hdmanager Cache FS'''
OXA_FILEHD_USE_CACHE=True

'''Cache folder to store VMs (if cache mechanism is used)'''
OXA_FILEHD_CACHE_VMS="/opt/ofelia/oxa/cache/vms/"

'''Remote folder to store VMs'''
OXA_FILEHD_REMOTE_VMS="/opt/ofelia/oxa/remote/vms/"

'''Cache folder for templates (if cache is enabled)'''
OXA_FILEHD_CACHE_TEMPLATES="/opt/ofelia/oxa/cache/templates/"

'''Remote folder for templates'''
OXA_FILEHD_REMOTE_TEMPLATES="/opt/ofelia/oxa/remote/templates/"

##Ofelia Debian VM configurator parameters
'''Kernel and initrd that will be used by machines'''
OXA_DEBIANCONF_XEN_SERVER_KERNEL="/boot/vmlinuz-2.6.32-5-xen-amd64"
OXA_DEBIANCONF_XEN_SERVER_INITRD="/boot/initrd.img-2.6.32-5-xen-amd64"

'''Debian usual file locations'''
OXA_DEBIANCONF_DEBIAN_INTERFACES_FILE_LOCATION = "/etc/network/interfaces"
OXA_DEBIANCONF_DEBIAN_UDEV_FILE_LOCATION = "/etc/udev/rules.d/70-persistent-net.rules"
OXA_DEBIANCONF_DEBIAN_HOSTNAME_FILE_LOCATION="/etc/hostname"

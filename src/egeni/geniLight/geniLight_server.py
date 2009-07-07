from soaplib.wsgi_soap import SimpleWSGISoapApp
from soaplib.service import soapmethod
from geniLight_types import *
import socket
import struct
import sys
from ctypes import create_string_buffer

SOAP_INTERFACE_PORT = 7889
AGGREGATE_MANAGER_PORT = 2603
AGGREGATE_MANAGER_IP = 'localhost'
#AGGREGATE_MANAGER_IP = 'openflowvisor.stanford.edu'

# Message IDs for all the GENI light calls
# This will be used by the aggrMgr controller
SFA_START_SLICE = 101
SFA_STOP_SLICE = 102
SFA_DELETE_SLICE = 103
SFA_CREATE_SLICE = 104
SFA_LIST_SLICES = 105
SFA_LIST_COMPONENTS = 106
SFA_REGISTER = 107
SFA_REBOOT_COMPONENT = 108

def print_buffer(buf):
    for i in range(0,len(buf)):
        print('%x' % buf[i])

def extract(sock):
    # Shud we first obtain the message length?
    # msg_len = socket.ntohs(sock.recv(2))
    msg = ""

    while (1):
        try:
            chunk = sock.recv(1)
        except socket.error, message:
            if 'timed out' in message:
                break
            else:
                sys.exit("Socket error: " + message)

        if len(chunk) == 0:
            break
        msg += chunk

    print 'done extracting response from aggrMgr'
    return msg
   
def connect(server, port):
    '''Connect to the Aggregate Manager module'''
    sock = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    sock.connect ( ( server, port) )
    sock.settimeout(1)
    print 'connected to aggregate manager module'
    return sock
    
def connect_aggrMgr():
    return connect(AGGREGATE_MANAGER_IP, AGGREGATE_MANAGER_PORT)

##
# The GeniServer class provides stubs for executing Geni operations at
# the Aggregate Manager.

class GeniLightServer(SimpleWSGISoapApp):
    def __init__(self):
        self.__tns__ = "http://yuba.stanford.edu/geniLight/"

    # implicitly no __init__()
    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def start_slice(self, slice):
        slice_id = slice.save_to_string()
        buf = create_string_buffer(2 + 1 + len(slice_id)) 
        format = 'hB%ds' % len(slice_id)
        struct.pack_into(format, buf, 0, socket.htons(len(buf)),
                SFA_START_SLICE, slice_id)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()

        return GeniResult(1, 'Success')

    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def stop_slice(self, slice):
        slice_id = slice.save_to_string()
        buf = create_string_buffer(2 + 1 + len(slice_id)) 
        format = 'hB%ds' % len(slice_id)
        struct.pack_into(format, buf, 0, socket.htons(len(buf)),
                SFA_STOP_SLICE, slice_id)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()

        return GeniResult(1, 'Success')

    @soapmethod(UserSliceInfo,String,_returns=GeniResult)
    def create_slice(self, slice, rspec_str):
        slice_id = slice.save_to_string()
        buf = create_string_buffer(2 + 1 + len(slice_id) + len(rspec_str)) 
        format = 'hB%ds%ds' % (len(slice_id), len(rspec_str))
        struct.pack_into(format, buf, 0, socket.htons(len(buf)),
                SFA_CREATE_SLICE, slice_id, rspec_str)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()

        return GeniResult(1, 'Success')

    @soapmethod(UserSliceInfo,_returns=GeniResult)
    def delete_slice(self, slice):
        slice_id = slice.save_to_string()
        buf = create_string_buffer(2 + 1 + len(slice_id)) 
        format = 'hB%ds' % len(slice_id)
        struct.pack_into(format, buf, 0, socket.htons(len(buf)),
                SFA_DELETE_SLICE, slice_id)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()

        return GeniResult(1, 'Success')

    @soapmethod(_returns=String)
    def list_slices(self):
        buf = create_string_buffer(2 + 1) 
        struct.pack_into('hB', buf, 0, socket.htons(len(buf)),
                SFA_LIST_SLICES)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        aggrMgr_sock.close()

        return 'list of slices'

    @soapmethod(_returns=String)
    def list_components(self):
        buf = create_string_buffer(2 + 1) 
        struct.pack_into('hB', buf, 0, socket.htons(len(buf)), SFA_LIST_COMPONENTS)

        aggrMgr_sock = connect_aggrMgr()
        aggrMgr_sock.send(buf)
        component_list = extract(aggrMgr_sock);
        aggrMgr_sock.close()

        return component_list 

if __name__=='__main__':
    try:from cherrypy.wsgiserver import CherryPyWSGIServer
    except:from cherrypy._cpwsgiserver import CherryPyWSGIServer
    
    if len(sys.argv) > 2:
        AGGREGATE_MANAGER_IP = sys.argv[1]
        AGGREGATE_MANAGER_PORT = int(sys.argv[2])
        
    gls = GeniLightServer()
    server = CherryPyWSGIServer(('localhost',SOAP_INTERFACE_PORT),gls)

    try:
        server.start()
    except (KeyboardInterrupt):
        sys.exit(0)

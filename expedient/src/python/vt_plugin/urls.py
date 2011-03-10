from django.conf.urls.defaults import *
from expedient.common.rpc4django.utils import rpc_url
from expedient.common.rpc4django import rpcmethod

urlpatterns = patterns('vt_plugin.controller.vtAggregateController.vtAggregateController',
    url(r'^aggregate/create/$', 'aggregate_crud', name='vt_plugin_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='vt_plugin_aggregate_edit'),
)


urlpatterns = urlpatterns + patterns('vt_plugin.controller.dispatchers.GUIdispatcher',
    url(r'^goto_create_vm/(?P<slice_id>\d+)/$', 'goto_create_vm', name='goto_create_vm'),
    url(r'^manage_vm/(?P<slice_id>\d+)/(?P<vm_id>\d+)/(?P<action_type>\w+)/$', 'manage_vm', name='manage_vm'),
    url(r'^virtualmachine_crud/(?P<slice_id>\d+)/(?P<server_id>\d+)/$', 'virtualmachine_crud', name='virtualmachine_crud'),
)


urlpatterns = urlpatterns + patterns('',
     rpc_url(r'^xmlrpc/vt_am/$', name='vt_am'),
)

from django.http import *
from django.core.urlresolvers import reverse
import os
import sys
from vt_plugin.models import *
from vt_manager.communication.utils.XmlUtils import *
from vt_plugin.utils.ServiceThread import *
from vt_plugin.utils.Translator import *

class ProvisioningResponseDispatcher():

    '''
    Handles all the VT AM vm provisioning responses and all the actions that go 
    from the VT AM to the VT Plugin
    '''

    @staticmethod
    def processResponse(response):
        print "Entra en processResponse\n"
        for action in response.action:

            #if Action.objects.filter(uuid = action.id).exists():
            if Action.objects.filter(uuid = action.id):
                #actionModel is an instance to the action stored in DB with uuid the same as the incomming action
                actionModel = Action.objects.get(uuid = action.id)
            else:                
                actionModel =Translator.ActionToModel(action, "provisioning", save = "noSave")
                #TODO adapt code in order to enter "if" when received SUCCESS status from actions generated by island manager
                actionModel.status = 'QUEUED' #this state is just to enter de if later
                actionModel.vm = VM.objects.get(uuid = action.virtual_machine.uuid)
                
            if actionModel.status is 'QUEUED' or 'ONGOING':                
                print "The response is:"
                print actionModel
                print actionModel.uuid
                print "actionModel.status = %s" %actionModel.status

                #update action status in DB
                actionModel.status = action.status
                print "The action.status is %s" %action.status
                actionModel.description = action.description
                actionModel.save()
                
                #according to incoming action response we do update the vm state
                if actionModel.status == 'SUCCESS':
                    if actionModel.type == 'create':
                        actionModel.vm.setState('created (stopped)')
                        actionModel.vm.save()
                    elif actionModel.type == 'start' or actionModel.type == 'reboot':
                        actionModel.vm.setState('running')
                        actionModel.vm.save()                        
                    elif actionModel.type == 'hardStop':
                        actionModel.vm.setState('stopped')
                        actionModel.vm.save()
                    elif actionModel.type == 'delete':
                        actionModel.vm.delete()
                elif actionModel.status == 'FAILED':
                    actionModel.vm.setState('failed')
                    actionModel.vm.save()
                elif actionModel.status == 'ONGOING':
                    if actionModel.type == 'create':
                        actionModel.vm.setState('creating...')
                        actionModel.vm.save()
                    elif actionModel.type == 'start':
                        actionModel.vm.setState('starting...')
                        actionModel.vm.save()
                    elif actionModel.type == 'hardStop':
                        actionModel.vm.setState('stopping...')
                        actionModel.vm.save()
                    elif actionModel.type == 'delete':
                        actionModel.vm.setState('deleting...')
                        actionModel.vm.save()
                    elif actionModel.type == 'reboot':
                        actionModel.vm.setState('rebooting...')
                        actionModel.vm.save()
                else:                    
                    actionModel.vm.setState('unknown')
                    actionModel.vm.save()

                return "Done Response"

            else:
                try:
                    raise Exception
                except Exception as e:
                    print e
                    return

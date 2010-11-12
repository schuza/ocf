import shlex, subprocess
from django.db import models
from django.db.models.fields import IPAddressField
import paramiko
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.resources.models import Resource, Sliver
from expedient.common.utils.modelfields import LimitedIntegerField
from expedient.common.middleware import threadlocals
from expedient.clearinghouse.utils import post_message_to_current_user
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.slice.models import Slice

class SSHServer(Resource):
    ip_address = IPAddressField(
        "IP address",
        help_text="Specify the server's IP address.",
    )
    ssh_port = LimitedIntegerField(
        "SSH port number",
        min_value=1,
        max_value=2**16-1,
        default=22,
        help_text="Specify the SSH port number to use."
    )

    def is_alive(self):
        """Ping the server and check if it's alive.
        
        @return: True if ping succeeds, False otherwise.
        """
        ret = subprocess.call(
            shlex.split("ping -c 1 -W 2 %s" % self.ip_address),
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.STDOUT,
        )
        
        if ret == 0:
            return True
        else:
            return False
        
    def exec_command(self, command, **connection_info):
        """Connect to the server using an SSH session and execute a command.
        
        @param command: The command to execute
        @type command: C{str}
        @param username: The username to use to connect to the server.
        @type username: C{str}
        @keyword connection_info: A dict of other info to pass to
            C{paramiko.SSHClient.exec_command}.
        @return: A (stdin, stdout, stderr) tuple that is three file-like
            objects.
        @rtype: tuple(C{paramiko.ChannelFile}, C{paramiko.ChannelFile},
            C{paramiko.ChannelFile})
        """

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            self.ip_address,
            port=self.port,
            **connection_info
        )
        return client.exec_command(command)
    
    def __unicode__(self):
        return u"SSH server at IP %s" % self.ip_address
        
class SSHServerSliver(Sliver): pass

class SSHSliceInfo(models.Model):
    slice = models.OneToOneField(Slice)
    public_key = models.TextField()
    
class SSHAggregate(Aggregate):
    information = "An aggregate of SSH servers that are controlled" \
        " by a single administrator, to which users can request" \
        " access. Once approved, users get SSH access to all" \
        " machines using a public key they provide."

    class Meta:
        verbose_name = "SSH Aggregate"

    admin_username = models.CharField(max_length=255)
    private_key = models.TextField()

    add_user_command = models.TextField(
        default="sudo useradd -m %(username)s",
        help_text="Specify the command to create a new user. " \
            "'%(username)s' will be replaced by the user's " \
            " username. The command should return non-zero on failure " \
            " and 0 on success.",
    )
    del_user_command = models.TextField(
        default="sudo userdel -r -f %(username)s",
        help_text="Specify the command to delete an existing user. " \
            "'%(username)s' will be replaced by the user's " \
            " username. The command should return non-zero on failure " \
            " and 0 on success.",
    )
    add_pubkey_user_command = models.TextField(
        default="sudo -u %(username)s mkdir /home/%(username)s/.ssh; "
            "sudo -u %(username)s chmod 700 /home/%(username)s/.ssh; "
            "sudo -u %(username)s echo %(pubkey)s >> "
            "/home/%(username)s/.ssh/authorized_keys",
        help_text="Specify the command to add a public key to a user's " \
            "account. '%(username)s' will be replaced by the user's " \
            " username and '%(pubkey)s' will be replaced by the public key." \
            " The command should return non-zero on failure " \
            " and 0 on success.",
    )
    
    def _op_user(self, op, server, cmd_subs, quiet=False):
        """common code for adding/removing users."""
        
        cmd = getattr(self, "%s_user_command" % op) % cmd_subs
        cmd = cmd + "; echo $?"
        _, stdout, _ = server.exec_command(
            cmd,
            username=self.username,
            pkey=self.private_key,
        )
        
        lines = stdout.readlines()
        ret = int(lines[-1].strip())
        
        if ret != 0:
            error = "".join(lines[:-1])
            if not quiet:
                msg = "Failed to %s user on %s. Output was:\n%s" \
                    % (op, server, error),
                post_message_to_current_user(
                    msg,
                    msg_type=DatedMessage.TYPE_ERROR,
                )
            raise Exception(msg)

    def add_user(self, server, username, pubkey, quiet=False):
        """Add a user to a server.
        
        Add a user with username C{username} with public key C{pubkey} to
        server C{server}.
        
        @param server: The server to add the user to.
        @type server: L{SSHServer}
        @param username: the new user's username
        @type username: C{str}
        @param pubkey: The public key to add to the user's account.
        @type pubkey: the public key's value a C{str} 
        @keyword quiet: If True, no messages will be sent on failure.
            Defaults to False.
        @type quiet: C{boolean}
        """
        self._op_user("add", server, {"username": username}, quiet)
        self._op_user(
            "add_pubkey",
            server,
            {"username": username, "pubkey": pubkey},
            quiet,
        )
    
    def del_user(self, server, username, quiet=False):
        """Remove user from a server.
        
        Remove user with username C{username} from server C{server}.
        
        @param server: The server to remove the user from.
        @type server: L{SSHServer}
        @param username: the user's username
        @type username: C{str}
        @keyword quiet: If True, no messages will be sent on failure.
            Defaults to False.
        @type quiet: C{boolean}
        """
        self._op_user("del", server, {"username": username}, quiet)
        
    def check_status(self):
        return self.available and reduce(
            lambda x, y: x and y.is_alive(),
            SSHServer.objects.filter(aggregate__id=self.id),
    )
    
    def start_slice(self, slice):
        super(SSHAggregate, self).start_slice(slice)
        
        slice_info = SSHSliceInfo.objects.get(slice=slice)
        user = slice.owner
        slivers = SSHServerSliver.objects.filter(
            slice=slice, resource__aggregate_id=self.id)

        succeeded = []
        for sliver in slivers:
            # Execute the command on the server and get status
            server = sliver.resource.as_leaf_class()
            
            try:
                self.add_user(server, user.username, slice_info.public_key)
            except:
                for s in succeeded:
                    try:
                        self.del_user(s, user.username)
                    except:
                        pass
                raise
            
            succeeded.append(server)
            
    def stop_slice(self, slice):
        super(SSHAggregate, self).start_slice(slice)
        user = threadlocals.get_thread_locals()["user"]
        for sliver in SSHServerSliver.objects.filter(slice=slice):
            server = sliver.resource.as_leaf_class()
            try:
                self.del_user(server, user.username)
            except:
                pass

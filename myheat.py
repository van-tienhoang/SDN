# %%
# read this https://devinpractice.com/2018/11/05/openstack-heat-python-tutorial/
# https://docs.openstack.org/python-novaclient/latest/reference/api/index.html
from heatclient import client as heat_client
from keystoneauth1 import loading
from keystoneauth1 import session

# %%

kwargs = {
    'auth_url': 'https://127.0.0.1:5000/v3',
    'username': 'admin',
    'password': 'sde-4511',
    'project_name': "admin",
    'user_domain_name': "Default",
    'project_domain_name': "default"
}
# %%

loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(**kwargs)
sess = session.Session(auth=auth, verify=False)

client = heat_client.Client('1', session=sess, endpoint_type='public', service_type='orchestration')
# %%
# list stack
for stack in client.stacks.list():
    print(stack)

#%%

def create_stack(stack_file_path, stack_name, heatclient, parameters=None):
    template = open(stack_file_path)
    if parameters:
        stack = heatclient.stacks.create(stack_name=stack_name,
                                         template=template.read(), parameters=parameters)
    else:
        stack = heatclient.stacks.create(stack_name=stack_name,
                                         template=template.read())
        template.close()
    return stack


def delete_stack(stack_id, heatclient):
    heatclient.stacks.delete(stack_id)


def list_stacks(heatclient):
    return heatclient.stacks.list()

#%%
import psutil


def check_script_running(script_name="ArrivalE.py"):
    """
    check if scrip_name is running
    :param script_name: name of script, default value is ArrivalE.py
    :return: True if it is running; otherwise False
    """
    for pid in psutil.pids(script_name):
        p = psutil.Process(pid)
        if p.name() == "python" and len(p.cmdline()) > 1 and script_name in p.cmdline()[1]:
            print ("ArrivalE.py is running")
            return True
    return False


def check_if_no_VM_left(_heat_client):
    """
    check if there is no VM left
    :return:
    """
    return is_having_stack(_heat_client)


def is_having_stack(_heat_client):
    """
    check if there is any stack in the system
    :return: True if there is no stack in the system, otherwise False
    """
    stacks = _heat_client.stack.list()
    if len(list(stacks) < 1):
        return True
    return False

#%%
#https://docs.openstack.org/python-novaclient/latest/reference/api/index.html
#%% create nova client to count number of vm
from novaclient import client
nova = client.Client('2','admin', 'sde-4511', "admin", 'https://172.29.2.7:5000/v3')

#%% try using 2nd method
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

AUTH_URL = 'https://172.29.2.7:5000/v3'
USERNAME = 'admin'
PASSWORD = 'sde-4511'
PROJECT_ID = 'f204416af77e4a699f5331b834189e36'
USER_DOMAIN_NAME="Default"

nova = client.Client("2", session=sess)
nova.servers.list()


def get_number_of_vm_in_system():
    from keystoneauth1 import loading
    from keystoneauth1 import session
    from novaclient import client
    # %%

    kwargs = {
        'auth_url': 'https://172.29.2.7:5000/v3',
        'username': 'admin',
        'password': 'sde-4511',
        'project_name': "admin",
        'user_domain_name': "Default",
        'project_domain_name': "default"
    }
    # %%

    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(**kwargs)
    sess = session.Session(auth=auth, verify=False)
    nova = client.Client("2", session=sess)
    number_vm = nova.servers.list()
    return len(number_vm)

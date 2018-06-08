import pytest
from sailfish.lib.errors import VmError
from sailfish.lib.builtins.builtin_types import ContractRef

''' 
Note: Members removed as owners remain members.  Members can see owners/members of their channel;
non-members cannot. Members removed as members are also removed as owners if possible.
'''

VERSION = '1.0.0'
ADMINS = ContractRef('admins', VERSION)

def test_admins(network):
    # Setup the local network.
    network.reset()
    network.publish([ADMINS])

    identities = ['alice', 'bob', 'carlos', 'eve', 'felix', 'george']
    for i in identities:
        network.register_identity(i)
    
    alice_api = network.alice.admins
    bob_api = network.bob.admins
    carlos_api = network.carlos.admins
    eve_api = network.eve.admins
    felix_api = network.felix.admins
    george_api = network.george.admins

    
    #alice creates channel
    alice_api.create_channel(channel_str = 'alice_channel')
    
    #raises error; bob is not an owner
    with pytest.raises(Exception) as e:
        bob_api.add_members(channel_str = 'alice_channel', members=['carlos'])

    
    #alice adds bob as owner
    alice_api.add_owners(channel_str = 'alice_channel', owners=['bob'])
    #bob adds carlos as a member
    bob_api.add_members(channel_str = 'alice_channel', members=['carlos'])
    #bob removes alice as an owner, but not as a member
    bob_api.remove_owners(channel_str = 'alice_channel', owners=['alice'])
    
    #alice_channel has 1 owner and 3 members
    assert len(bob_api.get_owners(channel_str = 'alice_channel')) == 1 
    assert len(alice_api.get_members(channel_str = 'alice_channel')) == 3

    #bob adds 2 owners that are already members
    bob_api.add_owners(channel_str = 'alice_channel', owners=['alice','carlos'])
    #carlos removes alice as a member
    carlos_api.remove_members(channel_str = 'alice_channel', members=['alice'])
    assert len(bob_api.get_owners(channel_str = 'alice_channel')) == 2 
    assert len(carlos_api.get_members(channel_str = 'alice_channel')) == 2
    #alice can no longer access info in alice_channel
    with pytest.raises(Exception) as e:
        assert len(alice_api.get_members(channel_str = 'alice_channel')) == 2
    

    #felix creates channel
    felix_api.create_channel(channel_str='felix_channel')
    #felix adds alice, bob, carlos, eve as members
    felix_api.add_members(channel_str = 'felix_channel', members=['alice','bob','carlos','eve'])
    #felix now removes bob as a member
    #felix_api.remove_members(channel_str = 'felix_channel', members=['bob'])
    
        
    #felix_channel has 1 owner and 4 members
    assert len(felix_api.get_owners(channel_str='felix_channel')) == 1
    assert len(felix_api.get_members(channel_str='felix_channel')) == 4
   
    #raises error; felix cannot see alice_channel's data
    with pytest.raises(Exception) as e:
        assert len(felix_api.get_members(channel_str='alice_channel')) == 4

    #bob adds felix,george,alice as members to alice channel
    bob_api.add_members(channel_str = 'alice_channel', members=['felix','george','alice'])
    #now felix can see members
    assert len(felix_api.get_members(channel_str='alice_channel')) == 5
    



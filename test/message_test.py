import pytest
from sailfish.lib.errors import VmError
from sailfish.lib.builtins.builtin_types import ContractRef

VERSION = '1.0.0'
MESSAGES = ContractRef('messages', VERSION)
ADMINS = ContractRef('admins', VERSION)

def test_messages(network):
    # Setup the local network.
    network.reset()
    network.publish([ADMINS,MESSAGES])

    identities = ['alice', 'bob', 'carlos', 'eve', 'felix', 'george', 'xander']
    for i in identities:
        network.register_identity(i)
    
    alice_api = network.alice.messages
    bob_api = network.bob.messages
    carlos_api = network.carlos.messages
    eve_api = network.eve.messages
    felix_api = network.felix.messages
    george_api = network.george.messages
    xander_api = network.xander.messages
    
    #alice posts message
    alice_api.create_channel(channel_str = 'alice_channel')
    alice_api.post_message(channel_str = 'alice_channel', msg_str = 'Hello World')
    alice_api.post_message(channel_str = 'alice_channel', msg_str = 'The quick brown fox...')
    alice_api.add_members(channel_str = 'alice_channel', members = ['felix', 'carlos'])
    felix_api.post_message(channel_str = 'alice_channel', msg_str = '...jumps over the lazy dog.')
    alice_api.add_owners(channel_str = 'alice_channel', owners = ['eve'])
    
    bob_api.create_channel(channel_str = 'bob\'s cool room')
    bob_api.add_members(channel_str = 'bob\'s cool room', members = ['alice', 'george'])
    
    assert alice_api.get_message_mult(channel_str = 'alice_channel', identity = 'felix')[0] == '...jumps over the lazy dog.'
    assert 'Hello World' in alice_api.get_message_mult(channel_str = 'alice_channel', identity = 'alice')
    assert len(felix_api.get_message_mult(channel_str = 'alice_channel')) == 3
    #xander can't read alice_channel messages
    with pytest.raises(Exception) as e:
        assert xander_api.get_message_mult(channel_str = 'alice_channel', identity = 'felix')[0] == '...jumps over the lazy dog.'
    
    eve_api.add_owners(channel_str = 'alice_channel', owners = ['carlos'])
    
    #remove owner
    eve_api.remove_owners(channel_str = 'alice_channel', owners = ['alice'])
    #alice can't add owners
    with pytest.raises(Exception) as e:
        alice_api.add_owners(channel_str = 'alice_channel', owners = ['george'])

    #import pdb; pdb.set_trace()

    #remove member
    eve_api.remove_members(channel_str = 'alice_channel', members = ['alice'])
    #import pdb; pdb.set_trace()

    #alice can't read messages
    with pytest.raises(Exception) as e:
        assert alice_api.get_message_mult(channel_str = 'alice_channel', identity = 'felix')[0] == '...jumps over the lazy dog.'

    
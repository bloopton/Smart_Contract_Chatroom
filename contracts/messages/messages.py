# MessageConstruct: Network Identity, message string, timestamp
MessageConstruct = Tuple[Identifier, str, Timestamp]
# E.g. Dict[TX['identity'],string, TX['timestamp']
messages_key = 'messages'

admins = Contract('admins', '1.0.0', direct=True)

import pdb

#Scope: channel
# -> Store list of MessageConstruct tuples
message_list = []

#creates channel
@public
@clientside
def create_channel(channel_str: str)->None:
    with PostTxArgs(PUBLIC, [PUBLIC], []):
        _create_channel(channel_str)

@executable
def _create_channel(channel_str: str)->None:
    admins.create_channel(channel_str)
    channel = admins.get_channel(channel_str)
    with PostTxArgs(channel, [PUBLIC], []): #channel/member lists are public
        _add_owners(channel_str = channel_str, owners = [TX['identity']])

@public
@clientside
def post_message(channel_str: str, msg_str: str) -> None:
    #get channel
    channel = admins.get_channel(channel_str)
    #post msg to channel
    with PostTxArgs(channel, [PUBLIC], []):
        _post_message(msg_str)
        
#return single message
@public
@clientside
def get_message_single(channel_str : str, index : int) -> MessageConstruct:
    channel = admins.get_channel(channel_str)
    messages_list = admins.get_data(channel, messages_key)

#return List of message tuples; if identity is given, return messages of just a person
@public
@clientside
def get_message_mult(channel_str : str, identity : str = None) -> List[str]:
    channel = admins.get_channel(channel_str)
    messages_list = admins.get_data(channel, messages_key)
    temp_list = []
    return_list = []
    if identity != None :
        temp_list = [message for message in messages_list if message[0]==identity]
        for message in temp_list:
            return_list.append(message[1])
    else :
        for message in messages_list:
            return_list.append(message[1])

    assert isinstance(return_list, List)
    return return_list


@executable
def _post_message(msg_str: str)->None:
    #create formatted message tuple
    msg = (TX['identity'], msg_str, TX['timestamp'])
    #add message to MessageList
    message_list.append(msg)
    #STORAGE executable for post_message
    admins.put_message(messages_key = messages_key, msg_list = message_list)

@public
@clientside
def add_owners(channel_str: str, owners: List[Identifier]) -> None:
    channel = admins.get_channel(channel_str)
    with PostTxArgs(channel, [PUBLIC], []): #channel/member lists are public
        _add_owners(channel_str = channel_str, owners = owners)
@executable
def _add_owners(channel_str: str, owners: List[Identifier]) -> None:
        admins.add_owners(channel_str = channel_str, owners = owners)
    

@public
@clientside
def add_members(channel_str: str, members: List[Identifier]) -> None:
    channel = admins.get_channel(channel_str)
    with PostTxArgs(channel, [PUBLIC], []): #channel/member lists are public
        _add_members(channel_str = channel_str, members = members)
@executable
def _add_members(channel_str: str, members: List[Identifier]) -> None:
    admins.add_members(channel_str = channel_str, members = members)
    
@public
@clientside
def remove_owners(channel_str: str, owners : List[Identifier]) -> None:
    channel = admins.get_channel(channel_str)
    with PostTxArgs(channel, [], []):
        _remove_owners(channel_str, channel, owners)

@executable
def _remove_owners(channel_str: str, channel: ChannelName, owners : List[Identifier]) -> None:
    admins.remove_owners(channel_str, channel, owners)

@public
@clientside
def remove_members(channel_str: str, members : List[Identifier]) -> None:
    channel = admins.get_channel(channel_str)
    with PostTxArgs(channel, [], []):
        _remove_members(channel_str, channel, members)

@executable
def _remove_members(channel_str: str, channel: ChannelName, members : List[Identifier]) -> None:
    admins.remove_members(channel_str, channel, members)
      
        
        
        
        


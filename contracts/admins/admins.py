#Contract for chatroom admins (channel owners)

import pdb

members_key = 'members'
owners_key = 'owners'

'''
Functions to wrap in messages begin

'''
@public
def get_channel(channel_str: str) -> ChannelName:
    return STORAGE.get(PUBLIC, channel_str)

@public
def get_data(channel : ChannelName, storage_key : str) -> Any:
    return STORAGE.get(channel, storage_key)

@public
def put_message(messages_key : str, msg_list : List[Tuple]) -> None:
    STORAGE.put(messages_key, List[Tuple], msg_list)

'''
Functions to wrap in messages end

'''



#Create chat room, optionally add additional owners
#Chatroom is channel
@public
def create_channel(channel_str: str, owners: List[Identifier] = []) -> None:
    channel = new_channel('MSG')#create a new channel
    owners = owners + [TX['identity']]#add channel creator as owner
    STORAGE.put(channel_str, ChannelName, channel)  #key is channel string like alice's channel
    #_add_owners(channel_str, owners)   

#add_owners for cross-contract use
@public
def add_owners(channel_str: str, owners: List[Identifier]) -> None:
    channel = STORAGE.get(PUBLIC, channel_str)
    _add_members(channel_str, owners)
    for o in owners:
        add_owner(channel, o)
    owners_list = STORAGE.get(channel, owners_key)#get members of channel
    if owners_list is not None :
        owners_list = owners_list + owners # concat
        owners_set = set(owners_list); #remove duplicates
        owners = list(owners_set);    
    __add_owners(owners)

#Default add all owners as members; for internal contract use
def _add_owners(channel_str: str, owners: List[Identifier]) -> None:
    channel = STORAGE.get(PUBLIC, channel_str)
    _add_members(channel_str, owners)
    for o in owners:
        add_owner(channel, o)
    owners_list = STORAGE.get(channel, owners_key)#get members of channel
    if owners_list is not None :
        owners_list = owners_list + owners # concat
        owners_set = set(owners_list); #remove duplicates
        owners = list(owners_set);
    with PostTxArgs(channel, [PUBLIC], []): #channel/member lists are public
        __add_owners(owners)

#Store (owners) channel/network identity list pairs in STORAGE- Key is 'owners'
def __add_owners(owners: List[Identifier]) -> None:  
    STORAGE.put(owners_key, List[Identifier], owners)#post member list back to channel, with key as 'members'

#Add members (sends keys); for cross-contract use
@public
def add_members(channel_str: str, members: List[Identifier]) -> None:
    channel = STORAGE.get(PUBLIC, channel_str) 
    for m in members:
        send_key(channel, m)
    members_list = STORAGE.get(channel, members_key)#get members of channel
    if members_list is not None :
        members_list = members_list + members # concat
        members_set = set(members_list); #remove duplicates
        members = list(members_set);
    __add_members(members)
    
    
#Add members (sends keys); for internal contract use
def _add_members(channel_str: str, members: List[Identifier]) -> None:
    channel = STORAGE.get(PUBLIC, channel_str) 
    for m in members:
        send_key(channel, m)
    members_list = STORAGE.get(channel, members_key)#get members of channel
    if members_list is not None :
        members_list = members_list + members # concat
        members_set = set(members_list); #remove duplicates
        members = list(members_set);
    with PostTxArgs(channel, [PUBLIC], []): #channel/member lists are public
        __add_members(members)
    
#Store (members) channel/network identity list pairs in STORAGE- Key is 'members'
def __add_members(members: List[Identifier]) -> None:
    STORAGE.put(members_key, List[Identifier], members)#post member list back to channel, with key as 'members'

#Accessor for owners
@public
def get_owners(channel_str: str)->List[Identifier]:
    channel = STORAGE.get(PUBLIC, channel_str)
    return STORAGE.get(channel, owners_key)

#Accessor for members
@public
def get_members(channel_str: str)->List[Identifier]:
    channel = STORAGE.get(PUBLIC, channel_str)
    return STORAGE.get(channel, members_key)

#Remove owners, keeps members
#Remove channel from identity owner list, PUT back in STORAGE 
@public
def remove_owners(channel_str: str, owners : List[Identifier]) -> None:
    #old channel is going to be cycled out
    channel = STORAGE.get(PUBLIC, channel_str)
    #Store list of owners
    owners_list = STORAGE.get(channel, owners_key)
    #Store list of members
    members_list = STORAGE.get(channel, members_key)
    #Remove owner(s) from list
    for o in owners:
        owners_list.remove(o)
    #rotate key
    rotate_key(channel)
    #add back members
    add_members(channel_str, members_list)
    #add remaining owners back to channel; i.e. call add_owners
    with PostTxArgs(channel, [PUBLIC], []):#
        _remove_owners(channel, channel_str, owners_list)#add back all valid owners as members/owners

#store updated owners list
@executable
def _remove_owners(channel: ChannelName, channel_str: str, owners: List[Identifier]) -> None:
    for o in owners:
        send_key(channel, o)#send keys to all valid owners
    STORAGE.put(owners_key, List[Identifier], owners)#post owner list back to channel, with key as 'owners'

#Remove members, default remove owners
#Rotate key, and read back all remaining members.
#Remove channel from identity member list, PUT back in STORAGE 
@public
def remove_members(channel_str: str, members : List[Identifier]) -> None:
    remove_owners(channel_str, members)
    channel = STORAGE.get(PUBLIC, channel_str)
    #Store list of members
    members_list = STORAGE.get(channel, members_key)
    #Remove owner(s) from list
    for m in members:
        members_list.remove(m)
    #rotate key
    rotate_key(channel)
    with PostTxArgs(channel, [], []):
        _remove_members(channel, channel_str, members_list)#store the channel in the public channel

#change channel members
@executable
def _remove_members(channel: ChannelName, channel_str: str, members: List[Identifier]) -> None:
    for m in members:
        send_key(channel, m)
    STORAGE.put(members_key, List[Identifier], members)#post member list back to channel, with key as 'members'



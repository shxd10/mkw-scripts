from dolphin import memory, utils, event

def main():
    region = utils.get_game_id()
    global og_values
    og_values = {}
    try:
        address_list = {"RMCE01": (0x805acec0, 0x805acecc, 0x805aced8)}
        for address in address_list[region]:
            og_values[address] = memory.read_u32(address)
            memory.write_u32(address, 0x60000000)
            memory.invalidate_icache(address, 0x4)
    except KeyError:
        raise RegionError

@event.on_scriptend
def revert(id_):
    if utils.get_script_id() == id_:
        if memory.is_memory_accessible():
            for address in og_values.keys():
                memory.write_u32(address, og_values[address])
                memory.invalidate_icache(address, 0x4)
        else:
            print('Memory not accessible.')
            print("Couldn't reverse the effect of the script")


@event.on_savestateload
def reload(*_):
    global og_values
    region = utils.get_game_id()
    if memory.is_memory_accessible():
        try:
            address_list = {"RMCE01": (0x805acec0, 0x805acecc, 0x805aced8)}
            for address in address_list[region]:
                og_values[address] = memory.read_u32(address)
                memory.write_u32(address, 0x60000000)
                memory.invalidate_icache(address, 0x4)
        except KeyError:
            raise RegionError        

if __name__ == '__main__':
    main()
   

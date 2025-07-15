from dolphin import utils, debug


PAL_EV_ADDR = {
                0x8057db60 : "Hop Reset",
                0x8057db68 : "Hop Reset",
                0x8057db70 : "Hop Reset",
                0x8057dba4 : "Hop Gain",
                0x8057dbb0 : "Hop Gain",
                0x8057dbbc : "Hop Gain",
                0x805880f4 : 'Lean effect', #https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartMove.cc#L2323
                0x80588104 : 'Lean effect', 
                0x80588114 : 'Lean effect',
                0x80596be4 : 'Slowfall', # Stage 1 typically
                0x80596bec : 'Slowfall', 
                0x80596bf4 : 'Slowfall', 
                0x805b52fc : 'Mult 0.998', # https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartDynamics.cc#L104
                0x805b5304 : 'Mult 0.998',
                0x805b5308 : 'Mult 0.998',
                0x805aec6c : 'EV to IV', # https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartDynamics.cc#L115
                0x805aec78 : 'EV to IV',
                0x805aec84 : 'EV to IV',
                0x805b4b90 : 'Respawn',
                0x805b4b94 : 'Respawn',
                0x805b4b98 : 'Respawn',
                0x805b5288 : '"Forces"', # https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartDynamics.cc#L98
                0x805b528c : '"Forces"', # Forces comes from gravity, but also this : https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartMove.cc#L1529
                0x805b5290 : '"Forces"',
                0x805b76f4 : "FloorCol Y 4",
                0x805b772c : "FloorCol Y 1",
                0x805b7734 : "FloorCol X",
                0x805b7738 : "FloorCol Z",
                0x805b7754 : "FloorCol Y 2", #seems to reset to 0
                0x805b52a4 : "FloorCol Y 3", #seems to reset to 0  https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartDynamics.cc#L101
                0x805b7de8 : 'Wheel EV decay', #https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartCollide.cc#L744 ?
                0x805b7df4 : 'Wheel EV decay',
                0x805b7e00 : 'Wheel EV decay',
                0x805b4d2c : 'Canon Entry',
                0x805b4d30 : 'Canon Entry',
                0x805b4d34 : 'Canon Entry',
                0x80585290 : 'Canon Duration',
                0x80585298 : 'Canon Duration',
                0x805852a0 : 'Canon Duration',
                0x8057ff2c : "Slow Ramp",
                0x8057ff34 : "Slow Ramp",
                0x8057ff3c : "Slow Ramp",
                0x80568a00 : 'Tumble launch',
                0x80568a0c : 'Tumble launch', #typically colliding a chainchomp
                0x80568a18 : 'Tumble launch',
                0x80568dac : 'Tumble land',
                0x80568db4 : 'Tumble land',
                0x80568dbc : 'Tumble land',                
                0x805690e8 : 'Flip launch',
                0x805690f0 : 'Flip launch', #typically a cataquack setting your EV to (0,60,0)
                0x805690f8 : 'Flip launch',
                0x80569170 : 'Some Object',
                0x80569180 : 'Some Object',
                0x80569190 : 'Some Object',
                0x80569558 : 'Flip mid air',
                0x80569560 : 'Flip mid air',
                0x80569568 : 'Flip mid air',
                0x805694cc : 'Flip landing',
                0x805694d4 : 'Flip landing',
                0x805694dc : 'Flip landing',
                0x80569a78 : 'Squish',
                0x80569a80 : 'Squish',
                0x80569a88 : 'Squish',
               }

NTSCU_EV_ADDR = {
                0x805772fc : "Hop Reset",
                0x80577304 : "Hop Reset",
                0x8057730c : "Hop Reset",
                0x80577340 : "Hop Gain",
                0x8057734c : "Hop Gain",
                0x80577358 : "Hop Gain",
                0x805818d0 : 'Lean effect', 
                0x805818e0 : 'Lean effect', 
                0x805818f0 : 'Lean effect', 
                0x805aa3d4 : 'Mult 0.998',
                0x805aa3dc : 'Mult 0.998',
                0x805aa3e0 : 'Mult 0.998',
                0x805a3d44 : 'EV to IV',
                0x805a3d50 : 'EV to IV',
                0x805a3d5c : 'EV to IV',
                0x805aa360 : 'Gravity',
                0x805aa364 : 'Gravity',
                0x805aa368 : 'Gravity',
                0x805ac80c : "SuperGrind?",
                0x805ac810 : "SuperGrind?",
                0x805acec0 : 'Wheel EV decay',
                0x805acecc : 'Wheel EV decay',
                0x805aced8 : 'Wheel EV decay',
               }

PAL_POS_ADDR = {
    0x805b4b84 : "Respawn 1", #TP to 0
    0x805b4b88 : "Respawn 1",
    0x805b4b8c : "Respawn 1",
    0x80590254 : "Respawn 2", #TP to Respawn
    0x80590258 : "Respawn 2",
    0x8059025c : "Respawn 2",
    0x80579be0 : "Respawn 3", #slowfall before gravity
    0x80579be8 : "Respawn 3",
    0x80579bf0 : "Respawn 3",
    0x805b5628 : "Speed",
    0x805b5634 : "Speed",
    0x805b5640 : "Speed",
    0x805b6d88 : "Collision 1", #Walls/Floor typically
    0x805b6d8c : "Collision 1",
    0x805b6d90 : "Collision 1",
    0x80597098 : "Collision 2", #Corner ?
    0x805970a4 : "Collision 2",
    0x805970b0 : "Collision 2",
    0x80597490 : "Vehicle compensation",
    0x805974a0 : "Vehicle compensation",
    0x805974b0 : "Vehicle compensation",
    0x80596e2c : "Collision Object",  #tree in rPB for example, or wigglers, or pipes
    0x80596e3c : "Collision Object",
    0x80596e4c : "Collision Object",
    0x80585238 : "Canon", 
    0x80585240 : "Canon",
    0x80585248 : "Canon",
    0x80586698 : "Reject Road?", #reject road ??? 
    0x805866a0 : "Reject Road?",
    0x805866a8 : "Reject Road?", 
    }


PAL_IV_ADDR = {
    0x8057bc44 : "Acceleration", #When holding A or B
    0x8057c00c : "Soft Cap", #Include walls
    0x8057bffc : "Soft Cap backward", #When you exceed the soft cap with negative speed
    0x8057af04 : "Deceleration", #When not holding A or B(multiply by 0.98 ?)
    0x8057af78 : "Turn Decel", #When turning with handling
    0x8057affc : "Air Decel", #When in the air for 5+ frames (multiply by 0.999 ?)
    0x8057ac2c : "EV to IV", #https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartMove.cc#L1198
    0x8057b0e4 : "Slope", #when you get speed from being on a slope. Only works below 30 IV ?
    0x8057bc88 : "SSMT", #Multiply by 0.8 ?
    0x8057bcac : "0 IV lock", #When you hold B, you'll stay at 0IV for a few frame before reversing
    0x8057ac48 : "Backward IV decel", #If your is IV under -20, it add 0.5 to your IV (seemingly)
    0x80578554 : "Canon Reset", #Reset IV to 0 when entering the canon
    0x805850c8 : "Canon 2", # Set IV to cap every frame 
    
    }

def union_dict(*args):
    res = {}
    for d in args:
        for k in d.keys():
            res[k] = d[k]
    return res

def get_addr_dict():
    region = utils.get_game_id()
    if region == 'RMCE01':
        return NTSCU_EV_ADDR
    elif region == 'RMCP01':
        return union_dict(PAL_EV_ADDR, PAL_POS_ADDR, PAL_IV_ADDR)
    else:
        return {}


def make_mbp(addr):
    mbp_dict = { "At" : addr,
           "BreakOnRead" : False,
           "BreakOnWrite" : True,
           "LogOnHit" : True,
           "BreakOnHit" : False}
    debug.set_memory_breakpoint(mbp_dict)
           

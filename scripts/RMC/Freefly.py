from dolphin import event
from Modules import mkw_utils
from Modules.framesequence import Frame
from Modules.mkw_classes import vec3, VehiclePhysics, eulerAngle
import math


def main():
    global position
    position = VehiclePhysics.position(0)

    global speed
    speed = 80

    global angles
    angles = mkw_utils.get_facing_angle(0)

    global prevInput
    prevInput = Frame([0,0,0,0,0,0,0,0])

    global frame
    frame = mkw_utils.frame_of_input()

    global yawAcc
    yawAcc = eulerAngle(0,2,0)

    global pitchAcc
    pitchAcc = eulerAngle(2,0,0)
    

if __name__ == '__main__':
    main()

@event.on_frameadvance
def on_frame_advance():
    global frame
    global angles
    global position
    global prevInput
    global speed
    
    newframe = frame != mkw_utils.frame_of_input()
    frame = mkw_utils.frame_of_input()

    if newframe :
        curInput = Frame.from_current_frame(0)

        angles += yawAcc * (curInput.stick_x / 7)
        angles -= pitchAcc * (curInput.stick_y / 7)

        if curInput.item and not prevInput.item :
            speed *= 1.1
        if curInput.brake and not prevInput.brake:
            speed /= 1.1

        if curInput.accel:
            position += angles.get_unit_vec3() * speed
            
        prevInput = curInput

    mkw_utils.player_teleport(0, position.x, position.y, position.z,
                                angles.pitch, angles.yaw, 0)


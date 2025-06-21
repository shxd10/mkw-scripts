from Modules import ttk_lib
from Modules.mkw_utils import frame_of_input
from Modules.framesequence import FrameSequence, Frame



def main() -> None:
    nulFrameSequence = FrameSequence()
    nulFrameSequence.read_from_list_of_frames([Frame.default() for _ in range(frame_of_input())])
    ttk_lib.setPlayerRKGBuffer(nulFrameSequence)

if __name__ == '__main__':
    main()

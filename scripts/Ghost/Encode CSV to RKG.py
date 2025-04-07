import sys
import os
from rkg_lib import decode_RKG, FrameSequence, RKGMetaData, encode_RKG


if __name__ == "__main__":
    if len(sys.argv) < 2:
        for filename in os.listdir():
            if filename[-4:] == '.csv':
                rkg_filename = filename[:-4]+'pyencode'+'.rkg'
                metadata_filename = filename[:-4]+'.txt'
                mii_filename = filename[:-4]+'.mii'
                
                inputList = FrameSequence(filename)
                
                with open(metadata_filename, 'r') as f:
                    if f is None:
                        metadata = RKGMetaData(None, True)
                    else:
                        metadata = RKGMetaData.from_string(f.read())
                
                with open(mii_filename, 'rb') as f:
                    if f is None:
                        mii_data = f.read()[:0x4A]
                    else:
                        mii_data = bytearray(0x4A)
                rkg_data = encode_RKG(metadata, inputList, mii_data)

                with open(rkg_filename, 'wb') as f:
                    f.write(rkg_data)
    else:
        filename = sys.argv[1]
        if filename[-4:] == '.csv':
            rkg_filename = filename[:-4]+'pyencode'+'.rkg'
            metadata_filename = filename[:-4]+'.txt'
            mii_filename = filename[:-4]+'.mii'
            
            inputList = FrameSequence(filename)
            
            with open(metadata_filename, 'r') as f:
                if f is None:
                    metadata = RKGMetaData(None, True)
                else:
                    metadata = RKGMetaData.from_string(f.read())
            
            with open(mii_filename, 'rb') as f:
                if f is None:
                    mii_data = f.read()[:0x4A]
                else:
                    mii_data = bytearray(0x4A)
            rkg_data = encode_RKG(metadata, inputList, mii_data)

            with open(rkg_filename, 'wb') as f:
                f.write(rkg_data)

                    

import sys
import os
from rkg_lib import decode_RKG


if __name__ == "__main__":
    if len(sys.argv) < 2:
        for filename in os.listdir():
            if filename[-4:] == '.rkg':
                with open(filename, "rb") as f:
                    raw_data = f.read()
                csv_filename = filename[:-4]+'.csv'
                metadata_filename = filename[:-4]+'.txt'
                mii_filename = filename[:-4]+'.mii'
                metadata, inputList, mii_data = decode_RKG(raw_data)
                
                inputList.write_to_file(csv_filename)
    else:
        with open(sys.argv[1], "rb") as f:
            raw_data = f.read()
        csv_filename = filename[:-4]+'.csv'
        metadata_filename = filename[:-4]+'.txt'
        mii_filename = filename[:-4]+'.mii'
        metadata, inputList, mii_data = decode_RKG(raw_data)
        
        inputList.write_to_file(csv_filename)



from decoder import Decoder
import os

# couldn't be bothered to make ini lol
gecko_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gecko_here.txt")
script_path = "C:\\Users\\lenovo\\Documents\\GitHub\\mkw-scripts\\scripts\\RMC\\test.py"

def main(path: str, script_path, type: str):
    decoder = Decoder()
    decoder.run(path, script_path, type)

if __name__ == "__main__":
    main(gecko_path, script_path, "gecko")

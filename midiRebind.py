import mido
from mapping import GrandMA2
from test import toDec
import sys
if __name__ == '__main__':
    Inter=GrandMA2.MidiInterface("patch/test.ini")
    Par=GrandMA2.MessageParse()
    Acts=GrandMA2.Actions(Inter)

    #message=toDec("F0 7F 	7F 	02 	7F 	01 	33 37 2E 32 30 30 00 35 20 31 	F7")
    #message=toDec("F0 7F 	7F 	02 	7F 	06 	02 02 4C 39 	F7")
    try:
        for msg in Inter.input:
            print("Received {}".format(msg))
            try:
                match=Par(message)
                res=Acts(match)
            except GrandMA2.MatchError:
                pass
            except:
                print("[Unexpected error] {}".format(sys.exc_info()[1]))

    except KeyboardInterrupt:
        print("[Keyboard Interrupt] : Exiting...")
        del Inter
        sys.exit()

import mido
from mapping import GrandMA2
from test import toDec
import sys
if __name__ == '__main__':
    Inter=GrandMA2.MidiInterface("patch/default.ini")
    Par=GrandMA2.MessageParse()
    Acts=GrandMA2.Actions(Inter)

    try:
        for msg in Inter.input:
            #print("Received {}".format(msg))
            try:
                match=Par(msg)
                print(match)
                res=Acts(match)
            except GrandMA2.MatchError:
                pass
            except:
                print("[Unexpected error] {}".format(sys.exc_info()))

    except KeyboardInterrupt:
        print("[Keyboard Interrupt] : Exiting...")
        del Inter
        sys.exit()

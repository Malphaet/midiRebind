#!/bin/python3

import mido, argparse, sys
import configparser,importlib


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Listen to a midi interface for incomming messages and send messages to different midi interfaces according to a patch file')

    parser.add_argument('patch', type=str,help='The patch file, this file is mandatory')
    parser.add_argument('--verbose', action='store_true',default=False,help='Make the program verbose)')

    args = parser.parse_args()

    try:
        path="patch/{}.ini".format(args.patch)
        conf=configparser.ConfigParser()
        conf.read(path)
        interpath="mapping.{}".format(conf["interface"]["mapping"])

        Module=importlib.import_module(interpath)

        #from mapping import GrandMA2
        Inter=Module.MidiInterface(path) # TODO, take directly a config object, will save some time
        Par=Module.MessageParse()
        Acts=Module.Actions(Inter)

        for msg in Inter.input:
            if args.verbose:
                try:
                    print("[Received] {}".format(str.join([hex(i).split('x')[1] for i in msg.data])))
                except:
                    print("[Received {}".format(msg))
            try:
                match=Par(msg)
                res=Acts(match)
            except Module.MatchError:
                pass
            except:
                print("[Unexpected error@midibind.py] {}".format(sys.exc_info()))
    except ImportError:
        print("[Error] Module {} doesn't exist".format(interpath))
    except KeyboardInterrupt:
        print("[Keyboard Interrupt] : Exiting...")
        del Inter
        sys.exit()
    except OSError:
        print('[Error] The patch "patch/{}.ini" is ill-formed or non-existent'.format(args.patch))

#!/bin/python3

import mido, argparse, sys
import configparser,importlib,mapping


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

        Inter=Module.MidiInterface(path) # TODO, take directly a config object, will save some time
        Par=Module.MessageParse()
        Acts=Module.Actions(Inter)

        if args.verbose:
            def vprint(msg):
                print(msg)
            mapping.base.vprint=vprint
        for msg in Inter.input:
            if args.verbose:
                try:
                    print("[Received]: {}".format(str.join([hex(i).split('x')[1] for i in msg.data])))
                except:
                    print("[Received]: {}".format(msg))
            try:
                match=Par(msg)
                res=Acts(match)
            except Module.MatchError:
                pass
            except KeyError:
                vprint("[Error] Command in {} could not be recognised".format(msg))
            except:
                 print("[Unexpected error@midibind.py] {}".format(sys.exc_info()))
    except ImportError as e:
        print("[Error] There was an error loading module {} ({})".format(interpath,e))
    except KeyError as e:
        print("[Error] There was an error while loading patch {} ({})".format(path,e))
    except KeyboardInterrupt:
        print("[Keyboard Interrupt] : Exiting...")
        #del Inter
        sys.exit()
    except OSError as e:
        print('[Error] The patch "patch/{}.ini" is ill-formed or non-existent'.format(args.patch))
        print(e)
    except TypeError as e:
        print("[Error] Can't iterate over an emplty list, check the list of inputs for an available input")
        print(e)
    # except KeyError

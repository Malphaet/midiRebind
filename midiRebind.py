import mido

if __name__ == '__main__':
    o=mido.open_output("Midi Through Port-0")
    print(o)
    o.close()

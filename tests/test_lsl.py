from pylsl import resolve_streams


print("Buscando streams LSL...")

streams = resolve_streams()

for stream in streams:
    print("Nombre:", stream.name())
    print("Tipo:", stream.type())
    print("Canales:", stream.channel_count())
    print("-----")

from pylsl import resolve_streams

print("Buscando streams LSL...")

streams = resolve_streams()

for s in streams:
    print("Nombre:", s.name())
    print("Tipo:", s.type())
    print("Canales:", s.channel_count())
    print("-----")
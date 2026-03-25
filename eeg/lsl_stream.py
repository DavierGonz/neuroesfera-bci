from pylsl import StreamInlet, resolve_stream

def connect_eeg():

    print("Buscando stream EEG...")

    streams = resolve_stream('type', 'EEG')

    inlet = StreamInlet(streams[0])

    print("EEG conectado")

    return inlet
from pylsl import StreamInfo, StreamOutlet


def create_marker_stream():

    info = StreamInfo(
        name='NeuroEsferaMarkers',
        type='Markers',
        channel_count=1,
        nominal_srate=0,
        channel_format='string',
        source_id='neuroesfera_bci'
    )

    outlet = StreamOutlet(info)

    print("Marker stream listo")

    return outlet


def send_marker(outlet, marker):

    outlet.push_sample([marker])

    print("Marker enviado:", marker)

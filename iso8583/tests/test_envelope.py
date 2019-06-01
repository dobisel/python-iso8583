import binascii

from iso8583.models import Envelope, Element, Bitmap


def test_envelope_repr():
    envelope = Envelope('0200')
    assert isinstance(envelope.bitmap, Bitmap)
    assert repr(envelope) == \
        '<ISO8583 00000000000000000000000000000000000000000000000000000000'\
        '00000000 />'

    envelope.set(2)
    envelope.set(3)
    envelope.set(11)
    envelope.set(37)
    assert repr(envelope) == \
        '<ISO8583 01100000001000000000000000000000000010000000000000000000' \
        '00000000 />'

    envelope.unset(2)
    assert repr(envelope) == \
        '<ISO8583 00100000001000000000000000000000000010000000000000000000' \
        '00000000 />'


def test_envelope_load_dump():
    mac_key = binascii.unhexlify(MAC_KEY)
    envelope = Envelope.loads(SAMPLE, mac_key)
    assert envelope.mti == 1100
    assert envelope.bitmap == 0x6030050008E10001

    dumped = envelope.dumps()
    assert dumped == SAMPLE


MAC_KEY = b'1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C'
SAMPLE = \
    b'027111006030050008E100011662802314007513' \
    b'5966000076242719052313153821140121124410' \
    b'191431376242701111102000001111102   65\xc8\xc7' \
    b'\xe4\xdf \xe3\xd3\xdf\xe4             \xca\xe5' \
    b'\xd1\xc7\xe4        THRIR00' \
    b'00011234567890070212290073P13006762427CI' \
    b'F012111001209483PHN01109121902288TKT003S' \
    b'FTTOK003000TKR0020272CCB6661787BFE6'


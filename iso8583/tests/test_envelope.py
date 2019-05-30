from iso8583.models import Envelope, Element, Bitmap


def test_envelope_repr():
    envelope = Envelope('0200')
    assert isinstance(envelope.bitmap, Bitmap)
    assert repr(envelope) == \
        '<ISO8583 00000000000000000000000000000000000000000000000000000000'\
        '00000000 />'

    envelope.set(2)
    envelope.set(20)
    envelope.set(37)
    envelope.set(40)
    assert repr(envelope) == \
        '<ISO8583 01000000000000000001000000000000000010010000000000000000'\
        '00000000 />'

    envelope.unset(2)
    assert repr(envelope) == \
        '<ISO8583 00000000000000000001000000000000000010010000000000000000'\
        '00000000 />'


def test_envelope_append():
    envelope = Envelope('0200')
    two = Element.create(2)
    envelope.set_element(two)
    envelope.set(20)

    assert 2 in envelope
    assert 20 in envelope
    assert two in envelope
    assert 30 not in envelope

    envelope.unset(20)
    assert 20 not in envelope


def test_envelope_load():
    sample = \
        b'027111006030050008E100011662802314007513' \
        b'5966000076242719052313153821140121124410' \
        b'191431376242701111102000001111102   65\xc8\xc7' \
        b'\xe4\xdf \xe3\xd3\xdf\xe4             \xca\xe5' \
        b'\xd1\xc7\xe4        THRIR00' \
        b'00011234567890070212290073P13006762427CI' \
        b'F012111001209483PHN01109121902288TKT003S' \
        b'FTTOK003000TKR0020272CCB6661787BFE6'

    envelope = Envelope.loads(sample)
    assert envelope.mti == 1100
    assert envelope.bitmap == 0x6030050008E10001



"""
def test_getitem():
    envelope = Envelope('0200')
    envelope.set(
    assert envelope[1] == field1


def test_delete():
    envelope = Envelope('0200')

    field2 = VariableLengthField(2)
    envelope += field2
    del envelope[1]
    assert field2 not in envelope


def test_str()
    excepted_str = '\n'.join([
        '002\tn\t12\t123456789012345\tPrimary account number (PAN)',
        '037\tan\t12\tempty\tRetrieval reference number',
    ])

    envelope = Envelope('0200')

    field2 = VariableLengthField(2, value=1234567890123456)
    envelope += field2

    field37 = FixedLengthField(37)
    envelope += field37

    assert str(envelope) == excepted_str


def test_envelope_dumps():
    envelope = Envelope('0200')

    pan = VariableLengthField(2)
    pan.value = 123456789
    envelope += pan

    process_code = FixedLengthField(3)
    process_code.value = 123456
    envelope += process_code

    amount = FixedLengthField(4, value=123456789012)
    envelope += amount

    retrieval_reference_number = FixedLengthField(37, value='abc123456789')
    envelope += retrieval_reference_number

    private_additional_data = VariableLengthField(48, value='123456abc')
    envelope += private_additional_data

    dumped = envelope.dumps()

    assert dumped == b'0200700000000801000009123456789123456123456789012' \
        b'abc123456789009123456abc'

def test_envelope_loads():
    ISO_message = b'0200700000000801000009123456789123456123456789012' \
        b'abc123456789009123456abc'

    envelope = Envelope.loads(ISO_message)

    assert envelope[2].value = 123456789
    assert envelope[3].value = 123456
    assert envelope[4].value = 123456789012
    assert envelope[37].value = 'abc123456789'
    assert envelope[48].value = '123456abc'
"""

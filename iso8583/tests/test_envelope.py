from iso8583 import Envelope, VariableLengthField, FixedLengthField


def test_bitmap():
    envelope = Envelope('0200')

    field2 = VariableLengthField(2)
    envelope += field2

    field20 = VariableLengthField(20)
    envelope += field20

    field37 = FixedLengthField(37)
    envelope += field37

    field48 = VariableLengthField(48)
    envelope += field48

    assert envelope.bitmap == \
        0b0100000000000000000100000000000000001000000000010000000000000000

    assert repr(envelope) == \
        '<ISO8583 01000000000000000001000000000000000010000000000100000000'\
        '00000000 />'


def test_add():
    envelope = Envelope('0200')

    field2 = VariableLengthField(2)
    envelope += field2

    field3 = FixedLengthField(3, value=123)
    envelope += field3

    assert field2 in envelope
    assert field3 in envelope


def test_getitem():
    envelope = Envelope('0200')

    field1 = VariableLengthField(2, value=123)
    envelope += field1
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


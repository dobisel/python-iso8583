import abc
import struct
import binascii


class Bitmap:
    _map = None

    def __init__(self, value=0, *, secondary=False):
        self._map = value
        self.secondary = secondary
        if secondary:
            self._map |= (1 << 127)

    @property
    def size(self):
        return 128 if self.secondary else 64

    def __repr__(self):
        return bin((1 << self.size) | self._map)[3:]

    def set(self, index):
        self._map |= 1 << (self.size - index)

    def unset(self, index):
        mask = ((1 << self.size) - 1) ^ (1 << (self.size - index))
        self._map &= mask

    def __eq__(self, other):
        if isinstance (other, int):
            return self._map == other

        return str(self) == other

    def __contains__(self, index):
        bit = 1 << (self.size - index)
        return bit & self._map

    @classmethod
    def from_hexstring(cls, hexstring):
        v = binascii.unhexlify(hexstring[:16])
        secondary = v[0] & (1 << 7)
        v = struct.unpack('!Q', v)[0]
        if secondary:
            v <<= 64
            v |= struct.unpack('!Q', hexstring[16:32])

        return cls(v, secondary=secondary)


class Envelope:
    bitmap = None
    mti = None
    elements = None

    def __init__(self, mti, secondary_bitmap=False, bitmap=0):
        self.mti = mti
        self.elements = {}
        if isinstance(bitmap, Bitmap):
            self.bitmap = bitmap
        else:
            self.bitmap = Bitmap(bitmap)

            if secondary_bitmap:
                self.secondary_bitmap = 0b0
                self.bitmap |= 1 << 127
            else:
                self.secondary_bitmap = None

    @property
    def bitmap_size(self):
        return 128 if self.secondary_bitmap else 64

    @property
    def bitmap_last(self):
        return self.bitmap_size - 1

    def set_element(self, element):
        self.elements[element.index] = element
        self.bitmap.set(element.index)

    def set(self, index, value=None):
        self.set_element(Element.create(index, value))

    def unset(self, index):
        self.bitmap.unset(index)
        del self.elements[index]

    def __repr__(self):
        return f'<ISO8583 {self.bitmap} />'

    def __contains__(self, element_or_index):
        if isinstance(element_or_index, Element):
            index = element_or_index.index
        else:
            index = element_or_index

        return index in self.elements

    def __iter__(self):
        for i in range(1, self.size):
            e = self.elements.get(i)
            if e is None:
                continue

            yield e

    @classmethod
    def loads(cls, message):
        # Length
        length = int(message[:4])
        assert length == len(message) - 4, 'Invalid length'

        # MTI
        mti = int(message[4:8])

        # Bitmap
        bitmap = Bitmap.from_hexstring(message[8:])
        envelope = cls(mti, bitmap=bitmap)

        return envelope

    def dumps(self):
        raise NotImplementedError()


class Element(metaclass=abc.ABCMeta):
    def __init__(self, index, kind, size, title, value=None):
        self.index = index
        self.kind = kind
        self.size = size
        self.title = title
        self.value = value

    @classmethod
    def create(cls, index, value=None):
        if index not in ISO8583_LAYOUT:
            raise ValueError(f'Invalid element index: {index}')

        kind, storage, size, title = ISO8583_LAYOUT[index]
        type_ = FixedLengthElement if storage == 'fixed' \
            else VariableLengthElement

        return type_(index, kind, size, title, value)


class VariableLengthElement(Element):
    pass


class  FixedLengthElement(Element):
    pass


ISO8583_LAYOUT = {
    0:  None,  # Reserved for bitmap
    1:  ('b',   'fixed',    64,  'Second Bitmap'),
    2:  ('n',   'variable', 19,  'Primary account number (PAN)'),
    3:  ('n',   'fixed',    6,   'Processing code'),
    4:  ('n',   'fixed',    12,  'Amount, transaction'),
    5:  ('n',   'fixed',    12,  'Amount, settlement'),
    6:  ('n',   'fixed',    12,  'Amount, cardholder billing'),
    7:  ('n',   'fixed',    10,  'Transmission date & time'),
    8:  ('n',   'fixed',    8,   'Amount cardholder billing fee'),
    9:  ('n',   'fixed',    8,   'Conversion rate, settlement'),
    10: ('n',   'fixed',    8,   'Conversion rate, cardholder billing'),
    11: ('n',   'fixed',    6,   'System trace audit number (STAN)'),
    12: ('n',   'fixed',    6,   'Local transaction time (hhmmss)'),
    13: ('n',   'fixed',    4,   'Local transaction date (MMDD)'),
    14: ('n',   'fixed',    4,   'Expiration date'),
    15: ('n',   'fixed',    4,   'Settlement date'),
    16: ('n',   'fixed',    4,   'Currency conversion date'),
    17: ('n',   'fixed',    4,   'Capture date'),
    18: ('n',   'fixed',    4,   'Merchant type, or merchant category code'),
    19: ('n',   'fixed',    3,   'Acquiring institution (country code)'),
    20: ('n',   'fixed',    3,   'PAN extended (country code)'),
    21: ('n',   'fixed',    3,   'Forwarding institution (country code)'),
    22: ('n',   'fixed',    3,   'Point of service entry mode'),
    23: ('n',   'fixed',    3,   'Application PAN sequence number'),
    24: ('n',   'fixed',    3,   'Function code (ISO 8583:1993), or network international identifier (NII)'),
    25: ('n',   'fixed',    2,   'Point of service condition code'),
    26: ('n',   'fixed',    2,   'Point of service capture code'),
    27: ('n',   'fixed',    1,   'Authorizing identification response length'),
    28: ('x+n', 'fixed',    8,   'Amount, transaction fee'),
    29: ('x+n', 'fixed',    8,   'Amount, settlement fee'),
    30: ('x+n', 'fixed',    8,   'Amount, transaction processing fee'),
    31: ('x+n', 'fixed',    8,   'Amount, settlement processing fee'),
    32: ('n',   'variable', 11,  'Acquiring institution identification code'),
    33: ('n',   'variable', 11,  'Forwarding institution identification code'),
    34: ('ns',  'variable', 28,  'Primary account number, extended'),
    35: ('z',   'variable', 37,  'Track 2 data'),
    36: ('n',   'variable', 104, 'Track 3 data'),
    37: ('an',  'fixed',    12,  'Retrieval reference number'),
    38: ('an',  'fixed',    6,   'Authorization identification response'),
    39: ('an',  'fixed',    2,   'Response code'),
    40: ('an',  'fixed',    3,   'Service restriction code'),
    41: ('ans', 'fixed',    8,   'Card acceptor terminal identification'),
    42: ('ans', 'fixed',    15,  'Card acceptor identification code'),
    43: ('ans', 'fixed',    40,  'Card acceptor name/location (1-23 street address, 24-36 city, 37-38 state, 39-40 country)'),
    44: ('an',  'variable', 25,  'Additional response data'),
    45: ('an',  'variable', 76,  'Track 1 data'),
    46: ('an',  'variable', 999, 'Additional data (ISO)'),
    47: ('an',  'variable', 999, 'Additional data (national)'),
    48: ('an',  'variable', 999, 'Additional data (private)'),
    49: ('n',   'fixed',    3,   'Currency code, transaction'),
    50: ('n',   'fixed',    3,   'Currency code, settlement'),
    51: ('n',   'fixed',    3,   'Currency code, cardholder billing'),
    52: ('b',   'fixed',    64,  'Personal identification number data'),
    53: ('n',   'fixed',    16,  'Security related control information'),
    54: ('an',  'variable', 120, 'Additional amounts'),
    55: ('ans', 'variable', 999, 'ICC data – EMV having multiple tags'),
    56: ('ans', 'variable', 999, 'Reserved (ISO)'),
    57: ('ans', 'variable', 999, 'Reserved (national)'),
    58: ('ans', 'variable', 999, 'Reserved (national)'),
    59: ('ans', 'variable', 999, 'Reserved (national)'),
    60: ('ans', 'variable', 999, 'Reserved (national) (e.g. settlement request: batch number, advice transactions: original transaction amount, batch upload: original MTI plus original RRN plus original STAN, etc.)'),
    61: ('ans', 'variable', 999, 'Reserved (private) (e.g. CVV2/service code   transactions)'),
    62: ('ans', 'variable', 999, 'Reserved (private) (e.g. transactions: invoice number, key exchange transactions: TPK key, etc.)'),
    63: ('ans', 'variable', 999, 'Reserved (private)'),
    64: ('b',   'fixed',    64,  'Message authentication code (MAC)'),
}

import abc
import struct
import binascii

from .cryptohelpers import iso9797_mac


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
        if isinstance(other, int):
            return self._map == other

        if isinstance(other, type(self)):
            return self._map == other._map

        # Treath as string
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

    def __iter__(self):
        for i in range(1, self.size + 1):
            if i in self:
                yield i

    def to_hexstring(self):
        primary = (self._map >> 8) if self.secondary else self._map
        result = binascii.hexlify(struct.pack('!Q', self._map))
        if self.secondary:
            result += struct.pack('!Q', ((1 << 8) - 1), self._map)

        return result.upper()


class Envelope:
    bitmap = None
    mti = None
    elements = None

    def __init__(self, mti, mackey=None, secondary_bitmap=False, bitmap=0):
        self.mackey = mackey
        self.mti = mti
        self.elements = {}
        if isinstance(bitmap, Bitmap):
            self.bitmap = bitmap
        else:
            self.bitmap = Bitmap(bitmap, secondary=secondary_bitmap)

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

    def __getitem__(self, i):
        return self.elements[i]

    @classmethod
    def loads(cls, message, mackey):
        # Length
        length = int(message[:4])
        assert length == len(message) - 4, 'Invalid length'

        # MTI
        mti = int(message[4:8])

        # Bitmap
        bitmap = Bitmap.from_hexstring(message[8:])
        envelope = cls(mti, mackey=mackey, secondary_bitmap=bitmap.secondary)
        cursor = (bitmap.size // 8) * 2 + 8
        for i in bitmap:
            e = Element.create(i)
            cursor += e.parse(message[cursor:])
            envelope.set_element(e)

        assert bitmap == envelope.bitmap
        mac = envelope[128 if bitmap.secondary else 64].value
        calculated_mac = iso9797_mac(message[4:-16], mackey)
        assert mac == calculated_mac
        return envelope

    def dumps(self):
        ignore = []
        if self.bitmap.secondary:
            ignore.append(128)
        else:
            ignore.append(64)

        parts = []
        for i in self.bitmap:
            if i in ignore:
                continue
            parts.append(self.elements[i].dumps())

        body = b'%04d%s%s' % (
            self.mti,
            self.bitmap.to_hexstring(),
            b''.join(parts)
        )
        mac = iso9797_mac(body, self.mackey)
        mac = binascii.hexlify(mac).upper()
        return b'%04d%s%s' % (len(body) + 16, body, mac)


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

    def _decode_value(self, b):
        if self.kind in ('a', 'n', 's', 'an', 'as', 'ns', 'ans'):
            self.value = b

        elif self.kind == 'b':
            self.value = binascii.unhexlify(b)

        else:
            raise TypeError(f'Invalid type: {self.kind}')

    def _encode_value(self):
        if not self.value:
            return b''

        result = None
        if self.kind in ('a', 'n', 's', 'an', 'as', 'ns', 'ans'):
            result = self.value

        elif self.kind == 'b':
            result = binascii.hexlify(self.value)

        else:
            raise TypeError(f'Invalid type: {self.kind}')

        return result

    @abc.abstractmethod
    def parse(self, binary):
        raise NotImplementedError()

    @abc.abstractmethod
    def dumps(self, binary):
        raise NotImplementedError()


class VariableLengthElement(Element):
    def __init__(self, index, kind, size, title, value=None):
        self.header_size = len(str(size))
        super().__init__(index, kind, size, title, value=value)

    def parse(self, binary):
        length = int(binary[:self.header_size])
        blob = binary[self.header_size:self.header_size+length]
        self._decode_value(blob)
        return self.header_size + length

    def dumps(self):
        value = self._encode_value()
        format_ = b'%%0%dd%%s' % self.header_size
        return format_ % (len(value), value)


class  FixedLengthElement(Element):
    def parse(self, binary):
        self._decode_value(binary[:self.size])
        return self.size

    def dumps(self):
        value = self._encode_value()
        pad = self.size - len(value)
        return value + b' ' * pad


ISO8583_LAYOUT = {
    0:  None,  # Reserved for bitmap
    1:  ('b',   'fixed',     64,  'Second Bitmap'),
    2:  ('n',   'variable',  19,  'Primary account number (PAN)'),
    3:  ('n',   'fixed',     6,   'Processing code'),
    11: ('n',   'fixed',     6,   'System trace audit number (STAN)'),
    12: ('n',   'fixed',     12,  'Local transaction time (YYMMDDhhmmss)'),
    22: ('an',  'fixed',     12,  'Point of service Condition'),
    24: ('n',   'fixed',     3,   'Point of service function code'),
    37: ('n',   'fixed',     12,  'Retrieval reference number'),
    39: ('n',   'fixed',     2,   'Response code'),
    41: ('ans', 'fixed',     8,   'Card acceptor terminal identification'),
    42: ('n',   'fixed',     15,  'Card acceptor identification code'),
    43: ('ans', 'variable',  99,  'Card acceptor name/location (1-23 street address, 24-36 city, 37-38 state, 39-40 country)'),
    48: ('ans', 'variable',  999, 'Additional data (private)'),
    64: ('b',   'fixed',     16,  'Message authentication code (MAC)'),
}

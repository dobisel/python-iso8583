from Crypto.Cipher import DES
from Crypto.Util.strxor import strxor

IV = b'\x00' * 8

# http://blog.canalda.net/Post.aspx?IdPost=478
def iso9797_mac(binary, secret):
    # Padding the data to be multiple of 8
    datalen = len(binary)
    binary += b'\x00' * (8 - (datalen % 8))

    # Devide keys into two parts
    secret = binascii.unhexlify(secret)
    assert len(secret) == 16
    firstkey = secret[:8]
    secondkey = secret[8:]

    # Message is divided in 8 byte blocks
    first = None
    for i in range(0, len(binary), 8):
        block = binary[i: i+8]
        if first is not None:
            # A XOR is applied to the result with the next block (it's the CBC)
            block = strxor(block, first)

        # Result is ciphered with first key
        firstcipher = DES.new(firstkey, DES.MODE_CBC, iv=IV)
        first = firstcipher.encrypt(block)

    # To this last result a decryption is applied with the second key
    # (nothing coherent is obtained).
    secondcipher = DES.new(secondkey, DES.MODE_CBC, iv=IV)
    second = secondcipher.decrypt(first)

    # Finally encrypt with K key. The result is the MAC.
    thirdcipher = DES.new(firstkey, DES.MODE_CBC, iv=IV)
    mac = thirdcipher.encrypt(second)
    return binascii.hexlify(mac).upper()


key = b'1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C'
data = \
    b'11006030050008E100011662802314007513' \
    b'5966000076242719052313153821140121124410' \
    b'191431376242701111102000001111102   65\xc8\xc7' \
    b'\xe4\xdf \xe3\xd3\xdf\xe4             \xca\xe5' \
    b'\xd1\xc7\xe4        THRIR00' \
    b'00011234567890070212290073P13006762427CI' \
    b'F012111001209483PHN01109121902288TKT003S' \
    b'FTTOK003000TKR00202'

mac = '72CCB6661787BFE6'

if __name__ == '__main__':
    import binascii

    m = iso9797_mac(data, key).decode()
    print(m)
    print(mac)



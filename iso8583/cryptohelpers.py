
from Crypto.Cipher import DES
from Crypto.Util.strxor import strxor

IV = b'\x00' * 8

# http://blog.canalda.net/Post.aspx?IdPost=478
def iso9797_mac(binary, secret):
    # Padding the data to be multiple of 8
    datalen = len(binary)
    binary += b'\x00' * (8 - (datalen % 8))

    # Devide keys into two parts
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
    return mac




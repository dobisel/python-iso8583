import binascii

from iso8583.cryptohelpers import iso9797_mac


def test_iso9797():
    key = binascii.unhexlify(KEY)
    mac = iso9797_mac(DATA, key)
    assert MAC == binascii.hexlify(mac).upper().decode()


KEY = b'1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C1C'
DATA = \
    b'11006030050008E100011662802314007513' \
    b'5966000076242719052313153821140121124410' \
    b'191431376242701111102000001111102   65\xc8\xc7' \
    b'\xe4\xdf \xe3\xd3\xdf\xe4             \xca\xe5' \
    b'\xd1\xc7\xe4        THRIR00' \
    b'00011234567890070212290073P13006762427CI' \
    b'F012111001209483PHN01109121902288TKT003S' \
    b'FTTOK003000TKR00202'

MAC = '72CCB6661787BFE6'


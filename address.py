#!/usr/bin/env python
# https://pastebin.com/4Lmf25gK
import ctypes
import hashlib
from base58 import encode as base58_encode
 
################################################################################
################################################################################
ssl_library = ctypes.cdll.LoadLibrary('libssl.so')
 
def gen_ecdsa_pair():
    NID_secp160k1 = 708
    NID_secp256k1 = 714
    k = ssl_library.EC_KEY_new_by_curve_name(NID_secp256k1)
 
    if ssl_library.EC_KEY_generate_key(k) != 1:
        raise Exception("internal error?")
 
    bignum_private_key = ssl_library.EC_KEY_get0_private_key(k)
    size = (ssl_library.BN_num_bits(bignum_private_key)+7)//8
    #print("Key size is {} bytes".format(size))
    storage = ctypes.create_string_buffer(size)
    ssl_library.BN_bn2bin(bignum_private_key, storage)
    private_key = storage.raw
 
    size = ssl_library.i2o_ECPublicKey(k, 0)
    #print("Pubkey size is {} bytes".format(size))
    storage = ctypes.create_string_buffer(size)
    ssl_library.i2o_ECPublicKey(k, ctypes.byref(ctypes.pointer(storage)))
    public_key = storage.raw
 
    ssl_library.EC_KEY_free(k)
    return public_key, private_key
 
def ecdsa_get_coordinates(public_key):
    x = bytes(public_key[1:33])
    y = bytes(public_key[33:65])
    return x, y
 
def generate_address(public_key):
    assert isinstance(public_key, bytes)
 
    x, y = ecdsa_get_coordinates(public_key)
   
    s = b'\x04' + x + y
    #print('0x04 + x + y:', ''.join(['{:02X}'.format(i) for i in s]))
 
    hasher = hashlib.sha256()
    hasher.update(s)
    r = hasher.digest()
    #print('SHA256(0x04 + x + y):', ''.join(['{:02X}'.format(i) for i in r]))
 
    hasher = hashlib.new('ripemd160')
    hasher.update(r)
    r = hasher.digest()
    #print('RIPEMD160(SHA256(0x04 + x + y)):', ''.join(['{:02X}'.format(i) for i in r]))
 
    # Since '1' is a zero byte, it won't be present in the output address.
    return '1' + base58_check(r, version=0)
 
def base58_check(src, version=0):
    src = bytes([version]) + src
    hasher = hashlib.sha256()
    hasher.update(src)
    r = hasher.digest()
    #print('SHA256(0x00 + r):', ''.join(['{:02X}'.format(i) for i in r]))
 
    hasher = hashlib.sha256()
    hasher.update(r)
    r = hasher.digest()
    #print('SHA256(SHA256(0x00 + r)):', ''.join(['{:02X}'.format(i) for i in r]))
 
    checksum = r[:4]
    s = src + checksum
    #print('src + checksum:', ''.join(['{:02X}'.format(i) for i in s]))
 
    return base58_encode(int.from_bytes(s, 'big'))
 
def test():
    public_key, private_key = gen_ecdsa_pair()
 
    hex_private_key = ''.join(["{:02x}".format(i) for i in private_key])
    assert len(hex_private_key) == 64
 
    print("ECDSA private key (random number / secret exponent) = {}".format(hex_private_key))
    print("ECDSA public key = {}".format(''.join(['{:02x}'.format(i) for i in public_key])))
    print("Bitcoin private key (Base58Check) = {}".format(base58_check(private_key, version=128)))
 
    addr = generate_address(public_key)
    print("Bitcoin Address: {} (length={})".format(addr, len(addr)))
 
if __name__ == "__main__":
    test()

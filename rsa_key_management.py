import rsa
from pathlib import Path

def loadSecrets():
    pathPrivate = Path('private.pem')
    if not pathPrivate.is_file():
        publicKey, privateKey = rsa.newkeys(512)
        priv_file = open('private.pem', 'w')
        priv_file.write(privateKey.save_pkcs1().decode('utf-8'))
        priv_file.close()
        pub_file = open('public.pem', 'w')
        pub_file.write(publicKey.save_pkcs1().decode('utf-8'))
        pub_file.close()
    with open('private.pem', mode='rb') as priv_file:
        priv_key_data = priv_file.read()
    privateKey = rsa.PrivateKey.load_pkcs1(priv_key_data)
    with open('public.pem', mode='rb') as pub_file:
        pub_key_data = pub_file.read()
    publicKey = rsa.PublicKey.load_pkcs1(pub_key_data)
    return privateKey, publicKey

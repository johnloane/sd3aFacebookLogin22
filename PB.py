from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

server_UUID = "server"
cipher_key = os.getenv("PUBNUB_CIPHER_KEY")
my_channel = "johns-pi-channel-sd3a"

pnconfig = PNConfiguration()

pnconfig.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
pnconfig.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
pnconfig.secret_key = os.getenv("PUBNUB_SECRET_KEY")
pnconfig.uuid = server_UUID
pnconfig.cipher_key = cipher_key
pubnub = PubNub(pnconfig)

def grant_access(auth_key, read, write):
    if read is True and write is True:
        grant_read_and_write_access(auth_key)
    elif read is True:
        grant_read_access(auth_key)
    elif write is True:
        grant_write_access(auth_key)
    else:
        revoke_access(auth_key)


def grant_read_and_write_access(auth_key):
    v = pubnub.grant() \
        .read(True) \
        .write(True) \
        .channels(my_channel) \
        .auth_keys(auth_key) \
        .ttl(60) \
        .sync()
    print("---------------------------------")
    print("---Granting read and write access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("--------------------------------------")

def grant_read_access(auth_key):
    v = pubnub.grant() \
        .read(True) \
        .channels(my_channel) \
        .auth_keys(auth_key) \
        .ttl(60) \
        .sync()
    print("---------------------------------")
    print("---Granting read and write access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("--------------------------------------")

def grant_write_access(auth_key):
    v = pubnub.grant() \
        .write(True) \
        .channels(my_channel) \
        .auth_keys(auth_key) \
        .ttl(60) \
        .sync()
    print("---------------------------------")
    print("---Granting read and write access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("--------------------------------------")


def revoke_access(auth_key):
    v = pubnub.revoke() \
        .channels(my_channel) \
        .auth_keys(auth_key) \
        .sync()
    print("---------------------------------")
    print("---Granting read and write access ---")
    for key, value in v.status.original_response.items():
        print(key, ":", value)
    print("--------------------------------------")

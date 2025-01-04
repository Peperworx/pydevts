from Cryptodome.PublicKey import RSA

key = RSA.generate(2048)
pub = key.public_key().export_key("PEM")
priv = key.export_key("PEM")

with open("certs/id2", "wb+") as f:
    f.write(priv)
with open("certs/id2.pub", "wb+") as f:
    f.write(pub)

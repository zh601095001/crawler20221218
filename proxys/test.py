import kdl

auth = kdl.Auth("o9ufnmidxdwf6xcjurnd1", "qite954mcds6jmcs5xusmwlwshf3mh4c")
client = kdl.Client(auth)
ips = client.get_dps(1, format='json')
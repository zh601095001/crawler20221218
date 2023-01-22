from main import BASE_URL
import requests as rq

res = rq.post(f"{BASE_URL}/db/s",
              params={
                  "collection": "settings"
              },
              json={
                  "_id": "basicSettings"
              }).json()["data"][0]
print(res)
secretId = res["secretId"]
secretKey = res["secretKey"]
print(secretId, secretKey)

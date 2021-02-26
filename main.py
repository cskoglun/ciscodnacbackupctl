import ciscodnacbackupctl
import time
import json

dnac = ciscodnacbackupctl.Api()
#print(dnac.settings)
data = dnac.get()

print(json.dumps(data, indent=4))

'''
for items in data["response"]:
    print("---")
    for k, v in items.items():
        if ("versions" != str(k)) and ("backup_services" != str(k)):
            if "time" in k:
                print("{}\t:{}".format(
                    k,
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(v)
                    )
                    ))
            else:
                print("{}:\t{}".format(
                    k,
                    v
                ))
'''
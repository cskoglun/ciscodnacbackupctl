import ciscodnacbackupctl
import json

dnac = ciscodnacbackupctl.Api()
data = dnac.get()
print(json.dumps(data, indent=4))
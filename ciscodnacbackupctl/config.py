from pathlib import Path
import os
import json
import base64

DNAC_CONFIG = "config.json"
DNAC_CONFIG_PATH = "/.ciscodnac/"
DNAC_FULL_CONFIG_PATH = "{}{}{}".format(Path.home(), DNAC_CONFIG_PATH, DNAC_CONFIG)


class Config:
    def __init__(self):
        self.config = self._check_settings()
        pass

    def _check_settings(self):
        """
        Check Environment cfg
        """
        env_cfg = self.read_env()
        if env_cfg[0] is True:
            return env_cfg[0], env_cfg[1]
        """
        Check local file cfg
        """
        file_cfg = self.read_file()
        if file_cfg[0] is True:
            return file_cfg[0], file_cfg[1]

        return False, "Can't find Cisco DNA Center Config"

    @classmethod
    def read_env(cls):
        """
        Mandatory Environment variables if using Base64
        """
        enviroment_cfg_base64 = "DNAC_CONFIG"
        if enviroment_cfg_base64 in os.environ:
            """ Validate cfg as base64 string """
            data = cls.base64_cfg(operation="decode", data=os.environ["DNAC_CONFIG"])
            if data[0] is True:
                return True, data[1]
            return False, data[1]
        """
        Mandatory Environment variables
        """
        enviroment_cfg = [
            "DNA_CENTER_BASE_URL",
            "DNA_CENTER_USERNAME",
            "DNA_CENTER_PASSWORD",
        ]
        valid_env_cfg = True
        for env in enviroment_cfg:
            if env not in os.environ:
                valid_env_cfg = False
                break

        """
        Validate cfg
        """
        if valid_env_cfg:
            if "DNA_CENTER_VERIFY" in os.environ:
                if "true" in os.environ["DNA_CENTER_VERIFY"].lower():
                    secure = True
                else:
                    secure = False
            else:
                secure = False
            data = {
                "dnac": {
                    "hostname": os.environ["DNA_CENTER_BASE_URL"],
                    "username": os.environ["DNA_CENTER_USERNAME"],
                    "password": os.environ["DNA_CENTER_PASSWORD"],
                    "secure": secure,
                }
            }
            return True, data

        return False, "Environment variables missing"

    @classmethod
    def base64_cfg(cls, **kwargs):
        """ Handle base64 encoding """
        if "encode" in kwargs["operation"]:
            """ Encode json cfg to base64 str """
            data = str(json.dumps(kwargs["data"], indent=4))
            data = base64.b64encode(data.encode("ascii"))
            return True, data.decode("utf-8")
        if "decode" in kwargs["operation"]:
            """ Decode base64 str to json cfg """
            data = kwargs["data"]
            try:
                data == base64.b64encode(base64.b64decode(data)).decode("utf-8")
                data = json.loads(base64.b64decode(data).decode("utf-8"))
            except Exception as e:
                return False, f"Can't decode config ({e})"
            return True, data
        return False, "Unknown base64 error"

    @classmethod
    def read_file(cls):
        """
        Reading local cfg file (json)
        """
        try:
            with open(DNAC_FULL_CONFIG_PATH, "r") as f:
                data = f.read()
                f.close()
                try:
                    """ Read base64 encoded config """
                    data == base64.b64encode(base64.b64decode(data)).decode("utf-8")
                    data = json.loads(base64.b64decode(data).decode("utf-8"))
                except Exception:
                    try:
                        """ Read JSON config (if not base64 encoded) """
                        data = json.loads(data)
                    except Exception:
                        return False, "Can't load json from config"
                return True, data
        except Exception as e:
            return False, f"Can't read config file ({e})"

    @classmethod
    def write(cls, hostname, username, password, secure, **kwargs):
        """
        Write config to local file (json)
        """

        """
        Check if existing folder structure exist
        """
        local_user_path = "{}{}".format(Path.home(), DNAC_CONFIG_PATH)
        if os.path.exists(local_user_path) is False:
            os.makedirs("{}{}".format(Path.home(), DNAC_CONFIG_PATH))

        """
        Don't override existing cfg without {overwrite}
        """
        if (
            "overwrite" not in kwargs["operation"]
            and cls._config_exist(DNAC_FULL_CONFIG_PATH) is True
        ):
            return False, "Config already exist"

        """
        Write json config to file
        """
        data = {
            "dnac": {
                "hostname": hostname,
                "username": username,
                "password": password,
                "secure": secure,
            }
        }
        try:
            with open(DNAC_FULL_CONFIG_PATH, "w") as f:
                f.write(json.dumps(data, indent=4))
            f.close()
            return True, "Success"
        except Exception as e:
            return False, f"Can't update config file ({e})"

    @classmethod
    def _config_exist(cls, path):
        """
        Check if local config file already exist
        """
        if os.path.exists(path):
            return True
        return False

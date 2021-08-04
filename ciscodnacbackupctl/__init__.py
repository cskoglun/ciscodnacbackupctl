import logging
import os
from datetime import timezone, timedelta, datetime
from collections import OrderedDict
import json
import requests
import schedule
from requests.auth import HTTPBasicAuth
import urllib3
from rich.console import Console
import click
from ciscodnacbackupctl.format import Format
from ciscodnacbackupctl.config import Config

author = "Robert Csapo"
email = "rcsapo@cisco.com"
description = "Cisco DNA Center Backup CLI"
repo_url = "https://github.com/cskoglun/ciscodnacbackupctl"
copyright = "Copyright (c) 2020 Cisco and/or its affiliates."
license = "Cisco Sample Code License, Version 1.1"
version = "0.2.6"


class Api:
    def __init__(self, config=False):
        """
        Create client session
        Checking config (env/local file)
        """
        _client = Config()
        if _client.config[0] is False:
            return
        """
        Authenticate towards Cisco DNA Center
        """
        if config is False:
            self.settings = _client.config[1]
            self._auth()
        return

    @classmethod
    def config(cls, hostname, username, password, secure, **kwargs):
        """
        if "read" in kwargs["operation"]:
            return Config.read()
        """
        if "write" in kwargs["operation"]:
            return Config.write(hostname, username, password, secure, **kwargs)

        return

    def _auth(self):
        """Cisco DNA Center Auth"""
        url = "https://{}/dna/system/api/v1/auth/token".format(
            self.settings["dnac"]["hostname"]
        )
        logging.info("Cisco DNA Center Authentication ({})".format(url))
        data = self._request(type="auth", url=url)
        self.settings["dnac"]["token"] = data["Token"]
        return

    def get(self, reverse=False):
        """
        Get Cisco DNA Center Backups
        """
        url = "https://{}{}".format(
            self.settings["dnac"]["hostname"], "/api/system/v1/maglev/backup"
        )

        data = self._request(type="get", url=url)
        data["response"] = sorted(
            data["response"], key=lambda k: k["end_timestamp"], reverse=reverse
        )

        data = self.remove_columns(data)

        return data

    def remove_columns(self, data):

        i = 0
        remove_columns = ["tenantId", "_id", "_version"]
        for backup in data["response"]:
            for k in list(backup):
                if k in remove_columns:
                    del data["response"][i][k]
            data["response"][i] = OrderedDict(sorted(backup.items()))
            i += 1
        return data

    def get_history(self):
        url = "https://{}{}".format(
            self.settings["dnac"]["hostname"], "/api/system/v1/maglev/backup/history"
        )
        data = self._request(type="get", url=url)
        data = self.remove_columns(data)
        return data

    def get_progress(self):
        url = "https://{}{}".format(
            self.settings["dnac"]["hostname"], "/api/system/v1/maglev/backup/progress"
        )
        data = self._request(type="get", url=url)
        data = self.remove_columns(data)
        return data

    def schedule_interval(self, **kwargs):
        """
        Function that returns the correct Schedule function based on which interval day that has been chosen
        """

        intervals = ["weekly", "daily"]

        if kwargs["interval"].lower() == intervals[0]:
            if kwargs["day"].lower() == "monday":
                ret = schedule.every().monday.at(kwargs["time"])
            if kwargs["day"].lower() == "tuesday":
                ret = schedule.every().tuesday.at(kwargs["time"])
            if kwargs["day"].lower() == "wednesday":
                ret = schedule.every().wednesday.at(kwargs["time"])
            if kwargs["day"].lower() == "thursday":
                ret = schedule.every().thursday.at(kwargs["time"])
            if kwargs["day"].lower() == "friday":
                ret = schedule.every().friday.at(kwargs["time"])
            if kwargs["day"].lower() == "saturday":
                ret = schedule.every().saturday.at(kwargs["time"])
            if kwargs["day"].lower() == "sunday":
                ret = schedule.every().sunday.at(kwargs["time"])
        elif kwargs["interval"].lower() == intervals[1]:
            ret = schedule.every().day.at(kwargs["time"])
        else:
            raise Exception

        return ret

    def _request(self, **kwargs):
        urllib3.disable_warnings()
        """
        HTTP Requests
        """

        if "auth" in kwargs["type"].lower():
            url = kwargs["url"]
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = requests.request(
                "POST",
                url,
                auth=HTTPBasicAuth(
                    self.settings["dnac"]["username"],
                    self.settings["dnac"]["password"],
                ),
                headers=headers,
                verify=self.settings["dnac"]["secure"],
            )
            if response.ok:
                data = response.json()
            else:
                if response.status_code == 429:
                    raise Exception(
                        "Can't login to Cisco DNA Center - Too Many Requests - Please try later"
                    )
                raise Exception(
                    "Can't login to Cisco DNA Center ({})".format(response.json())
                )
            return data

        if "get" in kwargs["type"].lower():
            """
            HTTP Method GET
            """
            url = kwargs["url"]
            headers = {
                "X-Auth-Token": self.settings["dnac"]["token"],
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = requests.request(
                "GET",
                url,
                headers=headers,
                verify=self.settings["dnac"]["secure"],
            )
            response.raise_for_status()
            if response.ok:
                data = response.json()
            else:
                if response.status_code == 404:
                    raise Exception("Error: Not found")
                data = response.json()
                print(
                    "Error: ({})".format(data["response"].get("error", "Not Available"))
                )
            return data
        if "delete" in kwargs["type"].lower():
            """
            HTTP Method DELETE
            """
            url = kwargs["url"]
            headers = {
                "X-Auth-Token": self.settings["dnac"]["token"],
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = requests.request(
                "DELETE",
                url,
                headers=headers,
                verify=self.settings["dnac"]["secure"],
            )
            if response.ok:
                data = response.json()
            else:
                if response.status_code == 404:
                    if "response" in response.json():
                        raise Exception(
                            f"Error: Not found ({response.json()['response']})"
                        )
                    raise Exception(f"Error: Not found ({response.text})")
                data = response.json()
                raise Exception(
                    "Error: ({})".format(data["response"].get("error", "Not Available"))
                )
            return data

        if "post" in kwargs["type"].lower():
            url = kwargs["url"]
            headers = {
                "X-Auth-Token": self.settings["dnac"]["token"],
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            response = requests.request(
                "POST",
                url,
                headers=headers,
                verify=self.settings["dnac"]["secure"],
                data=kwargs["payload"],
            )
            if response.ok:
                data = response.json()
            elif response.status_code == 409:
                data = response.json()
            else:
                if response.status_code == 404:
                    if "response" in response.json():
                        raise Exception(
                            f"Error: Not found ({response.json()['response']})"
                        )
                    raise Exception(f"Error: Not found ({response.text})")
                data = response.json()
                raise Exception(
                    "Error: ({})".format(data["response"].get("error", "Not Available"))
                )
            return data

    class CLI:
        def __init__(self):
            self.api = Api()

        def whoami(self, **kwargs):
            if "DNAC_CONFIG" in os.environ:
                self.api.settings["dnac"]["method"] = "environment (encoded)"
            elif "DNA_CENTER_BASE_URL" in os.environ:
                self.api.settings["dnac"]["method"] = "environment"
            else:
                self.api.settings["dnac"]["method"] = "file"
            Format.cli(
                style="standard",
                data=self.api.settings["dnac"],
                source="dict",
            )
            return True

        def list(self, reverse):
            data = self.api.get(reverse=reverse)
            Format.cli(style="standard", data=data, source="list")
            return True

        def history(self):
            data = self.api.get_history()
            Format.cli(style="standard", data=data, source="history")
            return True

        def create(self, name):
            console = Console()
            url = "https://{}{}".format(
                self.api.settings["dnac"]["hostname"], "/api/system/v1/maglev/backup"
            )
            payload = {"description": name}
            payload = json.dumps(payload)

            data = self.api._request(type="post", url=url, payload=payload)

            if type(data["response"]) == str:
                message = data["response"]
                console.print(f"Creating backup with id: {message}")
            else:
                message = data["response"]["error"]
                console.print(f"Error: {message}")

            return True

        def progress(self):
            """
            Cisco DNA Center Backups in Progress
            """
            data = self.api.get_progress()
            Format.cli(style="standard", data=data, source="progress")
            return True

        def delete(self, backup_id):
            console = Console()
            for id in backup_id:
                url = "https://{}{}{}".format(
                    self.api.settings["dnac"]["hostname"],
                    "/api/system/v1/maglev/backup/",
                    id,
                )
                data = self.api._request(type="delete", url=url)

                if "status" in data["response"]:
                    if data["response"]["status"] == "ok":
                        console.print(data["response"]["message"])
                else:
                    console.print("Error: {}".format(data["response"]))

            return True

        def schedule_backup(self, **kwargs):
            name = kwargs["name"]
            url = "https://{}{}".format(
                self.api.settings["dnac"]["hostname"],
                "/api/system/v1/maglev/schedule/backup",
            )
            url_post = url + f"/{name}"
            existing_data = self.api._request(type="get", url=url)

            if not existing_data["response"]:

                if kwargs["action"] == "create":
                    """
                    Create list of number 0-6 representing each weekday. This is needed for the DNAC payload.
                    """
                    weekdays = [
                        "sunday",
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                    ]

                    day_list = kwargs["day"]
                    if len(day_list) >= 1:
                        if day_list[0].lower() == "everyday":
                            _list = []
                            for day in weekdays:
                                _list.append(str(weekdays.index(day)))
                            interval = ",".join(_list)

                        else:
                            days = list(day_list)
                            _list = []

                            for day in days:
                                day = day.lower()
                                _list.append(str(weekdays.index(day)))
                            interval = ",".join(_list)
                    else:
                        raise Exception(
                            "Error in day argument when using schedule_backup()"
                        )

                    time = kwargs["time"]
                    time_list = time.split(":")
                    time_list[0] = int(time_list[0]) - 1
                    """
                    Payload for the POST request
                    """
                    payload = {
                        "schedule": "{} {} * * {}".format(
                            time_list[1], time_list[0], interval
                        ),
                        "json_payload": {
                            "description": kwargs["name"],
                            "appstacks": {"ndp": {}},
                        },
                        "env": {},
                        "url": "http://glusterfs-brick.maglev-system.svc.cluster.local:8080/api/v1/sidecar/backup/1234",
                    }
                    payload = json.dumps(payload)

                    data = self.api._request(type="post", url=url_post, payload=payload)
                    message = "There is now a scheduled backup"
                    data = [message, name, None]
                else:
                    message = "There is no scheduled backup available to delete"
                    data = [message]

            else:
                if kwargs["action"] == "create":
                    message = "There already exists a scheduled backup"
                    name = existing_data["response"][0]["name"]
                    ts = int(existing_data["response"][0]["upcoming_run"])
                    upcoming_time = datetime.utcfromtimestamp(ts).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    data = [message, name, upcoming_time]
                else:
                    if existing_data["response"][0]["name"] == name:
                        data = self.api._request(type="delete", url=url_post)
                        message = f"Backup with the name '{name}' has been deleted"
                        data = [message]
                    else:
                        message = f"No backup with the name '{name}' exists."
                        data = [message]

            return data

        def backup_delta(self, data, days):
            """ Calc delta times to keep backups based on days """
            timenow = datetime.now(tz=timezone.utc)
            keep = days[:-1]
            delta = timenow - timedelta(int(keep))
            delta_ts = datetime.timestamp(delta)
            res = [b for b in data["response"] if b["end_timestamp"] >= delta_ts]
            return res

        def backups_to_delete(self, **kwargs):
            """
            Purge (delete) Cisco DNA Center Backups
            """

            data = self.api.get(reverse=True)

            """
            List of {backup_ids} to keep
            """
            backups_to_keep = []

            if kwargs["incompatible"]:
                """
                Amount of {backup_ids} that is compatible
                """

                for backup in data["response"]:
                    if backup["compatible"].upper() == "TRUE":
                        backups_to_keep.append(backup)
            elif "d" in str(kwargs["keep"]):
                """
                Amount of {backup_ids} to keep based on days
                """
                backups = self.backup_delta(data, kwargs["keep"])
                for backup in backups:
                    backups_to_keep.append(backup)
            else:
                """
                Amount of {backup_ids} to keep
                """
                i = 0
                for backup in data["response"]:
                    if i != int(kwargs["keep"]):
                        backups_to_keep.append(backup)
                        i += 1
                    else:
                        break
            """
            Removing {backup_ids} in {backups_to_keep} from data["response"]
            """
            for backup in backups_to_keep:
                data["response"].remove(backup)

            return data

        def purge(self, keep, incompatible, force):
            """
            Purge (delete) Cisco DNA Center Backups
            """
            console = Console()
            data = self.backups_to_delete(
                incompatible=incompatible, keep=keep, force=force
            )  # backups_to_delete

            if len(data["response"]) == 0:
                console.print("No backup to delete")
                return False
            else:
                backup_id_to_delete = []
                for item in range(0, len(data["response"])):
                    backup_id_to_delete.append(data["response"][item]["backup_id"])

            if force is True:
                """
                Displayed deleted backups
                """
                for i in range(0, len(backup_id_to_delete)):
                    self.delete(backup_id_to_delete[i])
                Format.cli(style="standard", data=data, source="list")
                console.print(
                    f"Success: Backups ({len(data['response'])}) deleted", style="green"
                )
                return True
            else:
                """
                Display candidates to be deleted
                """
                Format.cli(style="standard", data=data, source="list")

                """
                Confirm action to delete
                """
                confirm = click.prompt(
                    click.style(
                        "Warning: Confirm if you want to delete these backups (y/n)",
                        fg="red",
                    ),
                    type=bool,
                )
                if not confirm:
                    console.print("Warning: Purge aborted", style="red")
                    return True

                """
                Purging backups with force
                """
                console.print(
                    "Deleting... (this could take a while - as it's synchronous API calls)",
                    style="red",
                )

                data = self.backups_to_delete(
                    incompatible=incompatible, keep=keep, force=True
                )

                backup_id = [x["backup_id"] for x in data["response"]]
                self.delete(backup_id)
                console.print(
                    f"Success: Backups ({len(data['response'])}) deleted {backup_id}",
                    style="green",
                )
                return True

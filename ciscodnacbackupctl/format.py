import time
import rich
from hurry.filesize import size
from tabulate import tabulate


class Format:
    def __init__(self):
        pass

    @staticmethod
    def cli(**kwargs):
        """
        Handle in coming CLI Output Style
        """
        if "standard" in kwargs["style"]:
            return Format._default(**kwargs)
        return "Error"

    @classmethod
    def _default(cls, **kwargs):
        table = []
        columns = []
        rows = []
        if kwargs["source"] == "dict":
            columns, rows = cls.__dict(kwargs["data"])
            table.append(rows)

        elif kwargs["source"] == "list":
            for d in kwargs["data"]["response"]:
                columns, rows = cls.__list(d)
                table.append(rows)

        elif kwargs["source"] == "history":
            for d in kwargs["data"]["response"]:
                __columns, __rows = cls.__history(d)
                
                """ Don't override existing table """
                if len(__columns) != 0:
                    columns = __columns
                if len(__rows) != 0:
                    rows = __rows
                
                table.append(rows)

        elif kwargs["source"] == "progress":
            for d in kwargs["data"]["response"]:
                columns, rows = cls.__progress(d)
                table.append(rows)

        if len(rows) != 0:
            console = rich.get_console()
            console.print(
                tabulate(
                    table,
                    columns,
                    tablefmt="plain",
                    stralign="left",
                    disable_numparse=True,
                ),
                soft_wrap=True,
            )
            return True
        return False

    @classmethod
    def __dict(cls, data):
        columns = []
        rows = []
        for k, v in data.items():
            if k.lower() != "token":
                columns.append(k.upper())
                rows.append(v)
        return columns, rows

    @classmethod
    def __list(cls, d):
        excluded_columns = [
            "versions",
            "backup_services",
            "compatible_error",
        ]
        columns = []
        rows = []
        for k, v in d.items():
            if k not in excluded_columns:
                columns.append(k.upper())
                if "time" in k:
                    v = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v)))
                if "size" in k:
                    v = str(size(v))
                if "percentage" in k:
                    v = "{}%".format(int(v))
                if "_version" in k:
                    v = str(v)
                rows.append(v)
        return columns, rows

    @classmethod
    def __history(cls, d):
        included_columns = [
            "backup_id",
            "start_timestamp",
            "status",
            "operation",
            "id",
            "progress_in_percentage",
            "description",
            "backup_size",
        ]
        columns = []
        rows = []
        if "PENDING" not in d["status"]:
            for k, v in d.items():
                if k in included_columns:
                    columns.append(k.upper())
                    if "time" in k:
                        v = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v)))
                    if "size" in k:
                        v = str(size(v))
                    if "percentage" in k:
                        v = "{}%".format(int(v))
                    rows.append(v)
        return columns, rows

    @classmethod
    def __progress(cls, d):
        included_columns = [
            "backup_id",
            "start_timestamp",
            "status",
            "operation",
            "id",
            "progress_in_percentage",
            "description",
            "backup_size",
        ]
        columns = []
        rows = []
        for k, v in d.items():
            if k in included_columns:
                columns.append(k.upper())
                if "time" in k:
                    v = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v)))
                if "size" in k:
                    v = str(size(v))
                if "percentage" in k:
                    v = "{}%".format(int(v))
                rows.append(v)
        return columns, rows

import time
import click
import ciscodnacbackupctl
import rich
from rich.console import Console
import daemonocle
import schedule
from ciscodnacbackupctl import Format
from ciscodnacbackupctl import Config

# Need to pass the KEEP variable to daemon worker
KEEP = 3


def app_daemon(
    interval="daily", incompatible=False, keep=KEEP, day="monday", hour="23:00"
):
    global KEEP
    ctl = ciscodnacbackupctl.Api()
    interval = interval.lower()
    _day = day.lower()
    _time = hour.lower()
    """
    job() function makes sure to purge the backups when called upon
    """

    def job():
        console = Console()
        ctl = ciscodnacbackupctl.Api()
        cli = ctl.CLI()
        force = True
        try:
            purge = cli.purge(keep=keep, incompatible=incompatible, force=force)
        except Exception as error_msg:
            console.print(
                "Cisco DNA Center isn't available - {}".format(error_msg), style="green"
            )
            pass

    schedule_function = ctl.schedule_interval(
        interval=interval, day=_day, time=_time
    ).do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
    return

@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    pass


@cli.command("daemon", help="{}".format(daemonocle.Daemon.list_actions()))
@click.option("--detach/--debug", default=True, help="Attach and debug")
@click.option(
    "--keep", type=str, default=3, help="Amount of backups to keep (default 3)"
)
@click.argument("command", nargs=1)
@click.pass_context
def daemon(ctx, detach, keep, command):
    global KEEP
    KEEP = keep
    daemon = daemonocle.Daemon(
        worker=app_daemon,
        pid_file="/tmp/ciscodnacbackupctl.pid",
        detach=detach,
    )
    if command.lower() in daemonocle.Daemon.list_actions():
        if command.lower() == "status":
            data = daemon.get_status()
            output = Format.cli(style="standard", data=data, source="dict")
            return
        daemon.do_action(command)
        return
    click.echo(ctx.get_help())
    return


@cli.command("whoami")
@click.option("--cfg", is_flag=True, help="Read local cfg")
@click.pass_context
def whoami(ctx, cfg):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.whoami(cfg=cfg)
    return


@cli.command("config")
@click.option("--env/--no-env", default=False)
@click.option("--hostname", required=True)
@click.option("--username", required=True)
@click.option("--password", required=True)
@click.option("--secure", is_flag=True, help="Secure HTTPS towards Cisco DNA Center")
@click.option(
    "--encode", is_flag=True, help="Encode Cisco DNA Center config to Base64 string"
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Writes over the existing config for Cisco DNA Center",
)
@click.pass_context
def config(ctx, env, hostname, username, password, secure, overwrite, encode):
    ctl = ciscodnacbackupctl.Api(config=True)
    console = Console()
    if env:
        if encode:
            data = {
                "dnac": {
                    "hostname": hostname,
                    "username": username,
                    "password": password,
                    "secure": secure,
                }
            }
            data = Config.base64_cfg(operation="encode", data=data)
            environments = {
                "DNAC_CONFIG": data[1],
            }
        else:
            environments = {
                "DNA_CENTER_BASE_URL": hostname,
                "DNA_CENTER_USERNAME": username,
                "DNA_CENTER_PASSWORD": password,
                "DNA_CENTER_VERIFY": secure,
            }
        console.print(
            "Environment Settings Generated (copy paste below)", style="green"
        )
        for k, v in environments.items():
            console.print("export {}={}".format(k, v), soft_wrap=True)
    else:
        """ TODO move to config.py """
        config = ciscodnacbackupctl.Api.config(
            hostname=hostname,
            username=username,
            password=password,
            secure=secure,
            operation="write",
        )

        if "Config already exist" in str(config[1]) and config[0] is False:
            if overwrite is False:
                confirm = click.prompt(
                    click.style(
                        "Warning: Config already exist ({}), are you sure you want override? (y/n)".format(
                            ciscodnacbackupctl.config.DNAC_FULL_CONFIG_PATH
                        ),
                        fg="red",
                    ),
                    type=bool,
                )
            if not confirm:
                console.print("Warning: Config aborted", style="red")
                return
            else:
                config = ciscodnacbackupctl.Api.config(
                    hostname=hostname,
                    username=username,
                    password=password,
                    secure=secure,
                    operation="overwrite",
                )
        console.print(
            "Success: Config created ({})".format(
                ciscodnacbackupctl.config.DNAC_FULL_CONFIG_PATH
            ),
            style="green",
        )
    return


@cli.command("list")
@click.option("--reverse/--no-reverse", default=False)
@click.pass_context
def list(ctx, reverse):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.list(reverse)
    return


@cli.command("progress")
@click.pass_context
def progress(ctx):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.progress()
    return


@cli.command("history")
@click.pass_context
def history(ctx):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.history()
    return


@cli.command("create")
@click.option("--name", required=True, help="Name of backup")
@click.pass_context
def create(ctx, name):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.create(name)
    return


@cli.command("delete")
@click.option("--backup_id", required=True, is_flag=True)
@click.argument('id', nargs=-1)
#@click.argument("--backup_id", required=True, nargs=-1)
@click.pass_context
def delete(ctx, backup_id, id):
    cli = ciscodnacbackupctl.Api.CLI()
    cli.delete(id)
    return


@cli.command("schedule_backup")
@click.option(
    "--action",
    "-a",
    required=True,
    help="Type "
    "Create"
    " or "
    "Delete"
    " to either create or delete scheduled backup",
    type=str,
)
@click.option("--name", "-n", required=True, help="Name of backup", type=str)
@click.option(
    "--day",
    "-d",
    multiple=True,
    help="Type which day you want backup or "
    "everyday"
    " if you want everyday backup.",
    default=["everyday"],
)
@click.option(
    "--hour",
    "-t",
    required=False,
    default="23:00",
    type=str,
    help="At what time hh:mm should the backup be created? Default is 23:00",
)
@click.pass_context
def schedule_backup(ctx, action, name, day, hour):
    action = action.lower()
    cli = ciscodnacbackupctl.Api().CLI()
    console = rich.get_console()
    data = cli.schedule_backup(name=name, day=day, time=hour, action=action)
    print(data)

    # TODO move this part to CLI class
    if action.lower() == "create":
        if "now" in data[0]:
            console.print(f"{data[0]} with name '{data[1]}'", style="green")
        else:
            console.print(f"{data[0]} with name '{data[1]}' ", style="red")
    else:
        if "no" in data[0]:
            console.print(f"{data[0]}", style="red")
        else:
            console.print(f"{data[0]}", style="red")


@cli.command("purge")
@click.option(
    "--keep", type=str, default=3, help="Amount of backups to keep (default 3)"
)
@click.option("--incompatible", is_flag=True, help="Remove incompatible backups")
@click.option("--force", is_flag=True, help="No interactive prompt to confirm purge")
@click.pass_context
def purge(ctx, keep, incompatible, force):
    cli = ciscodnacbackupctl.Api().CLI()
    purge = cli.purge(keep=keep, incompatible=incompatible, force=force)


@cli.command("schedule_purge")
@click.option(
    "--interval", "-i", required=True, help=" " "daily" " or " "weekly" " ", type=str
)
@click.option("--incompatible", is_flag=True, help="Remove incompatible backups")
@click.option(
    "--keep",
    "-k",
    required=False,
    default=3,
    type=str,
    help="Amount of backups to keep, default is 3",
)
@click.option(
    "--day",
    "-d",
    required=False,
    default="monday",
    type=str,
    help="Day to delete backups on",
)
@click.option(
    "--hour",
    "-h",
    required=False,
    default="23:00",
    type=str,
    help="Time to delete backups HH:MM, default is 23:00",
)
@click.pass_context
def schedule_purge(ctx, interval, incompatible, keep, day, hour):
    ctl = ciscodnacbackupctl.Api()
    cli = ctl.CLI()
    console = rich.get_console()

    interval = interval.lower()
    _day = day.lower()
    _time = hour.lower()

    """
    job() function makes sure to purge the backups when called upon
    """

    def job():
        force = True
        try:
            purge = cli.purge(keep=keep, incompatible=incompatible, force=force)
        except Exception as error_msg:
            console.print(
                "Cisco DNA Center isn't available - {}".format(error_msg), style="green"
            )
            pass

    """
    Print out confirmation that the backup is scheduled
    """
    # TODO move this part to class CLI
    if interval.lower() == "daily":
        click.echo(
            click.style(f"\nYour backups will be deleted daily at {_time}", fg="green")
        )
    else:
        click.echo(
            click.style(
                f"\nYour backups will be deleted {_day}s at {_time}", fg="green"
            )
        )

    schedule_function = ctl.schedule_interval(
        interval=interval, day=_day, time=_time
    ).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    cli()
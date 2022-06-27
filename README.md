# ciscodnacbackupctl
![PyPI](https://img.shields.io/pypi/v/ciscodnacbackupctl)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ciscodnacbackupctl)
![GitHub last commit](https://img.shields.io/github/last-commit/cskoglun/ciscodnacbackupctl)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/cskoglun/ciscodnacbackupctl)
![GitHub issues](https://img.shields.io/github/issues/cskoglun/ciscodnacbackupctl)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/cskoglun/ciscodnacbackupctl)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/cskoglun/ciscodnacbackupctl)
![GitHub Repo stars](https://img.shields.io/github/stars/cskoglun/ciscodnacbackupctl?style=social)  

Cisco DNA Center Backup Tool (as a CLI tool)  
_Helps you to manage your backups and purge previous backups and also incompatible backups (between versions)_

---

## Why?

In the current state of Cisco DNA Center, it's possible to schedule and perform backups.  
But there's no automated way of purging backups and users are asked to purge backups through the Web UI
```ciscodnacbackupctl``` offers a CLI interface to handle your backups from your terminal or as a daemon/docker container

## Features
- [x] List all backups
- [x] History/On-going backups
- [x] Delete backup
- [x] Purge backups (all or just incompatible ones)
- [x] Schedule backups
    - [x] New Backup
    - [x] Purge
- [x] Debug HTTP

## Installation

```pip install ciscodnacbackupctl```

### Config
```
ciscodnacbackupctl config --help
Usage: ciscodnacbackupctl config [OPTIONS]

Options:
  --env / --no-env
  --hostname TEXT   [required]
  --username TEXT   [required]
  --password TEXT   [required]
  --secure          Secure HTTPS towards Cisco DNA Center
  --encode          Encode Cisco DNA Center config to Base64 string
  --overwrite       Writes over the existing config for Cisco DNA Center
  --help            Show this message and exit.
```

```
Usage: ciscodnacbackupctl [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --version             Show the version and exit.
  --help                Show this message and exit.

Commands:
  config
  create
  daemon           ['start', 'stop', 'restart', 'status']
  delete
  history
  list
  progress
  purge
  schedule_backup
  schedule_purge
  whoami
```

## Technologies & Frameworks Used

**Cisco Products & Services:**

- Cisco DNA Center

**Tools & Frameworks:**

- rich
- tabulate
- hurry
- click
- schedule
- daemonocle

## Daemon or Docker
This makes it possible to automatically purge old backups daily

### Daemon
```ciscodnacbackupctl daemon start --keep 3```

### Docker Support
Generate Cisco DNA Center config as Base64 string  
```docker run -it --rm robertcsapo/ciscodnacbackupctl config --env --hostname <dnachost> --username <username> --password <password> --encode```

Use the ENV to exucute commands

List
```
docker run -it --rm \
-e DNAC_CONFIG=ewogICAgImRuYWMiOiB7CiAgICAgICAgImhvc3RuYW1lIjogInNhbXBsZS5ob3N0LnRsZCIsCiAgICAgICAgInVzZXJuYW1lIjogImRuYWMiLAogICAgICAgICJwYXNzd29yZCI6ICJwYXNzdzByZCIsCiAgICAgICAgInNlY3VyZSI6IGZhbHNlCiAgICB9Cn0 \
robertcsapo/ciscodnacbackupctl \
list
```
Purge
```
docker run -it --rm \
-e DNAC_CONFIG=ewogICAgImRuYWMiOiB7CiAgICAgICAgImhvc3RuYW1lIjogInNhbXBsZS5ob3N0LnRsZCIsCiAgICAgICAgInVzZXJuYW1lIjogImRuYWMiLAogICAgICAgICJwYXNzd29yZCI6ICJwYXNzdzByZCIsCiAgICAgICAgInNlY3VyZSI6IGZhbHNlCiAgICB9Cn0 \
robertcsapo/ciscodnacbackupctl \
purge
```

## Authors & Maintainers

Smart people responsible for the creation and maintenance of this project:

- Christina Skoglund <cskoglun@cisco.com>
- Robert Csapo <rcsapo@cisco.com>

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).

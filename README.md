# ciscodnacbackupctl

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
ciscodnacbackupctl --help
Usage: ciscodnacbackupctl [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

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

### Docker Support Coming soon

## Authors & Maintainers

Smart people responsible for the creation and maintenance of this project:

- Christina Skoglund <cskoglun@cisco.com>
- Robert Csapo <rcsapo@cisco.com>

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).

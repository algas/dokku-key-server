# Dokku SSH Public Key Management Web Server

Simple dokku key management server written in python tornado.
If you need to add ssh keys of some users for your dokku, this app may help you.

## Requirements

* Dokku or Dokku-Alt

## Installing Dokku

See [dokku](https://github.com/progrium/dokku) or [dokku-alt](https://github.com/dokku-alt).
Run the following commands on your dokku host to install dokku.

* dokku
    $ wget -qO- https://raw.github.com/progrium/dokku/master/bootstrap.sh | sudo bash

* dokku-alt
    $ sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/dokku-alt/dokku-alt/master/bootstrap.sh)"

## Set your first key

Run the following commands on your localhost.

    $ ssh-keygen -t rsa  # if you have no ssh keys
    $ scp ~/.ssh/id_rsa.pub your-dokku-host:
    $ ssh your-dokku-host
    $ cat id_rsa.pub | sudo sshcommand acl-add dokku (your_name)

## Deploying

Deploy dokku-key-server.

    $ git clone git@github.com:algas/dokku-key-server.git
    $ cd dokku-key-server
    $ git remote add dokku dokku@your-dokku-host:dokku-key-server
    $ git push dokku master

## Configuring

Configure shared volume.

    $ ssh your-dokku-host
    $ sudo chown dokku:dokku /home/dokku/.volumes # You should run it as a root user
    $ sudo dokku volume:create ssh-volume /home/dokku/.ssh:/home/dokku/.ssh # You should run it as a root user
    $ dokku volume:link dokku-key-server ssh-volume

## Undeploying

    $ dokku delete dokku-key-server

## License

MIT


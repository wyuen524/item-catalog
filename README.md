# item-catalog

### Prerequisites

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
* [Udacity VM](https://github.com/udacity/fullstack-nanodegree-vm)

### How to run

Clone the Udacity fullstack-nanodegree-vm

```
git clone https://github.com/udacity/fullstack-nanodegree-vm.git
```

Build the Vagrant VM

```
cd /vagrant
vagrant up (wait until setup is complete)
vagrant ssh
```

Replace the existing catalog directory with files from this repo

Create and load data into the database

```
cd /vagrant/catalog
python database_setup.py
python load_db.py
```

To start the application

```
cd /vagrant/catalog
python application.py
```

### API endpoints

These are the endpoints you can reach by typing in the url in the browser directly.

```
Category
Create: localhost:8000/weapons/new
Read: localhost:8000/weapons/<int:weapon_class_id>/
Update: localhost:8000/weapons/<int:weapon_class_id>/edit
Delete: localhost:8000/weapons/<int:weapon_class_id>/delete
```

```
Item
Create: localhost:8000/weapons/<int:weapon_class_id>/new
Read: localhost:8000/deatails/<int:weapon_id>/
Update: localhost:8000/weapons/<int:weapon_class_id>/<int:weapon_id>/edit
Delete: localhost:8000/weapons/<int:weapon_class_id>/<int:weapon_id>/delete
```

```
To see entire catalog in JSON:
localhost:8000/weapons/catalog.json

To see a single category in JSON:
localhost:8000/weapons/<int:weapon_class_id>/json

To see a single item in JSON:
http://localhost:8000/details/<int:weapon_id>/json
```

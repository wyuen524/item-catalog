# item-catalog

### Prerequisites

Vagrant
Virtual Box

### How to run

```
cd to directory with the Vagrantfile
vagrant up
vagrant ssh

copy catalog directory to /vagrant
cd /vagrant/catalog
python application.py
```

### API endpoints

```
Category
Create: localhost:8000/weapons/new
Read: localhost:8000/weapons/<int:weapon_class_id>/ or localhost:8000/weapons/<int:weapon_class_id>/list
Update: localhost:8000/weapons/<int:weapon_class_id>/edit
Delete: localhost:8000/weapons/<int:weapon_class_id>/delete
```

```
Item
Create: localhost:8000/weapons/<int:weapon_class_id>/new
Read: localhost:8000/weapons/<int:weapon_class_id>/ or localhost:8000/weapons/<int:weapon_class_id>/list
Update: localhost:8000/weapons/<int:weapon_class_id>/<int:weapon_id>/edit
Delete: localhost:8000/weapons/<int:weapon_class_id>/<int:weapon_id>/delete
```

```
To see entire catalog in JSON:
localhost:8000/weapons/catalog.json

To see a single category in JSON:
localhost:8000/weapons/<int:weapon_id>/json
```

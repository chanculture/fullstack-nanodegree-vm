Christopher Chan: Full Stack Web Developer Nanodegree
==========

Project 4: Item Catalog
==========
As of April 25, 2016 Item Catalog is now Project 4 (previously project 3).

Requirements
==========

* Python 2.7.6 or greater
* Flask 0.9

Instructions
==========
Clone the git repository located at:
https://github.com/chanculture/fullstack-nanodegree-

The files necessary for this project are located /vagrant/catalog
within the cloned git repository.

Assuming you follow the instructions from the project to use a
Vagrant Virtual Machine, follow these steps:

1.  Run database_setup.py to create and configure the project database,
    called itemcatalog.db.  "python database_setup.py"
2.  Run database_populate.py to create some categories and initial data.
    "python database_populate.py"
3.  Start the server. "python project.py", this file is configured for port 8000.
4.  Navigate to http://localhost:8000/ to view the project.

OAuth2 Providers
==========
* Google
* Facebook


API Endpoints
==========
/catalog/JSON
------------------
Lists all items in catalog

/catalog/<string:categoryname>/JSON
------------------
Lists all items from a specified category
* categoryname: The name of the category

/catalog/<string:categoryname>/<string:itemname>/JSON
------------------
Returns a particular item
* categoryname: The name of the category
* itemname: The name of the item

/catalog/categories/JSON
------------------
Returns a list of valid categories


Content
==========
* fb_client_secrets.json
Client secrets for facebook oauth2 functionality
* g_client_secrets.json
Client secrets for google oauth2 functionality

EXTRA
==========
* Ability to add images to items
Images are stored on the server in ./static/images
Item images (1 per item is allowed) are renamed to the item's
database id and keep the original extension type of the file
uploaded.  The image files types allowed are 'png', 'jpg',
'jpeg', and 'gif'.

License
==========
Copyright Christopher Chan

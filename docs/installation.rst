Installation
============

Prerequisites
---------------------------------------

* Apache
* MySQL
* Python
* Pip

Install the latest revision from GitHub
---------------------------------------
Run the following command to install the latest version from GitHub::

    pip install git+https://github.com/KarrLab/test_history_server.git#egg=test_history_server

Configure the package
---------------------------------------

1. Create a MySQL database
2. Edit the site and database configuration in `/path/to/web-server/test_history_server/test_history_server/site/settings.py`
3. Setup the database::

      cd /path/to/web-server/test_history_server/test_history_server/site
      python manage.py makemigrations core
      python manage.py migrate

4. Edit the server configuration in `/path/to/web-server/test_history_server/test_history_server/site/wsgi.py`

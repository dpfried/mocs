# Maps of Computer Science
MoCS is a system to visualize topics from the [DBLP](http://dblp.uni-trier.de/) database of research papers. A [live version of this code](http://mocs.cs.arizona.edu) is available, including a description of the algorithms implemented and demonstrations of the maps rendered by the system, and a research paper describing how the system works.

## License
Code is released under the [MIT License](MIT-LICENSE.txt).

## Setup for command line interface
Allows creation of basemaps through [`lib/cli_interface.py`](lib/cli_interface.py).

1. Install the python dependencies listed in requirements.txt. Using pip:
```
pip install -r requirements.txt
```

2. Install [graphviz](http://graphviz.org/Download..php)

3. Download NLTK corpora by running
```
python -m nltk.downloader brown langid
```

4. Rename `lib/mocs_configTEMPLATE.py` to `lib/mocs_config.py`
Edit this file if your graphviz binaries or nltk data are in a non-standard location, or if you want the document database to be stored in a non-SQLite database. If this file is not edited, the DBLP data will be stored in a SQLite database called `mocs.db` in the project root.

5. Run `./build_dblp.sh` to create the database and load it with data downloaded from DBLP.

## Setup for webserver
Allows creation of basemaps and heatmaps

1. Install [rabbitmq](http://www.rabbitmq.com/download.html).

2. Set up Django settings (optional).
Edit `DATABASES`, `SECRET_KEY`, and `ADMINS` in `settings.py`, or create a new file
`local_settings.py` containing these parameters.
If DATABASES is not edited, the DBLP data will be stored in a SQLite database called `mocs.db` in the project root (which is by default the same database the DBLP data is stored in).

3. Create Django databases:
```
./manage.py syncdb
```

4. Run the server:
```
./manage.py celeryd
./manage.py runserver
```

5. Access the map interface at `http://localhost:8000/maps/query/`

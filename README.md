# **The Worlds Heritrash**
## Video Demo:  https://youtu.be/mCjw80JF0Pg
## Description:
The idea for this Web Applikation came while being on a hike and literally passing so much trash & litter, that I was wondering how places that are even positioned in a **world heritage** environment will survive over the next years. As not all trash can (or would want to) be removed by the respective "finder" right away, the idea of a simple mapping platform was born allowing user to keep track of trash in their most favorite places and engage / raise awareness for the negative impact trash on the environment.

Note: Files are **NOT** being stored in static folder. Need to create /img folder - see app.py

### Core functionalities of the Web-App are:
- dynamic map interaction (based on leaflet with custom marker elements)
- Simple 3-click trash reporting logic
- capturing images from build-in camera (environment facing)
- captering Geo-Position based on either location or manual marker selection
- possibility to view trash reports without registration
- selection of existing trash reports and cleaning up
- easy UI (all unnecessary buttons / interaction elements of the UI are removed on purpose)

### The basic files / folder structure:
- **/img**
    - /cap (path to images captured from video stream through getUserMedia)
    - /uploads (path to all manually uploaded files)
- **/static**
    - /favicon (all the various favicons (ico / png))
    - /js (all javascript code that is not implemented in html pages)
    - /map_icon (folder for all custom map marker graphics)
    - styles.css (stylesheet for this project)
- **/templates**
    - capture.html (used when reporting trash)
    - clean.html (report details of cleaned up place)
    - cleanup.html (used when being in cleaning up process)
    - imprint.html (imprint, description and contact details)
    - index.html (main map)
    - layout.html (flasks basic layout serving the other templates)
    - login.html (login page)
    - register.html (registration page)
    - trash.html (template finished trash report details)
- **/**
    - app.py (flask web server with config, custom routes and jinja setup )
    - helpers.py (some helpers for login)
    - Readme.md (this file)
    - requirement.txt (basic requirements for this project)
    - trash.db (main database)
        - table users (holding user information e.g. name + pw-hash)
        - table img (holding image information through upload / capture e.g. path, data, reportID,...)
        - table trash (holding all information about trash/clean reports)


### Languages, frameworks and other components used:
[![Tech stack](https://skills.thijs.gg/icons?i=py,css,html,js,jquery,sql&theme=dark)](https://skills.thijs.gg)
- Python / flask framework, Jinja
- SQL (sqlite3)
- Javascript
- HTML5/CSS
- bootstrap
- JQuery
- Dropzone
- Leaflet
- Openstreetmap

### Future ideas
There are plenty of functional and technical ideas on how this project could still be improved e.g.:
- [ ] flask PWA framework to allow stand-alone installation
- [ ] rewarding system for users
- [ ] Offline availability of static file components
- [ ] notification system outside the application
- [ ] modification of the map filter to allow dynamic transistion between grayscale and color
- ...

### Credits and thanks:
- **Everyone** from the developers community that I might have forgotten to mention in person
- [Stackoverflow](https://stackoverflow.com/) for always having the right answer from some genius availabe
- [Miguel Grinberg](https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask) for his ideas on filehandling on flask
- [CS50-Team (David, Doug, Brian,...)](https://cs50.harvard.edu/)
- [Dulan fomr enlear](https://enlear.academy/working-with-geo-coordinates-in-mysql-5451e54cddec) for his ideas on mysql and Geo-Coordinates

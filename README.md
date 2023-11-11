# KDM Scripts
This package contains scripts for helping to book-keep and manage
Kindom Death: Monster board game campaigns.

This relies on the bookkeeping for your campaign being done throuh the
`Scribe for KDM` mobile app. Which can save and load backup `JSON` files
which are read, manipulated and saved by this package - so you can load them
back into the app.

# Install
- Install python.
- Clone this repo.
- Create a virtual environment at the root of the repo
    - ```python3 -m venv venv```
- Install requirements
    - ```.\venv\Scripts\activate```
    - ```pip install -r requirements.txt```
- Add kdm project to the venv site packages.
    - Add a `kdm.pth` file under `venv\Lib\site-packages` that just contains the absolute path to the git repo
- Optionally you can add the CLI directory to your `PATH` environment variable.

# Use
The CLI is in the form of a series of `bat` scripts prefixed with `kdm-`. If you've added 
the `bin` directory to your `PATH`, just use `kdm-` + tab to cycle your options.

e.g. `kdm-make-babies --help`
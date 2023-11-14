# KDM Scripts
This package contains scripts for helping to book-keep and manage
Kindom Death: Monster board game campaigns.

This relies on the bookkeeping for your campaign being done throuh the
`Scribe for KDM` mobile app. Which can save and load backup `JSON` files
which are read, manipulated and saved by this package - so you can load them
back into the app.

# Install
- Install python.
- Install git.
- Clone this repo.
- Run the bat scripts in the `bin` directory to use. Optionally you can add the `bin` directory to your `PATH` environment variable.
    - **Note:** The first time you run a command, it will create a virtual environment and install requirements automatically.

# Use
The CLI is in the form of a series of `bat` scripts prefixed with `kdm-`. If you've added 
the `bin` directory to your `PATH`, just use `kdm-` + tab to cycle your options.

e.g. `kdm-make-babies --help`
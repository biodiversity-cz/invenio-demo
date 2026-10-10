# Static Images

This folder contains **static image assets** for the repository UI.  
These files are served directly as part of the web application’s static files.

## Usage

- Place logos, favicons, icons, and other project-specific images here.  
- **Site header logo:** name the file `theme-logo.png` (see `THEME_LOGO` in config). Files here are copied automatically when you run `./run.sh run`, `./run.sh install`, or `./run.sh upgrade` (see `scripts/sync_static_images.sh`). If you start the app with `.venv/bin/invenio run` directly, run that script once or copy manually into `.venv/var/instance/static/images/`.
- Reference them in templates or stylesheets using the static path, for example:

  ```jinja
  <img src="{{ url_for('static', filename='images/my-logo.png') }}" alt="Site logo">

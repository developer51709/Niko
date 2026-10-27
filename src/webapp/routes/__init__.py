"""Flask route modules.

Every module here registers its routes on the shared application from
``webapp.app`` (``webapp.server``) and pulls the names it needs from that
module's namespace with a ``globals().update(vars(_server))`` snapshot at the
top of the file.

``webapp/__init__.py`` imports them in order after the application is set up,
so importing this package on its own does nothing.
"""

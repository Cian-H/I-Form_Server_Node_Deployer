#!/usr/bin/env python

def main() -> None:
    from . import config
    config.update_config("cli")
    from .node_deployer import app
    app()

def debug():
    from . import config
    config.update_config("debug")
    from .node_deployer import app
    
    # Below, we set the default value of the debug flag
    # for the base function of each command to True
    def unwrap(f):
        if hasattr(f, "__wrapped__"):
            return unwrap(f.__wrapped__)
        else:
            return f

    for c in app.registered_commands:
        f = unwrap(c.callback)
        defaults = list(f.__defaults__)
        defaults[-1] = True
        f.__defaults__ = tuple(defaults)
    
    app()

if __name__ == "__main__":
    main()
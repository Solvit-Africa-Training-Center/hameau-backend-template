#!/usr/bin/env python

import os
import sys


def main():
<<<<<<< HEAD
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
=======
   
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
>>>>>>> cfe19b0ec02c92b4fe0f0faf3029d5635f0e4d98
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

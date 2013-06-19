'''
Copyright [2013] [Konstantin Renner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters':
    {
     'verbose': {'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'},
     'simple': {'format': '%(levelname)s %(message)s'},
     },
    'handlers':
    {
     'console':
     {
      'level': 'DEBUG',
      'class': 'logging.StreamHandler',
      'formatter': 'simple'
     },
     'file':
     {
      'level': 'DEBUG',
      'class': 'logging.handlers.RotatingFileHandler',
      'formatter': 'verbose',
      'filename': 'transcoder.log',
      'maxBytes': 4096 * 1024,
      'backupCount': 5
      },
    },
    'loggers':
    {
     '': {'handlers': ['file', 'console'], 'level': 'DEBUG', 'propagate': True}
     }
}

import logging
import logging.config
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

import os


def fileFinder(path, extentions):
    files = []
    if not os.path.isdir(path):
        raise FileNotFoundError
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            for extention in extentions:
                if filename.endswith(extention):
                    files.append(os.path.join(dirpath, filename))
                    break
    return files


def configureLogger():
    logging.config.dictConfig(LOG_CONFIG)


def changeExtension(filename, target_extention):
    name = os.path.splitext(filename)[0]
    return name + '.' + target_extention


def moveFile(file, target_dir, new_extension=''):
    if '' == new_extension:
        destination = os.path.join(target_dir, os.path.basename(file))
    else:
        destination = os.path.join(target_dir, changeExtension(os.path.basename(file), new_extension))
    logger.debug('Moving %s to %s' % (file, destination))
    os.renames(file, destination)

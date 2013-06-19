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

import logging
logger = logging.getLogger(__name__)

from os import makedirs, path
from shutil import rmtree
import subprocess

from util import fileFinder, moveFile


class Transcoder(object):
    name = str()
    """
    The Path to the Transcoder executable
    """
    executable = str()
    """
    a list of parapeters that will be giver to 'command' on execution.
    $INFILE will be replaced by the source file
    $OUTFILE will be replaced by the target path
    """
    parameters = list()

    workdir_in = str()
    workdir_out = str()

    def __init__(self, executable, parameters, name):
        logger.info('Creating new Transcoder(%s) from Executable: %s' % (name, executable))
        logger.info('Call Parameters are: %s' % parameters)
        self.executable = executable
        for parameter in parameters:
            self.parameters.extend(parameter.split(' '))
        self.name = name

    def transcode(self, filename):
        in_file = path.join(self.workdir_in, filename)
        out_file = path.join(self.workdir_out, filename)
        calllist = list()
        calllist.insert(0, self.executable)
        for parameter in self.parameters:
            calllist.append(parameter.replace('$OUTFILE', '%s' % out_file).replace('$INFILE', '%s' % in_file))

        logger.debug('Executing: %s' % calllist)
        subprocess.check_call(calllist, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_file

    def prepare(self, workdir):
        workdirs = list()
        self.workdir_in = path.join(workdir, '%s_in' % self.name)
        self.workdir_out = path.join(workdir, '%s_out' % self.name)
        workdirs.append(self.workdir_in)
        workdirs.append(self.workdir_out)
        for wdir in workdirs:
            try:
                makedirs(wdir, exist_ok=True)
            except OSError as e:
                logger.warning(e)
                logger.warning('Failed to create Workdir for %s' % self.name)

    def cleanup(self):
        rmtree(self.workdir_in)
        rmtree(self.workdir_out)


class Process(object):
    transcoders = list()
    extensions = list()
    sourcedir = str()
    targetdir = str()
    workdir = str()
    target_extention = str()

    def __init__(self, sourcedir, targetdir, workdir, transcoders, extensions, target_extension):
        logger.info('Creating new Process for Source Directory %s to Target Directory %s' % (sourcedir, targetdir))
        logger.info('Handling the following extentiones: %s' % extensions)
        self.transcoders = transcoders
        self.sourcedir = sourcedir
        self.targetdir = targetdir
        self.workdir = workdir
        self.extensions = extensions
        self.target_extension = target_extension

    def prepare(self):
        self.transcoders.sort(key=lambda tupel: tupel[0])
        for transcoder in self.transcoders:
            transcoder = transcoder[1]
            transcoder.prepare(self.workdir)

    def cleanup(self):
        for transcoder in self.transcoders:
            transcoder[1].cleanup()

    def process(self, file):
        for transcoder in self.transcoders:
            transcoder = transcoder[1]
            moveFile(file, transcoder.workdir_in)
            file = transcoder.transcode(path.basename(file))
        moveFile(file, self.targetdir, self.target_extension)

    def work(self):
        self.prepare()
        counter = 0
        files = fileFinder(self.sourcedir, self.extensions)
        for file in files:
            counter += 1
            logger.info('Processing %s of %s (%s)' % (counter, len(files), file))
            self.process(file)
        self.cleanup()

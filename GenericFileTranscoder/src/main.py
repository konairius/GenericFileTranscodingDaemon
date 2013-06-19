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
import util

util.configureLogger()

logger = logging.getLogger(__name__)

from xml.dom.minidom import parseString

from models import Transcoder, Process

processes = dict()


def main(configPath):
    with open(configPath, 'r') as file:
        string = file.read().replace('\n', '')
        processes = parseXML(string)
        for process in processes:
            process.work()


def parseXML(XMLString):

    def parseXMLNode(node):
        if 'process' == node.localName:
            return parseXMLProcess(node)
        elif 'transcoder' == node.localName:
            return parseXMLTranscoder(node)

    def parseXMLProcess(node):
        sourcedir = node.getAttribute('sourcedir')
        targetdir = node.getAttribute('targetdir')
        workdir = node.getAttribute('workdir')
        target_extension = node.getAttribute('target_extension')
        extensions = list()
        transcoders = list()
        for cnode in node.childNodes:
            #logger.debug('Found node of type %s containing %s' % (node.firstChild.nodeType, node.firstChild.data))
            if 'extension' == cnode.nodeName:
                extensions.append(cnode.firstChild.data)
            if 'transcoder' == cnode.nodeName:
                transcoders.append(parseXMLTranscoder(cnode))
        return Process(sourcedir=sourcedir,
                       targetdir=targetdir,
                       workdir=workdir,
                       target_extension=target_extension,
                       extensions=extensions,
                       transcoders=transcoders)

    def parseXMLTranscoder(node):
        name = node.getAttribute('name')
        orderNo = node.getAttribute('orderNo')
        parameters = list()
        for cnode in node.childNodes:
            if  'executable' == cnode.nodeName:
                executable = cnode.firstChild.data
            elif 'parameter' == cnode.nodeName:
                parameters.append(cnode.firstChild.data)
        return (orderNo, Transcoder(executable=executable, parameters=parameters, name=name))

    dom = parseString(XMLString)
    processes = list()
    for node in dom.childNodes:
        process = parseXMLNode(node)
        #for extension in process.extensions:
        processes.append(process)
    return processes

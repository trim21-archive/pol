#!/usr/bin/env python
from livereload import Server, shell

server = Server()
server.watch('source/*.*', shell('sphinx-build -M html source build'))
server.serve(root='build/html')

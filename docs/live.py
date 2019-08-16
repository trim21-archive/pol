#!/usr/bin/env python
from livereload import Server, shell

server = Server()
server.watch('source/*.*', shell('make html'))
server.serve(root='build/html')

#!/usr/bin/python
from xml.dom.minidom import Document
from optparse import OptionParser
import sys

system_encoding="utf-8"

parser = OptionParser("Usage: %prog [options] <source files>" )

parser.add_option( "-n", "--first-name", help="Author first name", dest="first_name", default = "Unknown" )
parser.add_option( "-s", "--second-name", help="Author second name", dest="second_name" )
parser.add_option( "-m", "--third-name", help="Author muddle name", dest="middle_name" )

parser.add_option( "-g", "--genre", help="Book genre", dest="genre", default="unknown" )
parser.add_option( "-t", "--title", help="Book title", dest="title", default = "Unknown Title" )
parser.add_option( "-c", "--encoding", help="Source file encoding", dest="encoding", default=system_encoding )
parser.add_option( "-o", "--output", help="Output file", dest="output" )

(options, args) = parser.parse_args()

if len(args) == 0:
    parser.error( "No input files specified" )
    exit( 1 )

################################################################################
# Start generating XML
################################################################################

doc = Document()

def make( root, elem_name, attrs=[] ):
    elem = doc.createElement( elem_name )
    if isinstance( attrs, dict ):
        attrs = attrs.values()
    for attr_name, attr_value in attrs:
        elem.setAttribute( attr_name, attr_value )
    root.appendChild( elem )
    return elem

def text( root, elem, text ):
    p_elem = make( root, elem )
    txt = doc.createTextNode( text )
    p_elem.appendChild( txt )
    return p_elem, txt


book = make( doc, "FictionBook" )

desc = make( book, "description" )
title_info = make( book, "title-info" )
text( title_info, "genre", options.genre.decode( system_encoding ) )
author = make( title_info, "author" )
text( author, "name", options.first_name.decode( system_encoding ) )
text( title_info, "book-title", options.title.decode( system_encoding ) )


body = make( book, "body" )


def convert_one_line_per_paragraph( src_file ):
    idx = 0
    while True:
        l = src_file.readline()
        idx += 1
        if not l: break
        l = l.strip("\r\n")
        
        try:
            text( body, "p", l.decode( options.encoding ) )
        except LookupError, err:
            raise
        except UnicodeDecodeError, err:
            print "Error decoding line %d: %s"%(idx, err)


for src in args:
    try:
        convert_one_line_per_paragraph( open( src ) )
    except Exception, err:
        print "Exception:", err



if options.output:
    ofile = open( options.output, "w" )
    ofile.write( doc.toxml("utf-8") )
    ofile.close()
else:
    print doc.toxml()



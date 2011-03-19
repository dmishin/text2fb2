#!/usr/bin/python
from xml.dom.minidom import Document
from optparse import OptionParser
import os.path

system_encoding="utf-8"
version = "0.1"

parser = OptionParser("Usage: %prog [options] <source files>" )

parser.add_option( "-f", "--first-name", help="Author first name", dest="first_name", default = "Unknown" )
parser.add_option( "-l", "--last-name", help="Author last name", dest="last_name" )
parser.add_option( "-m", "--third-name", help="Author muddle name", dest="middle_name" )

parser.add_option( "-g", "--genre", help="Book genre", dest="genre", default="unknown" )
parser.add_option( "-t", "--title", help="Book title", dest="title", default = "Unknown Title" )
parser.add_option( "-c", "--encoding", help="Source file encoding", dest="encoding", default=system_encoding )
parser.add_option( "-L", "--lang", help="Book language", dest="lang" )
parser.add_option( "-s", "--src-lang", help="Book source language", dest="src_lang" )
parser.add_option( "--encoding-errors", help="How to handle encoding errors: strict/ignore/replace", dest="encoding_errors", default="strict")
#parser.add_option( "--cover", help="Cover image", dest="cover" )

parser.add_option( "-o", "--output", help="Output file", dest="output" )

(options, args) = parser.parse_args()

if len(args) == 0:
    parser.error( "No input files specified" )
    exit( 1 )
if len(args) > 1 and options.output:
    parser.error( "Output file can not be used, when converting several files" )
if options.encoding_errors not in ('strict', 'ignore', 'replace'):
    parser.error( "Encoding error handler must be strict/ignore/replace" )
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
if options.first_name:
    text( author, "first-name", options.first_name.decode( system_encoding ) )
if options.last_name:
    text( author, "last-name", options.last_name.decode( system_encoding ) )
if options.middle_name:
    text( author, "middle-name", options.middle_name.decode( system_encoding ) )

text( title_info, "book-title", options.title.decode( system_encoding ) )
if options.lang:
    text( title_info, "lang", options.lang.decode( system_encoding ) )
if options.src_lang:
    text( title_info, "src-lang", options.src_lang.decode( system_encoding ) )

text( title_info, "program-used", "text2fb2.py version %s"%version )

body = make( book, "body" )
def convert_one_line_per_paragraph( src_file ):
    idx = 0
    while True:
        l = src_file.readline()
        idx += 1
        if not l: break
        l = l.strip("\r\n")
        
        try:
            text( body, "p", l.decode( options.encoding, options.encoding_errors ) )
        except LookupError, err:
            raise
        except UnicodeDecodeError:
            print "Error decoding line %d"%(idx, err)
            print l
            raise


for src in args:
    if options.output:
        ofile = options.output
    else:
        ofile = os.path.splitext( os.path.split( src )[1] )[0] + ".fb2"

    try:
        convert_one_line_per_paragraph( open( src ) )
        
        ofile = open( ofile, "w" )
        ofile.write( doc.toxml("utf-8") )
        ofile.close()
    except Exception, err:
        print "Exception:", err
    




''' 
    This program reads the contact data from an OVI backup file
    (sqlite) create for a NOKIA N95 phone and writes them formated 
    as XML to stdout.

    The backup file is usually located in: 
    C:\Users\<user>\AppData\Local\Nokia\Nokia Data Store\DataBase\MDataStore.db3

    Note: the exported XML only contains elements with a valid value (not None)

    Example:
        > python contacts2xml.py MDataStore.db3
        <?xml version="1.0" ?>
        <contacts>
          <contact id="0">
            <GUID>{83c8c515-7dbb-425c-af74-f0364a452b3d}</GUID>
            <GivenName>Aaron</GivenName>
            <LastName>Arinson</LastName>
            <GeneralMobile>0123456789</GeneralMobile>
            <GeneralPhone>0987654321</GeneralPhone>
          </contact>
          <contact id="1">
            <GUID>{fb7edaba-5d36-4b57-b923-71a859189fff}</GUID>
            <GivenName>Bert</GivenName>
            <LastName>Bronson</LastName>
            <GeneralMobile>422323422</GeneralMobile>
          </contact>
          ...
        </contacts>

'''

import sqlite3 as sqlite3
import sys, os
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
       found here: http://pymotw.com/2/xml/etree/ElementTree/create.html
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def ovi_n95_contact_backup_2_xml(db_file):

    ''' read the Contact table from a OVI sqlite backup file and
        write the content formated as XML to stdout
    '''

    try:

        con = sqlite3.connect(db_file)
        cur = con.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = cur.fetchall()

        if (u'Contact',) not in all_tables:
            raise Exception('missing table \'Contact\' - not a valid \
                OVI backup database file?!?')
        
        cur.execute("SELECT * FROM Contact")
        rows = cur.fetchall()

        if len(rows) == 0:
            raise Exception('not contacts found in database.')    

        col_names = [col[0] for col in cur.description]

        root = Element('contacts')

        i = 0

        for entry in rows:
            contact = SubElement(root, 'contact', id="%d" % (i))

            for idx, col in enumerate(entry):
                if col is not None:
                    SubElement(contact, col_names[idx]).text = col
            i += 1
        
        print prettify(root)

    except sqlite3.Error, err:
        sys.stderr.write('failed to open sqlite database cause: %s', err)
        sys.exit(-1)

    except Exception as err:

        sys.stderr.write('%s\n' % (err))
        sys.exit(-1)

if __name__ == '__main__':

    try:
        if os.path.isfile(sys.argv[1]) is False:
            sys.stderr.write('given database file \'%s\' not found.\n' \
                % (sys.argv[1]))
            sys.exit(-1)

        ovi_n95_contact_backup_2_xml(sys.argv[1])

    except IndexError:
        sys.stderr.write('missing parameter <db-file-name>.\n')
        sys.exit(-1)
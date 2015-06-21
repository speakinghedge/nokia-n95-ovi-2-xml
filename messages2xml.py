'''
    This program reads the message data from an OVI backup file
    (sqlite) create for a NOKIA N95 phone and writes them formated
    as XML to stdout.

    The backup file is usually located in:
    C:\Users\<user>\AppData\Local\Nokia\Nokia Suite/ \
        Messages/Database/msg_db.sqlite

    Note: the exported XML only contains elements with a valid value (not None)

    Example:
        > python messages2xml.py msg_db.sqlite
        <?xml version="1.0" ?>
        <messages>
          <message id="0">
            <msg_txt>Lorem ipsum dolor sit amet, consectetur </msg_txt>
            <msg_address>123456789</msg_address>
            <msg_folder>1</msg_folder>
            <msg_time>1297268424</msg_time>
            <msg_imei>789456123</msg_imei>
            <msg_status>36</msg_status>
            <msg_uid>{1c58fef3-932e-4106-86ee-f9fe0a50363d}</msg_uid>
            <msg_address_substr>3572583</msg_address_substr>
          </message>
          <message id="1">
            <msg_txt>odio ultrices nunc semper iaculis. Fusce nibh</msg_txt>
            <msg_address>987654321</msg_address>
            <msg_folder>1</msg_folder>
            <msg_time>1300101857</msg_time>
            <msg_imei>358064010341612</msg_imei>
            <msg_status>36</msg_status>
            <msg_uid>{e93839af-a899-4de8-a14c-92e136d13ccd}</msg_uid>
            <msg_address_substr>3572583</msg_address_substr>
          </message>
          ...
        </messages>
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

def ovi_n95_messages_backup_2_xml(db_file):

    ''' read the messages table from a OVI sqlite backup file and
        write the content formated as XML to stdout
    '''

    try:

        con = sqlite3.connect(db_file)
        cur = con.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = cur.fetchall()

        if (u'messages',) not in all_tables:
            raise Exception('missing table \'messages\' - not a valid ' \
                'OVI backup database file?!?')

        cur.execute("SELECT * FROM messages")
        rows = cur.fetchall()

        if len(rows) == 0:
            raise Exception('no messages found in database.')

        col_names = [col[0] for col in cur.description]

        root = Element('messages')

        i = 0

        for entry in rows:
            message = SubElement(root, 'message', id="%d" % (i))

            for idx, col in enumerate(entry):
                if col:
                    SubElement(message, col_names[idx]).text = "%s" % (col)
            i += 1

        print u''.join(prettify(root)).encode('utf-8', \
            errors='xmlcharrefreplace').strip()

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

        ovi_n95_messages_backup_2_xml(sys.argv[1])

    except IndexError:
        sys.stderr.write('missing parameter <db-file-name>.\n')
        sys.exit(-1)
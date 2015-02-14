"""
    This project is a program to validate well-formdness of XML files.
    author: Matjaz Pirnovar

    XML syntaxt rules to use in the program logic:

    1. The first line in the document is the XML declaration should always be included.
    It defines the XML version of the document:<?xml version="1.0"?>

    2. Root element (the first element). Needs to have open and closing tag. - WORKING ON
    - check that the root element exists and that it has opening and closing tag
    - indicator of the root element could be < without question mark (<? is for XML declaration)

    3. Child elements need to be within the root element
    - check that child elements have parents

    4. Nested child elements need to be within their parents

    5. All XML elements need to have closing tag.

    6. XML tags are case sensitive

    7. All elements must be properly nested

    8. Attribute values must always be quoted

    9. Comments must be within comment tags <!-- -->

    10. All data strings must be within element tags (not inside tags)

    11. XML must allow multiple whitespace characters.

    12. Must be no spaces in the name of an element (<dateofbirth> is correct, <date of birth> is incorrect )

    13. Must be no space between opening bracket and the name of an element.
    Example: < body> is prohibited

    14. There may be whitespace between the end of the name or attribute in an opening element tag and the closing bracket of that element.
    Example: <body   > is allowed
    It's because attributes can be put there.
"""



def getstring():
    '''
    put xml content from file into a string (also make sure you use try/except!)
    :return: xml_string
    '''
    xml_string = ""
    with open('xml_example.txt', 'r') as f:
        for i in f:
            xml_string = xml_string + i
        return xml_string


# ****************************************************************************************************
#   GET THE OPENING ROOT ELEMENT
# ****************************************************************************************************

def root_element_opening():
    ''' Get the opening root element.

        Iterate from start of the file onwards.
        store position value when you hit first '<' character that is not part of XML declaration (no ? after '<')
        that is the opening tag of the root element
        WHAT ABOUT IF  '<' chars appear before the root tag '<'???? Then it doesn't work! How do I define root element and finf it???
    '''
    opening, closing = 0,0
    flag = False
    for i, char in enumerate(getstring()):     # loop through tuple items and find the first item that has '<'.
        if char == '<' and getstring()[i + 1] != '?' and getstring()[i + 1] != '!' :      # '!' is to ignore DTD declarations
            opening = i
            flag = True
        if char == '>' and flag == True:
            closing = i
            content = getstring()[opening:closing+1]
            return content

print('result-opening: ', root_element_opening())



# ****************************************************************************************************
#   GET THE CLOSING ROOT ELEMENT
# ****************************************************************************************************

def root_element_closing():
    ''' Get the closing root element.
    '''
    opaning, closing = 0,0
    for count, char in enumerate(reversed(getstring())):        # loop through tuple items and find the first item that has '<'.
        if char == '>':   # found last closing bracket in the whole file, function only as an assertion - no other mening
            assert count == 0
        if char == '<':     # iterate from the end and find first opening bracket
            opening = count + 1
            return getstring()[-opening:]      # return characters from last opening bracket to the end


print('result-closing: ', root_element_closing())



# ****************************************************************************************************
#   COMPARE OPENING AND CLOSING ROOT ELEMENTS IF THEY MATCH
# ****************************************************************************************************

def root_element_exists_and_matches():
    ''' Compare opening and closing root element if they match.
    '''
    # check if the names of the root tags match
    # make sure that for comparison you ignore the forward slash
    if root_element_opening() == (root_element_closing()[0] + root_element_closing()[2:]):
        print(root_element_opening(), root_element_closing(), "Root element: opening and closing tag match.")
    else:
        print(root_element_opening(), root_element_closing(), "Root element: opening and closing tag don't match.")

root_element_exists_and_matches()



'''
Characters to escape in XML:
"   &quot;
'   &apos;
<   &lt;
>   &gt;
&   &amp;
'''


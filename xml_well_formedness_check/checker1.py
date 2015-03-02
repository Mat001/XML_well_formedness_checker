"""
    This project is a program to validate well-formedness of XML files.
    author: Matjaz Pirnovar
    date: Feb 2015
"""

from xml_well_formedness_check.utility_functions import *
import re


# ****************************************************************************************************
#   CHECK THAT NUMBER OF < and > IS EVEN
# ****************************************************************************************************

def number_of_angle_brackets_is_even():
    """
    Check that number of angle brackets (<,>) is even.
    PS: Not a full test of matching brackets! For example even number of closing brackets
    could be missing or be added and the number would still be even.
    :return: sum of all angle brackets (as length of the list)
    """
    number_of_all_angle_brackets = len([char for char in getstring() if char == '<' or char == '>'])
    if number_of_all_angle_brackets % 2 != 0:
        print('No of angle brackets is not even (' + str(number_of_all_angle_brackets) + '). Check that brackets correctly surround tags.')
        return False
    else:
        return True

# ****************************************************************************************************
#   CHECK THAT NUMBERS OF < and > MATCH
# ****************************************************************************************************
def number_of_opening_and_closing_brackets_match():
    """
    Get number of opening and closing brackets and compare if the number matches.
    :return: boolean
    """
    open = getstring().count('<')
    clos = getstring().count('>')
    if not open == clos:
        print('Numbers of opening and closing brackets don\'t match. '
              'Check that brackets correctly surround tags (' + str(open) + ', ' + str(clos) + ').')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THERE ARE NO IDENTICAL TAGS (except comments and single elements)
# ****************************************************************************************************
def no_duplicate_tags():
    """
    Check for exactly identical tags. Should never occur, except for comments and single elements.
    Paired elements need closing tag.
    :return: boolean
    """

    if len(find_duplicate_tags()) != 0:
        print('Duplicate tags found: ', find_duplicate_tags())
        return False
    else:
        return True



# ****************************************************************************************************
#   CHECK THAT FILE STARTS WITH XML DECLARATION
# ****************************************************************************************************
def starts_with_xml_declaration():
    """
    Check that file starts with xml declaration
    :return: boolean
    """
    xml='<?xml'

    # Starts with xml declaration
    if getstring().startswith(xml):
        #print('XML file immediately starts with XML declaration.')
        return True
    else:
        print('XML file does not start with XML declaration.')
        return False


# ****************************************************************************************************
#   COMPARE OPENING AND CLOSING TAGS OF THE ROOT ELEMENT IF THEY MATCH
# ****************************************************************************************************

def root_tags_match():
    """ Compare opening and closing root element if they match.
    :return: boolean
    """
    # check if the names of the root tags match

    # clean opening and closing tag
    # inthis case it means: transform tuple ("<example id=''>", '</example>') into <example, <example)
    opening = get_root_element()[0] # get opening tag

    # get tag name from < to first whitespace and
    # get tag name from < to >
    first_space = opening.find(' ')
    no_space = opening.find('>')
    opening_if_space = opening[1:first_space]
    opening_if_no_space = opening[1:no_space]

    if ' ' in opening: opening = opening_if_space
    elif ' ' not in opening: opening = opening_if_no_space

    closing = get_root_element()[1].replace('/', '')    # ignore forward slash in closing tag
    closing = closing[1:-1]     # get closing tag's name

    # now tags should be in clean form to be compared (eg example, example)
    if opening != closing:
        print('Root tags don\'t match.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE IS NO SPACE BETWEEN AN OPENING BRACKET AND THE NAME OPENING TAGS
# ****************************************************************************************************
def no_initial_space_in_opening_tags():
    """
    Check there is no space between opening bracket and the name in opening tags
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == ' ':
            print('Space immediatelly after \'<\' not allowed.', tag)
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT THERE NO SPACE IN CLOSING TAGS
# ****************************************************************************************************
def no_spaces_in_closing_tags():
    """
    Check that closing tags don't have spaces. INCLUDE SINGLE EMPTY TAGS!!!
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == '/' and ' ' in tag[1:]:
            print('Closing tag must not have spaces.', tag)
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT CLOSING TAGS START WITH </
#  ****************************************************************************************************
def closing_tag_incorrectly_formed():
    """
    Check that closing tags start with '</' .
    :return: boolean
    """
    tags = remove_declaration_doctype_comments()

    # for paired closing tags
    without_singles = [tag for tag in tags if '/>' not in tag]

    for tag in without_singles:
        # if it has '/' it should be immediatelly after <
        if '/' in tag:
            if not tag.startswith('</'):
                print('Closing tag not formed correctly (must start with \'</\' if tag has open tag counterpart or end with \'/>\' if the tag is single): ', tag)
                return False
    return True


# ****************************************************************************************************
#   CHECK FOR INVALID CHARACTERS AT THE BEGINNING OF TAG NAME
# ****************************************************************************************************
def no_invalid_initial_characters_in_opening_tag():
    """
    Element names must not start with digits, diacritics, the full stop, the hyphen and 'xml' (any letter case).
    Element names must start with letter (uppercase or lowercase), underscore, or colon.
    :return: boolean
    """

    # Check that element names DO NOT start with digits, diacritics, the full stop,
    # the hyphen and 'xml' (any letter case).
    # I left diacritics requirement out for the moment
    invalid_start_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ,
                                '.', '-', 'xml', 'XML', 'Xml', 'xMl', 'xmL', 'XMl', 'xML']

    for tag in get_all_tags_in_order():
        for char in invalid_start_characters:
            if tag[1] == char:
                print('Tag with invalid start character: ', tag)
                return False


    # Check that element names DO start with letter (uppercase or lowercase), underscore, or colon.
    for tag in get_all_tags_in_order():     #make sure that names starting with ? and ! pass through
        if tag[1] != '?' and tag[1] != '!' and \
            not tag[1].isalpha() and \
            not tag[1] == '_' and \
            not tag[1] == ':' and \
            not tag[1] == '/':
                print('Element name should start with letter, underscore or colon: ', tag)
                return False
    else:
        return True



# ****************************************************************************************************
#   CHECK THAT ELEMENT NAMES CONTAIN ONLY VALID CHARACTERS
# ****************************************************************************************************
def element_names_contain_only_valid_characters():
    """
    Rule 1:
    Name must begin with letter (uppercase or lowercase), underscore, or colon
    and CONTINUING with letters, digits, hyphens, underscores, colons, or full stops.
    Middle dot also allowed (unlikely to be seen in xml).
    (source: http://www.xml.com/pub/a/2001/07/25/namingparts.html and http://www.w3.org/TR/xml/#sec-well-formed)

    - Doesnt check initial character rules (already covered)
    - Doesn't check for initial space in name (already covered)
    :return: boolean
    """

    if no_invalid_initial_characters_in_opening_tag() and no_initial_space_in_opening_tags():
        names = set(get_clean_tags())

        # if anything else but letters, digits, hyphens, underscores, colons or full stops in names return false
        for name in names:
            if not re.match(r'[ A-Za-z0-9_:.-]*$', name):
                print('Element name contains invalid character(s): ', name)
                return False
        return True

    else:
        print('Invalid initial character or disallowed initial space in opening tag.')
        return False


# ****************************************************************************************************
#   CHECK THAT ELEMENTS ARE CLOSED PROPERLY AND NAMES MATCH (PAIRED ELEMENTS, NOT SINGLE ONES)
# ****************************************************************************************************
def paired_elements_are_closed_properly_and_names_match():
    """
    Check that paired elements (not single ones) are closed properly.
    Based on the fact that number of < must match number of </.
    If it doesn't, then either < or </ are mis-formatted or are missing.
    :return: boolean
    """
    # This is only a preliminary partial check -> fails when there is even number of missing brackets of the same type!
    # The rest of the code below must run for complete check
    if not number_of_angle_brackets_is_even():
        print('Elements not properly closed. Number of angle brackets is not even - tag(s) incorrectly formed.')
        return False

    if not number_of_opening_and_closing_brackets_match():
        print('Numbers of opening and closing brackets don\'t match.')
        return False

    # get all tags and clean them up
    tags = remove_declaration_doctype_comments()

    # get rid of singles (that end with '/>'
    l = [ tag for tag in tags if '/>' not in tag ]

    # get rid of any attributes in opening tags
    l2=[]
    indices = []
    for i, tag in enumerate(l):
        if ' ' in tag and tag.startswith('</'):
            print('Closing tag must not contain spaces.', tag)
            return False
        if ' ' in tag and '/' not in tag:
            space_pos = tag.index(' ')
            open_name = tag[:space_pos] + '>'
            l2.append(open_name)    # a list of changed opening names
            indices.append(i)

    for count, tag in enumerate(l2):
        l[indices[count]] = l2[count]      # this is the list of tags without attributes


    # MAKE CHECKS
    # opening and closing bracket in place
    both_brackets_in_place = [ tag for tag in l if tag.startswith('<') and tag.endswith('>') ]
    if both_brackets_in_place == 0:
        print('Opening and closing bracket not matching.')
        return False
    # no space in closing tag
    if no_spaces_in_closing_tags() != True:
        print('One or more closing tag(s) contains space.')
        return False

    # no space in opening tag
    if no_initial_space_in_opening_tags() != True:
        print('One or more opening tag(s) contains space at the begining of the tag.')
        return False

    # get content between tags and compare - find pair names that don't match
    opening = [ tag for tag in l if not tag.startswith('</') ]
    closing = [ tag for tag in l if tag.startswith('</') ]

    closing_no_slashes = [ tag.replace('/','') for tag in closing if '/' in tag ]    # remove slashes
    #print('CLOSING NO SLASHES: ', closing_no_slashes)

    mismatching_tag_name_op = list(set(opening) - set(closing_no_slashes))
    mismatching_tag_name_cl = list(set(closing_no_slashes) - set(opening))

    # put slashes back to closing tags so they can be printed properly in error message
    for i, name in enumerate(mismatching_tag_name_cl):
        mismatching_tag_name_cl[i] = name[0]+'/'+name[1:]

    if len(mismatching_tag_name_op) != 0:
        print('The following opening tag names don\'t have a match: ', mismatching_tag_name_op) # check - always shows opening tag as without a match, even when closing one is problematic
        return False
    elif len(mismatching_tag_name_cl) != 0:
        print('The following closing tag names don\'t have a match: ', mismatching_tag_name_cl)
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT TAGS ARE CASE SENSITIVE - CURRENTLY WORKS FOR LOWERCASE
# ****************************************************************************************************
def all_lowercase_tags():
    """
    Check that tags are case sensitive.
    For now, ensure all tag names are lower case.
    :return: boolean
    """
    for tag in get_clean_tags():
        if not tag.islower():
            print('Incorrect tag name. Should be lower case: ', tag)
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT NESTING IS PROPER - DONE!
# ****************************************************************************************************
def is_nesting_proper():
    """
    CHECK THAT NESTING IS PROPER

    Symmetry approach using stack:
    Iterate through the list of cleaned, ordered tags
    If item is not in (initially empty) temp list, then append item
    else if item is the last element in the temp list, then pop it out
    else - if item doesn't match the last item in the temp list, then that item was incorrectly nested. we flag error.

    There must always be both parts of a tag-pair within a stretched element (parent).
    In the example below <to></to> is "stretched tag" -  tag that holds other elements.
    For example <to><from></from><lastname></lastname></to> is correct
    For example <to><from><lastname></lastname></to></from> is incorrect
    :return: boolean
    """
    # clean up tags from scratch and remove single elements (they don't affect nesting)
    tags = remove_declaration_doctype_comments()

    without_singles = [tag for tag in tags if '/>' not in tag]

    no_slash = [tag.replace('/', '') for tag in without_singles]
    split = [tag.split() for tag in no_slash]
    first_part = [part[0] for part in split]

    clean = []
    for tag in first_part:
        tag = tag.strip('<')
        tag = tag.strip('>')
        clean.append(tag)

    tag_list_pairs = [x for x in clean if clean.count(x) >= 2]

    # use symmetry approach using a stack
    temp_list = []
    for item in tag_list_pairs:
        if item not in temp_list:
            temp_list.append(item)
        elif item == temp_list[-1]:
            temp_list.pop()
        else:
            print('Incorrectly nested tag is \'' +temp_list[-1] + '\' or that tag needs to be a single tag ending with \'/>\'.')
            return False

    if len(temp_list) == 0:
        return True


# ****************************************************************************************************
#   IS NUMBER OF COMMENT TAGS EVEN
# ****************************************************************************************************
def is_number_of_comment_tags_even():
    """
    Check if number of commnt tags is even
    - utility function
    :return: boolean
    """
    if len(get_opening_comment_tag_positions() + get_closing_comment_tag_positions()) % 2 != 0:
        print('Number of comment tags is not even.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT OPENING COMMENT TAG IS FOLLOWED BY CLOSING TAG
# ****************************************************************************************************
def is_comment_opening_tag_followed_by_closing_tag():
    """
    # Check that each opening comment tag is followed by closing tag
    Sequence of comment tags must follow: opening-closing_opening_closing.
    Disallow two of the same one after the other. This will check for nesting.
    :return: boolean
    """
    if is_number_of_comment_tags_even():
        l=[]
        # append position of opening tag then closing, then opening, then closing etc.
        # sequence must be strictly sorted in ascending order, otherwise this function test fails-False
        for i in range(len(get_opening_comment_tag_positions())):
            l.append(get_opening_comment_tag_positions()[i])
            l.append(get_closing_comment_tag_positions()[i])
        #print('SEQUENCE: ', l)
        if l != sorted(l):
            print('Error in comment tags.')
            return False
        else:
            return True
    else:
        print('Number of comment tags is not even - wrong nesting.')
        return False


# ****************************************************************************************************
#   CHECK THAT COMMENT CLOSING TAGS DONT HAVE EXTRA DASH (--->)
# ****************************************************************************************************
def comment_closing_tags_dont_have_extra_dash():
    """
    Check that comment closing tags don't have extra dash (--->).
    :return: boolean
    """
    if '--->' in getstring():
        print('Comment tags should not have extra dash.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT CLOSING TAGS THAT ARE NOT SINGLE DON'T HAVE ATTRIBUTES
# ****************************************************************************************************
def closing_tags_that_are_not_single_dont_have_attributes():
    """
    Check that closing tags that are not single don't have attributes.
    Here the check is made on absence of spaces in closing tag.
    That automatically implies no attributes.
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == '/':
            if ' ' in tag:
                print('Closing tag (paired one) should not have an attribute.')
                return False
            else:
                return True


# ****************************************************************************************************
#   CHECK THAT SINGLE ELEMENTS ARE CORRECTLY FORMED - CASE WITHOUT ATTRIBUTE
# ****************************************************************************************************
def single_element_is_correctly_formed_case_without_attribute():
    """
    Check that single elements are correctly formed.
    Examples: <example/> <br       />, <acb />, <child attribute="value" />

    # Done so far:
    # Includes proper closure!
    # Not checking for space between name and / because it is allowed. It's for attributes, which still need to be checked.
    # checking that there is no space between / and >
    # first part of the tag <... is already checked because functions no_initial_space_in_opening_tags(), ... take car of it
    # closing tag /> is validated here - no space between / and >
    # in between it's okay to have space - for attribute - which still need to be checked
    :return: boolean
    """

    # test the correctness of the single tag (if '/' at the end before >)
    for tag in get_single_elements():
        if not tag.endswith('/>') or tag.startswith('< '):
            print('Problematic single element - not correctly formed: ', tag)
            return False
        else:
            return True


# ****************************************************************************************************
#   CHECK THAT NO RESTRICTED CHARACTERS ARE PRESENT IN DATA CONTENT
# ****************************************************************************************************
def no_restricted_characters_in_content():
    """
    TO SIMPLIFY, LIMIT RESTRICTED CHARS TO: <,>,&
    WARNING: DOESN'T YET HANDLE REPLACEMENTS WITH &quot; &apos; etc.

    Characters ", ', <, >, & must not appear in xml document content.
    They need to be replaced by:
        "   &quot;
        '   &apos;
        <   &lt;
        >   &gt;
        &   &amp;
    :return: boolean
    """
    # check brackets first
    if not number_of_angle_brackets_is_even():
        print('Elements not properly closed. Number of angle brackets is not even - tag(s) incorrectly formed.')
        return False

    if not number_of_opening_and_closing_brackets_match():
        print('Numbers of opening and closing brackets don\'t match.')
        return False

    # get content between tags (>  <)g
    # check that it doesn't contain any of the above characters
    restricted = [ '<', '>', '&' ]
    restricted_chars = [ char for char in get_data_content() for c in restricted if c in char ]
    if len(restricted_chars) != 0:
        print('Invalid characters (<, >, &) in data content: ', restricted_chars)
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE IS NOTHING BEFORE AND AFTER THE ROOT TAG
# ****************************************************************************************************
def no_invalid_content_after_root_tag():
    """
    And that there is nothing below the ending root tag
    :return: boolean
    """
    # check after the ending root tag
    last_char = getstring()[-1]
    after = getstring()[-1:]
    if last_char != '>' and after != '':
        print('Content after the ending root tag is disallowed. Even spaces - please delete them.')
        return False
    else:
        return True





# ****************************************************************************************************
# ****************************************************************************************************
# ****************************************************************************************************
#   EXECUTE FUNCTIONS
# ****************************************************************************************************

#print('**********************************************************************************')
#print('    UTILITIES')
#print('**********************************************************************************')

# UTILITIES
#print('All tags in order: ', get_all_tags_in_order())
#print('Clean tags: ', get_clean_tags())
#print('Duplicate tags: ', find_duplicate_tags())
#print('Root element: ', get_root_element())
#print('Get comment opening tag positions: ', get_opening_comment_tag_positions())
#print('Get comment closing tag positions: ', get_closing_comment_tag_positions())
#print('Number of all tags (without declar, doctype, commen): ', get_number_of_all_tags_excluding_declar_doctype_comments())
#print('Get single elements: ', get_single_elements())
#print('Get data content: ', get_data_content())

print('**********************************************************************************')
print('    CHECKS')
print('**********************************************************************************')

# CHECKS
# Main run:


def run():
    """
    Function to invoke the program
    :return: print statements: warnings and that file is well formed.
    """
    if number_of_angle_brackets_is_even():
        #print('Number of angle brackets is even: ', number_of_angle_brackets_is_even())
        if number_of_opening_and_closing_brackets_match():
            #print('Numbers of opening and closing brackets match: ', number_of_opening_and_closing_brackets_match())
            if no_duplicate_tags():
                #print('No duplicate tags: ', no_duplicate_tags())
                if starts_with_xml_declaration():
                    #print('Starts with xml declaration (or comment and then xml declar.)): ', starts_with_xml_declaration())
                    if root_tags_match():
                        #print('Root element tags match: ', root_tags_match())
                        if no_invalid_initial_characters_in_opening_tag():
                            #print('No invalid initial characters in opening tag: ', no_invalid_initial_characters_in_opening_tag())
                            if no_initial_space_in_opening_tags():
                                #print('No initial space in opening tags: ', no_initial_space_in_opening_tags())
                                if element_names_contain_only_valid_characters():
                                    #print('Element names contain only valid characters: ', element_names_contain_only_valid_characters())
                                    if closing_tag_incorrectly_formed():
                                        #print('Closing tg starts correctly: ', closing_tag_incorrectly_formed())
                                        if no_spaces_in_closing_tags():
                                            #print('No spaces in closing tags:', no_spaces_in_closing_tags())
                                            if paired_elements_are_closed_properly_and_names_match():
                                                #print('Elements are closed properly: ', paired_elements_are_closed_properly_and_names_match())
                                                if closing_tags_that_are_not_single_dont_have_attributes():
                                                    #print('Closing tags (not single) dont have attributes: ', closing_tags_that_are_not_single_dont_have_attributes())
                                                    if single_element_is_correctly_formed_case_without_attribute():
                                                        # print('Single element is correctly formed (not considering attrib.): ', single_element_is_correctly_formed_case_without_attribute())
                                                        if all_lowercase_tags():
                                                            #print('All lowercase tags: ', all_lowercase_tags())
                                                            if is_nesting_proper():
                                                                #print('Is nesting proper: ', is_nesting_proper())
                                                                if is_number_of_comment_tags_even():
                                                                    #print('Is number of comment tags even: ',  is_number_of_comment_tags_even())
                                                                    if is_comment_opening_tag_followed_by_closing_tag():
                                                                        #print('Is opening tag for comments immediatelly followed by closing tag (means there is no nesting): ',
                                                                         #     is_comment_opening_tag_followed_by_closing_tag())
                                                                        if comment_closing_tags_dont_have_extra_dash():
                                                                            #print('Comment closing tags dont have extra dash: ', comment_closing_tags_dont_have_extra_dash())
                                                                                if no_restricted_characters_in_content():
                                                                                    #print('No restricted characters in content: ', no_restricted_characters_in_content())
                                                                                    if no_invalid_content_after_root_tag():
                                                                                        #print('No invalid content before or after the root tag: ', no_invalid_content_before_and_after_root_tag())
                                                                                        print('Document is well formed!')


# run the program
run()




""" # SOME GUI HERE, NOT YET LINKED TO XML CHECKER
#**********************************************************************************
#    GUI
#**********************************************************************************
import sys
from tkinter import *

def gui():
    mText = xml_text.get()
    mLabel2 = Label(mGui, text = mText).pack()
    return


mGui = Tk()
xml_text = StringVar()

mGui.geometry('500x500')
mGui.title('XML Well Formedness Checker')
mLabel = Label(mGui, text = 'XML Well Formedness Checker').pack()
mEntry = Entry(mGui, textvariable = xml_text).pack()
mButton = Button(mGui, text = 'Check', command = gui, fg='yellow', bg='black').pack()

mainloop()
"""
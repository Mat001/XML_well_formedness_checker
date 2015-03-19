"""
    This project is a non-validating XML parser that checks well-formedness of XML files.
    author: Matjaz Pirnovar
    date: Feb 2015
"""

from xml_well_formedness_check.utility_functions import *
import re

"""
Class that simplifies displaying warning messages.
~"""

class ErrorLog():

    def __init__(self):
        self.sText = ""
        self.count = 0

    def add_msg(self, s_src, s_msg):
        """
        :param s_src: where the error happens, ie something like C1Colors.ReadFromXml
        :param s_msg: the actual error message
        """
        # Matjaz: Find way to incorporate line numbers and line text into s_msg

        self.count += 1
        self.sText += "\n============================================================="
        self.sText += "\nFrom " + s_src +":\n" + s_msg

err = ErrorLog()

# ****************************************************************************************************
#   CHECK THAT DOCUMENT DOESN'T HAVE EXTRA-ORPHAN BRACKETS
# ****************************************************************************************************

def no_orphan_brackets(err):
    """
    Check that there are no orphan, single, obsolete, extra brackets.
    Each opening bracket should have a closing pair (<,>).
    Function checks that no two or more consecutive opening or closing brackets exist (<,< is incorrect).
    - every > must have < as the next bracket
    - every < must have > as the previous bracket
    - find places where these two rules are violated
    :return: boolean
    """
    # get ordered list of all indexed brackets
    brackets = [ (ind, i) for ind, i in enumerate(getstring()) if i == '<' or i == '>']
    #print(brackets)

    # get list of lengths of each line
    line_lenghts = [ len(line[1]) for line in get_line_numbers() ]

    # get list of lengths of each line in growing fashion. Each length is a sum of previous lengths.
    # this is to have intervals in which we look for bracket position
    increasing_line_lengths=[0] # Needs to start at zero!
    s=0
    for i in line_lenghts:
        s += i
        increasing_line_lengths.append(s)
    #print('Increasing line lengths: ', increasing_line_lengths)

    # implement "sliding window" technique, that is compare two consecutive brackets. They should not be the same.
    for i, bracket in enumerate(brackets[:-1]):
        if brackets[i+1][1] == bracket[1]:
            # find interval in which bracket falls
            for ind, brack in enumerate(increasing_line_lengths[:-1]):
                if bracket[0] >= brack and bracket[0] < increasing_line_lengths[ind + 1]:
                    number, content = get_line_numbers()[ind]  # tuple unpacking of line number and the line content
                    #print('Document has extra-orphan bracket(s) on line number ' + str(number) + ': ' + content)
                    #print(err.sText + str(number) + ': ' + content)
                    err.add_msg('no_orphan_brackets', 'Document has extra-orphan bracket(s) on line number '
                                                            + str(number) + ': ' + content)

            return False
    return True


# ****************************************************************************************************
#   CHECK THAT NUMBER OF < and > IS EVEN
# ****************************************************************************************************

def number_of_angle_brackets_is_even(err):
    """
    Check that number of angle brackets (<,>) is even.
    PS: Not a full test of matching brackets! For example even number of closing brackets
    could be missing or be added and the number would still be even.
    :return: sum of all angle brackets (as length of the list)
    """
    number_of_all_angle_brackets = len([char for char in getstring() if char == '<' or char == '>'])
    if number_of_all_angle_brackets % 2 != 0:
        err.add_msg('number_of_angle_brackets_is_even', 'No of angle brackets is not even (' + str(number_of_all_angle_brackets) + ') '
                                                            'Check that brackets correctly surround tags.')

        return False
    else:
        return True

# ****************************************************************************************************
#   CHECK THAT NUMBERS OF < and > MATCH
# ****************************************************************************************************

def number_of_opening_and_closing_brackets_match(err):
    """
    Get number of opening and closing brackets and compare if the number matches.
    :return: boolean
    """
    open = getstring().count('<')
    clos = getstring().count('>')

    if open > clos:
        err.add_msg('number_of_opening_and_closing_brackets_match', 'Numbers of opening and closing brackets don\'t match. '
              'There is/are ' + str(open-clos) + ' too many opening bracket(s).'
              'Check that brackets correctly surround tags.')
        return False
    elif open < clos:
        err.add_msg('number_of_opening_and_closing_brackets_match', 'Numbers of opening and closing brackets don\'t match. '
              'There is/are ' + str(clos - open) + ' too many opening bracket(s).'
              'Check that brackets correctly surround tags.')
    else:
        return True



# ****************************************************************************************************
#   CHECK THERE ARE NO IDENTICAL TAGS (except comments and single elements)
# ****************************************************************************************************
def no_duplicate_tags(err):
    """
    Check for exactly identical tags. Should never occur, except for comments and single elements.
    Paired elements need closing tag.
    REVISION: NOT TRUE. TAGS CAN REPEAT. EXAMPLE: many books in a library <book></book>
    THIS FUNCTION HAS BEEN UNCOMMENTED WHERE IT'S CALLED.
    :return: boolean
    """

    if len(find_duplicate_tags()) != 0:
        err.add_msg('no_duplicate_tags', 'Duplicate tags found: ', find_duplicate_tags())
        return False
    else:
        return True



# ****************************************************************************************************
#   CHECK THAT FILE STARTS WITH XML DECLARATION
# ****************************************************************************************************
def starts_with_xml_declaration(err):
    """
    Check that file starts with xml declaration
    :return: boolean
    """
    xml='<?xml'

    # Starts with xml declaration
    if getstring().startswith(xml):
        return True
    else:
        err.add_msg('starts_with_xml_declaration', 'XML file does not start with XML declaration.')
        return False


# ****************************************************************************************************
#   COMPARE OPENING AND CLOSING TAGS OF THE ROOT ELEMENT IF THEY MATCH
# ****************************************************************************************************

def root_tags_match(err):
    """ Compare opening and closing root element if they match.
    :return: boolean
    """
    # check if the names of the root tags match

    # clean opening and closing tag
    # in this case it means: transform tuple ("<example id=''>", '</example>') into <example, <example)
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
        err.add_msg('root_tags_match', 'Root tags don\'t match.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE IS NO SPACE BETWEEN AN OPENING BRACKET AND THE NAME OPENING TAGS
# ****************************************************************************************************
def no_initial_space_in_opening_tags(err):
    """
    Check there is no space between opening bracket and the name in opening tags
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == ' ':
            for i in get_line_numbers():
                if tag in i[1]:
                    # display line. Could display just the tag.
                    # But to be consistent, the whole affected line is displayed.
                    err.add_msg('no_initial_space_in_opening_tags', 'Space immediatelly after \'<\' not allowed. '
                                                                    'Line ' + str(i[0]) + ': ' + i[1])

            return False
    return True


# ****************************************************************************************************
#   CHECK THAT THERE NO SPACE IN CLOSING TAGS
# ****************************************************************************************************
def no_spaces_in_closing_tags(err):
    """
    Check that closing tags don't have spaces. INCLUDE SINGLE EMPTY TAGS!!!
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == '/' and ' ' in tag[1:]:
            err.add_msg('no_spaces_in_closing_tags', 'Closing tag must not have spaces.', tag)
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT CLOSING TAGS START WITH </
#  ****************************************************************************************************
def closing_tag_incorrectly_formed(err):
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
                err.add_msg('closing_tag_incorrectly_formed', 'Closing tag not formed correctly '
                                                              '(must start with \'</\' if tag has open tag counterpart '
                                                              'or end with \'/>\' if the tag is single): ', tag)
                return False
    return True


# ****************************************************************************************************
#   CHECK FOR INVALID CHARACTERS AT THE BEGINNING OF TAG NAME
# ****************************************************************************************************
def no_invalid_initial_characters_in_opening_tag(err):
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
            if tag[1:].startswith(char):         # BUG was here - first character can't have more than one character (xml, Xml, xMl, like list has)
                                                 # now fixed. Needs to be tested
                err.add_msg('no_invalid_initial_characters_in_opening_tag', 'Tag with invalid start character: ', tag)
                return False


    # Check that element names DO start with letter (uppercase or lowercase), underscore, or colon.
    for tag in get_all_tags_in_order():     #make sure that names starting with ? and ! pass through
        if tag[1] != '?' and tag[1] != '!' and \
            not tag[1].isalpha() and \
            not tag[1] == '_' and \
            not tag[1] == ':' and \
            not tag[1] == '/':
                err.add_msg('no_invalid_initial_characters_in_opening_tag', 'Element name should start with letter, underscore or colon: ', tag)
                return False
        # case for malformed single element
        if tag[1] != '?' and tag[1] != '!' and \
            tag[1] == '/' and tag.endswith('/>'): #and \
            #element_names_contain_only_valid_characters():
            err.add_msg('no_invalid_initial_characters_in_opening_tag', 'Element name should start with letter, underscore or colon: ', tag)
            return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT ELEMENT NAMES CONTAIN ONLY VALID CHARACTERS
# ****************************************************************************************************
def element_names_contain_only_valid_characters(err):
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
    if no_invalid_initial_characters_in_opening_tag(err) and no_initial_space_in_opening_tags(err):
        names = set(get_clean_tags())

        # if anything else but letters, digits, hyphens, underscores, colons or full stops in names return false
        #p = re.compile('[ A-Za-z0-9_:.-]*$')
        for name in names:
            if not re.match(r'[ A-Za-z0-9_:.-]*$', name):
                err.add_msg('element_names_contain_only_valid_characters',
                            'Element name contains invalid character(s) - allowed are letters, digits, _, :, ., - : ', name)
                return False
        return True

    else:
        err.add_msg('element_names_contain_only_valid_characters', 'Invalid initial character or disallowed initial space in opening tag.')
        return False


# ****************************************************************************************************
#   CHECK THAT ELEMENTS ARE CLOSED PROPERLY AND NAMES MATCH (PAIRED ELEMENTS, NOT SINGLE ONES)
# ****************************************************************************************************
def paired_elements_are_closed_properly_and_names_match(err):
    """
    Check that paired elements (not single ones) are closed properly.
    Based on the fact that number of < must match number of </.
    If it doesn't, then either < or </ are mis-formatted or are missing.
    :return: boolean
    """
    # This is only a preliminary partial check -> fails when there is even number of missing brackets of the same type!
    # The rest of the code below must run for complete check
    if not number_of_angle_brackets_is_even(err):
        err.add_msg('paired_elements_are_closed_properly_and_names_match',
                    'Elements not properly closed. Number of angle brackets is not even - tag(s) incorrectly formed.')
        return False

    if not number_of_opening_and_closing_brackets_match(err):
        err.add_msg('paired_elements_are_closed_properly_and_names_match',
                    'Numbers of opening and closing brackets don\'t match.')
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
            err.add_msg('paired_elements_are_closed_properly_and_names_match', 'Closing tag must not contain spaces.', tag)
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
        err.add_msg('paired_elements_are_closed_properly_and_names_match', 'Opening and closing bracket not matching.')
        return False
    # no space in closing tag
    if no_spaces_in_closing_tags(err) != True:
        err.add_msg('paired_elements_are_closed_properly_and_names_match', 'One or more closing tag(s) contains space.')
        return False

    # no space in opening tag
    if no_initial_space_in_opening_tags(err) != True:
        err.add_msg('paired_elements_are_closed_properly_and_names_match', 'One or more opening tag(s) contains space at the begining of the tag.')
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
        # check - always shows opening tag as without a match, even when closing one is problematic
        err.add_msg('paired_elements_are_closed_properly_and_names_match',
                    'The following opening tag names don\'t have a match: ', mismatching_tag_name_op)
        return False
    elif len(mismatching_tag_name_cl) != 0:
        err.add_msg('paired_elements_are_closed_properly_and_names_match' , 'The following closing tag names don\'t have a match: ', mismatching_tag_name_cl)
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT TAGS ARE CASE SENSITIVE - CURRENTLY WORKS FOR LOWERCASE
# ****************************************************************************************************
def all_lowercase_tags(err):
    """
    Check that tags are case sensitive.
    For now, ensure all tag names are lower case.
    :return: boolean
    """
    for tag in get_clean_tags():
        if not tag.islower():
            err.add_msg('all_lower_case', 'Incorrect tag name. Should be lower case: ', tag)
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT NESTING IS PROPER - DONE!
# ****************************************************************************************************
def is_nesting_proper(err):
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
            err.add_msg('is_nesting_proper', 'Incorrectly nested tag is \'' +temp_list[-1] +
                                             '\' or that tag needs to be a single tag ending with \'/>\'.')
            return False

    if len(temp_list) == 0:
        return True


# ****************************************************************************************************
#   IS NUMBER OF COMMENT TAGS EVEN
# ****************************************************************************************************
def is_number_of_comment_tags_even(err):
    """
    Check if number of commnt tags is even
    - utility function
    :return: boolean
    """
    if len(get_opening_comment_tag_positions() + get_closing_comment_tag_positions()) % 2 != 0:
        err.add_msg('is_number_of_comment_tags_even', 'Number of comment tags is not even.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT OPENING COMMENT TAG IS FOLLOWED BY CLOSING TAG
# ****************************************************************************************************
def is_comment_opening_tag_followed_by_closing_tag(err):
    """
    # Check that each opening comment tag is followed by closing tag
    Sequence of comment tags must follow: opening-closing_opening_closing.
    Disallow two of the same one after the other. This will check for nesting.
    :return: boolean
    """
    if is_number_of_comment_tags_even(err):
        l=[]
        # append position of opening tag then closing, then opening, then closing etc.
        # sequence must be strictly sorted in ascending order, otherwise this function test fails-False
        for i in range(len(get_opening_comment_tag_positions())):
            l.append(get_opening_comment_tag_positions()[i])
            l.append(get_closing_comment_tag_positions()[i])
        #print('SEQUENCE: ', l)
        if l != sorted(l):
            err.add_msg('is_comment_opening_tag_followed_by_closing_tag', 'Error in comment tags.')
            return False
        else:
            return True
    else:
        err.add_msg('is_comment_opening_tag_followed_by_closing_tag', 'Number of comment tags is not even - wrong nesting.')
        return False


# ****************************************************************************************************
#   CHECK THAT COMMENT CLOSING TAGS DONT HAVE EXTRA DASH (--->)
# ****************************************************************************************************
def comment_closing_tags_dont_have_extra_dash(err):
    """
    Check that comment closing tags don't have extra dash (--->).
    :return: boolean
    """
    if '--->' in getstring():
        err.add_msg('comment_closing_tags_dont_have_extra_dash', 'Comment tags should not have extra dash.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT CLOSING TAGS THAT ARE NOT SINGLE DON'T HAVE ATTRIBUTES
# ****************************************************************************************************
def closing_tags_that_are_not_single_dont_have_attributes(err):
    """
    Check that closing tags that are not single don't have attributes.
    Here the check is made on absence of spaces in closing tag.
    That automatically implies no attributes.
    :return: boolean
    """
    for tag in get_all_tags_in_order():
        if tag[1] == '/':
            if ' ' in tag:
                err.add_msg('closing_tags_that_are_not_single_dont_have_attributes',
                            'Closing tag (paired one) should not have an attribute.')
                return False
            else:
                return True


# ****************************************************************************************************
#   CHECK THAT SINGLE ELEMENTS ARE CORRECTLY FORMED - CASE WITHOUT ATTRIBUTE
# ****************************************************************************************************
def single_element_is_correctly_formed_case_without_attribute(err):
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
            err.add_msg('single_element_is_correctly_formed_case_without_attribute', 'Problematic single element - not correctly formed: ', tag)
            return False
        else:
            return True


# ****************************************************************************************************
#   CHECK THAT NO RESTRICTED CHARACTERS ARE PRESENT IN DATA CONTENT
# ****************************************************************************************************
def no_restricted_characters_in_content(err):
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
    if not number_of_angle_brackets_is_even(err):
        err.add_msg('no_restricted_characters_in_content',
                    'Elements not properly closed. Number of angle brackets is not even - tag(s) incorrectly formed.')
        return False

    if not number_of_opening_and_closing_brackets_match(err):
        err.add_msg('no_restricted_characters_in_content', 'Numbers of opening and closing brackets don\'t match.')
        return False

    # get content between tags (>  <)g
    # check that it doesn't contain any of the above characters
    restricted = [ '<', '>', '&' ]
    restricted_chars = [ char for char in get_data_content() for c in restricted if c in char ]
    if len(restricted_chars) != 0:
        err.add_msg('no_restricted_characters_in_content',
                    'Invalid characters (<, >, &) in data content: ', restricted_chars)
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE IS NOTHING BEFORE AND AFTER THE ROOT TAG
# ****************************************************************************************************
def no_invalid_content_after_root_tag(err):
    """
    And that there is nothing below the ending root tag
    :return: boolean
    """
    # check after the ending root tag
    last_char = getstring()[-1]
    after = getstring()[-1:]
    if last_char != '>' and after != '':
        err.add_msg('no_invalid_content_after_root_tag',
                    'Content after the ending root tag is disallowed. Even spaces - please delete them.')
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


#def run(sText, err):
def run():
    """
    Function to invoke the program
    :return: print statements: warnings and that file is well formed.
    """
#if get_clean_tags():
#   print(get_clean_tags(sText, err))
#    if not number_of_angle_brackets_is_even(): return
#    result, comment = number_of_angle_brackets_is_even()
#    if not result: return

if no_orphan_brackets(err):
    if number_of_angle_brackets_is_even(err):
        if number_of_opening_and_closing_brackets_match(err):
            if starts_with_xml_declaration(err):
                if root_tags_match(err):
                    if no_initial_space_in_opening_tags(err):
                        if no_invalid_initial_characters_in_opening_tag(err):
                            if element_names_contain_only_valid_characters(err):
                                if closing_tag_incorrectly_formed(err):
                                    if no_spaces_in_closing_tags(err):
                                        if paired_elements_are_closed_properly_and_names_match(err):
                                            if closing_tags_that_are_not_single_dont_have_attributes(err):
                                                if single_element_is_correctly_formed_case_without_attribute(err):
                                                    if all_lowercase_tags(err):
                                                        if is_nesting_proper(err):
                                                            if is_number_of_comment_tags_even(err):
                                                                if is_comment_opening_tag_followed_by_closing_tag(err):
                                                                    if comment_closing_tags_dont_have_extra_dash(err):
                                                                        if no_restricted_characters_in_content(err):
                                                                            if no_invalid_content_after_root_tag(err):
                                                                                print('Document is well formed!')


# run the program
run()

if err.count > 0:
    print(err.sText)

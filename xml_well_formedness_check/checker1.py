"""
    This project is a non-validating XML parser that checks well-formedness of XML files.
    author: Matjaz Pirnovar
    date: Feb-Mar 2015

    - DO LINE NUMBERS
    - get_all_tags_in_order() function blows up when brackets are out of place or extra/missing!
    (fixed by checking brackets first by functions: no_redundant_brackets, no_of_brackets_even, matching_brackets)
"""

from xml_well_formedness_check.utility_functions import utility
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
        self.count += 1
        self.sText += "\n============================================================="
        self.sText += "\nFrom " + s_src + ":\n" + s_msg.strip()      # strip cleans up any newline chars in messages for nicer display

# error object for printing warning messages
err = ErrorLog()

# ****************************************************************************************************
#   CHECK THAT DOCUMENT DOESN'T HAVE EXTRA-ORPHAN BRACKETS
# ****************************************************************************************************
def no_redundant_brackets(err, xmlstr, linenum):
    """
    Check that there are no orphan, single, obsolete, extra brackets.
    Each opening bracket should have a closing pair (<,>).
    Function checks that no two or more consecutive opening or closing brackets exist (<,< is incorrect).
    - every > must have < as the next bracket
    - every < must have > as the previous bracket
    - find places where these two rules are violated

    Steps:
    - get line numbers for all the brackets
    - compare two consecutive brackets
    - if they re the same, then one of them is orphan bracket
    - line number will depend on whether it's opening or closing bracket
    :return: boolean
    """
    # get line numbers for all the brackets
    brackets_line_numbers = []
    for tup in linenum:
        for char in tup[1]:
            if char == '<' or char == '>':
                #print(tup[0], char)
                brackets_line_numbers.append((tup[0], char))

    # compare two consecutive brackets
    # if they are the same, then one of them is orphan bracket
    # line number will depend on whether it's opening or closing bracket
    for ind, br in enumerate(brackets_line_numbers[:-1]):
        # IMPORTANT:
        # Two if statements:
        # first for consecutive opening brackets (<<). Uses br[0] to show line number.
        # second for consecutive closing brackets (>>). Uses brackets_line_numbers[ind+1][0] to show line number.
        # Function returns incorrect line number of erroneous bracket if above is ignored.
        if br[1] == '<' and brackets_line_numbers[ind+1][1] == '<':
            op = br[0]
            line_num, content = linenum[op-1] # -1, just indicates appropriate start of counting
            err.add_msg('no_redundant_brackets',
                        'Redundant, missing or nested empty bracket(s) on line ' + str(line_num) + ': ' + content.lstrip())
            return False
        if br[1] == '>' and brackets_line_numbers[ind+1][1] == '>':
            cl = brackets_line_numbers[ind+1][0]
            line_num, content = linenum[cl-1] # -1, just indicates appropriate start of counting
            err.add_msg('no_redundant_brackets',
                        'Redundant closing bracket(s) or empty nested brackets on line ' + str(line_num) + ': ' + content.lstrip())
            return False


    # check for empty tags

    # get all brackets with indexes
    count_br = [ (count, br) for count, br in enumerate(xmlstr) if br == '<' or br == '>' ]
    #print(count_br)

    zipped = zip(brackets_line_numbers, count_br)
    z = list(zipped)

    l=[]
    for i in z:
        a,b = i
        l.append((a[0], b[0], b[1]))  # gives triples [(1, 0, '<'), (1, 53, '>'), (2, 58, '<'),...]

    for ind, br in enumerate(l[:-1]):
        # variables
        space_between_brackets = xmlstr[br[1] + 1: l[ind + 1][1]]
        start_line = br[0]
        ending_line = l[ind + 1][0]
        start_line_content = linenum[start_line - 1][1]

        # if statements
        if space_between_brackets.isspace() and '\n' in space_between_brackets \
                                            and br[2] == '<' and l[ind+1][2] == '>':
            err.add_msg('no_redundant_brackets',
                        'Empty tag starting on line ' + str(start_line) + ' and ending on line ' + str(ending_line) + '.')
            return False
        elif space_between_brackets.isspace() and br[2] == '<' and l[ind+1][2] == '>':
            err.add_msg('no_redundant_brackets',
                        'Empty tag on line ' + str(start_line) + ': ' + start_line_content.strip())
            return False
        elif space_between_brackets == '' and br[2] == '<' and l[ind+1][2] == '>':
            err.add_msg('no_redundant_brackets',
                        'Empty tag(s) on line ' + str(start_line) + ': ' + start_line_content.strip())
            return False

    return True


# ****************************************************************************************************
#   CHECK THAT NUMBER OF < and > IS EVEN
# ****************************************************************************************************

#  LINE NUMBERS !!!!!!!!!!!!!!!!!!!!!!!!! - BUT how to define the affected line?

def number_of_angle_brackets_is_even(err, xmlstr):
    """
    Check that number of angle brackets (<,>) is even.
    PS: Not a full test of matching brackets! For example even number of closing brackets
    could be missing or be added and the number would still be even.
    :return: sum of all angle brackets (as length of the list)
    """
    number_of_all_angle_brackets = len([char for char in xmlstr if char == '<' or char == '>'])
    if number_of_all_angle_brackets % 2 != 0:
        err.add_msg('number_of_angle_brackets_is_even', 'No of angle brackets is not even (' + str(number_of_all_angle_brackets) + ') '
                                                        'Check that brackets correctly surround tags.')

        return False
    else:
        return True

# ****************************************************************************************************
#   CHECK THAT NUMBERS OF < and > MATCH
# ****************************************************************************************************

#  LINE NUMBERS !!!!!!!!!!!!!!!!!!!!!!!!! - BUT how to define the affected line?

def number_of_opening_and_closing_brackets_match(err, xmlstr):
    """
    Get number of opening and closing brackets and compare if the number matches.
    :return: boolean
    """
    open = xmlstr.count('<')
    clos = xmlstr.count('>')

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
#   CHECK THAT FILE STARTS WITH XML DECLARATION
# ****************************************************************************************************
def starts_with_xml_declaration(err, xmlstr, linenum):
    """
    Check that file starts with xml declaration
    :return: boolean
    """
    xml='<?xml'

    # get number of the first line: 1
    first_line_number = linenum[0][0]
    first_line_content = linenum[0][1]

    # Starts with xml declaration
    if xmlstr.startswith(xml):
        return True
    else:
        err.add_msg('starts_with_xml_declaration', 'XML file does not start with XML declaration. '
                                                   'Line ' + str(first_line_number) + ': ' + first_line_content)
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
    opening = utility.get_root_element()[0] # get opening tag

    # get tag name from < to first whitespace and
    # get tag name from < to >
    first_space = opening.find(' ')
    no_space = opening.find('>')
    opening_if_space = opening[1:first_space]
    opening_if_no_space = opening[1:no_space]

    if ' ' in opening: opening = opening_if_space
    elif ' ' not in opening: opening = opening_if_no_space

    closing = utility.get_root_element()[1].replace('/', '')    # ignore forward slash in closing tag
    closing = closing[1:-1]     # get closing tag's name

    # now tags should be in clean form to be compared (eg example, example)
    if opening != closing:

        # get line number and content
        op_number, op_line = 0, ''
        cl_number, cl_line = 0, ''
        root_el=utility.get_root_element()
        for e in utility.line_numbers:
            if root_el[0] in e[1] :
                op_number, op_line =  e
            if root_el[1] in e[1]:
                cl_number, cl_line = e

        err.add_msg('root_tags_match', 'Root tags don\'t match on:\n'
                    + 'line ' + str(op_number) + ': ' + op_line.strip() +
                    '\nline ' + str(cl_number) + ': ' + cl_line.strip())
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE ARE NO SPACE IN CLOSING TAGS
# ****************************************************************************************************
def no_spaces_or_attributes_in_closing_tags(err, tags_order):
    """
    Check that paired (non-empty) closing tags don't have spaces.
    :return: boolean
    """
    for tag in tags_order:
        if (tag[1] == '/' and ' ' in tag[1:]):

            # get line number and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e

            err.add_msg('no_spaces_or_attributes_in_closing_tags',
                        'Closing tag must not have spaces or attributes. Line ' + str(num) + ': ' + content.strip())
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT CLOSING TAGS START WITH </
#  ****************************************************************************************************
def closing_tag_must_start_with_forward_slash(err):
    """
    Check that closing tags start with '</' .
    :return: boolean
    """
    tags = utility.remove_declaration_doctype_comments()

    # for paired closing tags
    without_singles = [tag for tag in tags if '/>' not in tag]

    for tag in without_singles:
        # if it has '/' it should be immediatelly after <
        if '/' in tag:
            if not tag.startswith('</'):

                # get line numbers and line content
                num, content = 0, ''
                for e in utility.line_numbers:
                    if tag in e[1]:
                        num, content = e

                err.add_msg('closing_tag_must_start_with_forward_slash',
                            'Closing tag must start with forward slash '
                            'if tag has open tag counterpart (non-empty element) \n'
                            'or end with \'/>\' if the tag is single (empty element). \n'
                            'Line ' + str(num) + ': ' + content.strip())
                return False
    return True


# ****************************************************************************************************
#   CHECK FOR INVALID CHARACTERS AT THE BEGINNING OF TAG NAME
# ****************************************************************************************************
def no_invalid_initial_characters_in_opening_tag(err, tags_order):
    """
    Element names must not start with digits, diacritics, the full stop, the hyphen and 'xml' (any letter case).
    Element names must start with letter (uppercase or lowercase), underscore, or colon.
    :return: boolean
    """

    # Check that element names DO NOT start with digits, diacritics, the full stop,
    # the hyphen and 'xml' (any letter case).
    # I left diacritics requirement out for the moment
    invalid_start_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ,
                                '.', '-', 'xml', 'XML', 'Xml', 'xMl', 'xmL', 'XMl', 'xML', ' ']

    for tag in tags_order:
        for char in invalid_start_characters:
            if tag[1:].startswith(char):

                # get line number and line content
                num, content = 0, ''
                for e in utility.line_numbers:
                    if tag in e[1]:
                        num, content = e

                err.add_msg('no_invalid_initial_characters_in_opening_tag',
                            'Invalid start character (including space) on line ' + str(num)
                            + ': ' + content.strip())
                return False


    # Valid start characters
    # Check that element names DO start with letter (uppercase or lowercase), underscore, or colon.
    for tag in tags_order:     #make sure that names starting with ? and ! pass through
        if tag[1] != '?' and tag[1] != '!' and \
            not tag[1].isalpha() and \
            not tag[1] == '_' and \
            not tag[1] == ':' and \
            not tag[1] == '/':

            # get line number and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e
            err.add_msg('no_invalid_initial_characters_in_opening_tag',
                            'Element name should start with letter, underscore or colon on line ' +
                            str(num) + ': ' + content.strip())
            return False

        # case for malformed single element
        if tag[1] != '?' and tag[1] != '!' and \
            tag[1] == '/' and tag.endswith('/>'):

            # get line number and line content (for this problematic tag)
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e

            err.add_msg('no_invalid_initial_characters_in_opening_tag',
                        'Element name should start with letter, underscore or colon. '
                        '\nOr ambiguity if this is a closing tag or a single element. On line ' +
                        str(num) + ': ' + content.strip())
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
    names = set(utility.get_clean_tags())
    # if anything else but letters, digits, hyphens, underscores, colons or full stops in names return false
    #p = re.compile('[ A-Za-z0-9_:.-]*$')
    for name in names:
        if not re.match(r'[ A-Za-z0-9_:.-]*$', name):

            # get line numbers and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if name in e[1]:
                    num, content = e

            err.add_msg('element_names_contain_only_valid_characters',
                        'Element name contains invalid character (allowed are letters, digits, _, :, ., -). '
                        'On line ' + str(num) + ': ' + content.strip())
            return False
    return True


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
    # start by getting clean tags
    clean = utility.get_clean_tags()

    # add unpaired items to a list
    unpaired_tags = []
    for item in clean:
        if item not in unpaired_tags:
            unpaired_tags.append(item)
        elif item in unpaired_tags:
            unpaired_tags.remove(item)

    # get elements that are unique - that are shown only once (ignoring duplicates)
    print('UNPAIRED TAGS: ', unpaired_tags)
    # retrieve full tag structures of unpaired tags. So I can check if they are in line numbers lines.
    # Shortened version (ie l vs <    l > may be problematic when finding line number and content.

    # make list of tuples: (index of a tag, tag name)
    numbered=[]
    l1 = [ (ind, tag) for ind, tag in enumerate(clean) ]
    for i in l1:
        for t in unpaired_tags:
            if t == i[1]:
                numbered.append(i)

    # et tuples of index and tag for full tags in order without comments
    all_tags = [ (ind, tag) for ind, tag in enumerate(utility.remove_declaration_doctype_comments()) ]

    # get full tags by intersecting indexes of all tags and numbered
    full_tags =[]
    for n in numbered:
        for a in all_tags:
            if n[0] == a[0]:
                full_tags.append(a[1])

    # get line number and content from full tags
    num, content = 0, ''
    for tag in full_tags:
        for e in utility.line_numbers:
            if tag in e[1]:
                num, content = e
                # move err.add_msg block into outer for loop scope
                # if you want to display one error message at the time, instead of all of them
                err.add_msg('paired_elements_are_closed_properly_and_names_match. ',
                            'Tag \'' + tag + '\' doesn\'t have a match. On line ' + str(num) + ': ' + content.strip())


# ****************************************************************************************************
#   CHECK THAT TAGS ARE CASE SENSITIVE - CURRENTLY WORKS FOR LOWERCASE
# ****************************************************************************************************
def all_lowercase_tags(err, tags_order):
    """
    Check that tags are case sensitive.
    For now, ensure all tag names are lower case.
    :return: boolean
    """
    for tag in tags_order:

        # empty tag is already checked in no_redundant_brackets(). Do I then really need this section?
        # Check if there is realy a reason for this check of empty brackets.
        if tag == '<>' or tag[1:-1].isspace():

            # get line numbers and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e

            err.add_msg('all_lower_case', 'Found empty tag on line ' + str(num) + ': ' + content.strip())
            return False

        if not tag.islower() and tag[1] != '?' and tag[1] != '!':

            # get line numbers and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e

            err.add_msg('all_lower_case',
                        'Tag should be lower case on line ' + str(num) + ': ' + content.strip())
            return False
    return True


# ****************************************************************************************************
#   CHECK THAT NESTING IS PROPER
# ****************************************************************************************************

#  DEBUG !!!!!

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
    tags = utility.remove_declaration_doctype_comments()

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
            # get line numbers and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if temp_list[-1] in e[1]:
                    num, content = e

            err.add_msg('is_nesting_proper',
                        'Incorrectly nested tag is \'' + temp_list[-1] +
                        '\' or that tag needs to be a single tag ending with \'/>\'.'
                        '\nLine ' + str(num) + ': ' + content.strip())
            return False

    if len(temp_list) == 0:
        return True


# ****************************************************************************************************
#   IS NUMBER OF COMMENT TAGS EVEN
# ****************************************************************************************************

#  LINE NUMBERS !!!!!!!!!!!!!!!!!!!!!!!!! HOW? DOESN'T NEED LINE NUMBERS?

def is_number_of_comment_tags_even(err):
    """
    Check if number of commnt tags is even
    - utility function
    :return: boolean
    """
    if len(utility.get_opening_comment_tag_positions() + utility.get_closing_comment_tag_positions()) % 2 != 0:
        err.add_msg('is_number_of_comment_tags_even', 'Number of comment tags is not even.')
        return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT COMMENT CLOSING TAGS DONT HAVE EXTRA DASH (--->)
# ****************************************************************************************************
def comment_closing_tags_dont_have_extra_dash(err, xmlstr):
    """
    Check that comment closing tags don't have extra dash (--->).
    :return: boolean
    """
    if '--->' in xmlstr:

        # get line numbers and line content
        num, content = 0, ''
        for e in utility.line_numbers:
            if '--->' in e[1]:
                num, content = e

        err.add_msg('comment_closing_tags_dont_have_extra_dash',
                    'Too many dashes in the closing tag in the comment. Line ' + str(num) + ': ' + content.strip())
        return False
    else:
        return True


''' THIS FUNCTION IS ALREADY ADDRESSED WITH OTHER FUNCTIONS - CHECK IF THERE IS ANYTHING IT COULD BE USEFUL FOR
# ****************************************************************************************************
#   CHECK THAT SINGLE ELEMENTS ARE CORRECTLY FORMED - CASE WITHOUT ATTRIBUTE
# ****************************************************************************************************
def single_element_is_correctly_formed_case_without_attribute(err):
    """
    Check that single elements are correctly formed.
    Examples: <example/> <br       />, <acb />, <child attribute="value" /> - THESE ARE ALL VALID

    # Done so far:
    # Includes proper closure!
    # Not checking for space between name and /> because it is allowed. It's for attributes, which still need to be checked.
    # checking that there is no space between / and >
    # first part of the tag <... is already checked because functions no_initial_space_in_opening_tags(), ... take car of it
    # closing tag /> is validated here - no space between / and >
    # in between it's okay to have space - for attribute - which still need to be checked
    :return: boolean
    """

    # test the correctness of the single tag (if '/' at the end before >)
    for tag in utility.get_single_elements():
        if not tag.endswith('/>') or tag.startswith('< '):

            # get line numbers and line content
            num, content = 0, ''
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e

            err.add_msg('single_element_is_correctly_formed_case_without_attribute',
                        'Incorrectly formed single element on line ' + str(num) + ': ' + content.strip())
            return False
        else:
            return True
'''

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
    # get content between tags (>  <)g
    # check that it doesn't contain any of the above characters
    # < and > will already be checked by no_redundant_brackets() unless a proper tag is formed
    # (but in that case content data changes into a tag)
    restricted = [ '<', '>', '&' ]
    restricted_chars = [ char for char in utility.get_data_content() for c in restricted if c in char ]
    if len(restricted_chars) != 0:

        print('RESTRICTED CHARS: ', restricted_chars)
        # get line numbers and line content
        num, content = 0, ''
        for tag in restricted_chars:
            for e in utility.line_numbers:
                if tag in e[1]:
                    num, content = e
                    err.add_msg('no_restricted_characters_in_content',
                                'Invalid characters (<, >, &) in data content on line: '
                                + str(num) + ': ' + content.strip())

            return False
    else:
        return True


# ****************************************************************************************************
#   CHECK THAT THERE IS NOTHING BEFORE AND AFTER THE ROOT TAG
# ****************************************************************************************************

# FIX DISPLAY!!!!!! AND THEN DONE!

def no_invalid_content_after_root_tag(err, xmlstr):
    """
    And that there is nothing below the ending root tag
    :return: boolean
    """

    print(utility.line_numbers[-1:])
    # check after the ending root tag
    last_char = xmlstr[-1]
    after = xmlstr[-1:]
    if last_char != '>' and after != '':
        #utility.line_numbers[:-1]
        err.add_msg('no_invalid_content_after_root_tag',
                    'Content after the ending root tag is disallowed. Even spaces - please delete them.'
                    '\nOn line ' + str(utility.line_numbers[-1:][0]) + ': ' + str(utility.line_numbers[-1:]))
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
    # if - check is needed first to sort out angle brackets.
    # two vital functions depend on this (get_all_tags_in_order() and get_clean_tags())
    if no_redundant_brackets(err, xmlstr=utility.xml_string, linenum=utility.line_numbers) and \
       number_of_angle_brackets_is_even(err, xmlstr=utility.xml_string) and \
       number_of_opening_and_closing_brackets_match(err, xmlstr=utility.xml_string):

        no_invalid_initial_characters_in_opening_tag(err, tags_order=utility.get_all_tags_in_order())
        no_spaces_or_attributes_in_closing_tags(err, tags_order=utility.get_all_tags_in_order())
        starts_with_xml_declaration(err, xmlstr=utility.xml_string, linenum=utility.line_numbers)
        root_tags_match(err)
        element_names_contain_only_valid_characters(err)
        closing_tag_must_start_with_forward_slash(err)
        paired_elements_are_closed_properly_and_names_match(err)
        #single_element_is_correctly_formed_case_without_attribute(err)
        all_lowercase_tags(err, tags_order=utility.get_all_tags_in_order())
        is_nesting_proper(err)
        is_number_of_comment_tags_even(err)
        #is_comment_opening_tag_followed_by_closing_tag(err)
        comment_closing_tags_dont_have_extra_dash(err, xmlstr=utility.xml_string)
        no_restricted_characters_in_content(err)
        no_invalid_content_after_root_tag(err, xmlstr=utility.xml_string)


# run the program
run()

if err.count > 0:
    print(err.sText.strip())
else:
    print('Document is well formed!')



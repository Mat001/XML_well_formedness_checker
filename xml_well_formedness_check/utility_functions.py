"""
Utility functions for xml well formedness checker.
They provide helpful functionality but don't perform direct checking of the xml file.
"""

import logging
import sys

# ****************************************************************************************************
#   GET XML STRING -READ FROM FILE - utility function
# ****************************************************************************************************
def getstring():
    """
    put xml content from file into a string (also make sure you use try/except!)
    :return: xml_string
    """
    logging.basicConfig(level=logging.DEBUG)

    xml_string = ''

    try:
        with open('/home/matjaz/PycharmProjects/xml_well_formedness_check/'
                  'xml_well_formedness_check/xml_example.txt', 'r') as f:
            for i in f:
                xml_string = xml_string + i
        return xml_string
    except IOError as e:
        logging.error(e)
        logging.error(sys.exc_info())


# ****************************************************************************************************
#   GET ALL TAGS - utility function
# ****************************************************************************************************
def get_all_tags_in_order():
    """
    [ IMPORTANT:  ASSUMES THAT ALL ANGLE BRACKETS ARE PRESENT!!! AND THAT THERE ARE NO EXTRA ANGLE BRACKETS!
    IF IN DOUBT THEN CHECK THAT ALL ANGLE BRACKETS ARE OKAY FIRST.]

    Get all tags (opening, closing) in order of appearance top down
    Procedure:
    get positions of opening and closing brackets
    pair up tag positions into list of tuples
    get a list of all tags
    :return: list of tags in order (top down)
    """

    # get positions of opening and closing brackets
    opening_bracket_positions = [i for i, char in enumerate(getstring()) if char == '<']
    closing_bracket_positions = [i for i, char in enumerate(getstring()) if char == '>']

    # pair up tag positions into list of tuples
    zipped = zip(opening_bracket_positions, closing_bracket_positions)
    zipped = list(zipped)

    # get a list of all tags
    result = [ getstring()[i[0] : i[1]+1] for i in zipped ]
    return result


# ****************************************************************************************************
#   REMOVE DECLARATIONS, DOCTYPE AND COMMENTS - utility function
# ****************************************************************************************************
def remove_declaration_doctype_comments():
    """
    Removes xml declartion, doctype and comment tags for easier processing of remaining elements.
    :return: list of elements
    """
    # clean up tags from scratch and remove single elements (they don't affect nesting)
    without_declarations_and_comments = get_all_tags_in_order()

    for item in get_all_tags_in_order():
        if '<!' in item:
            without_declarations_and_comments.remove(item)
            # print(without_declarations_and_comments)
        if '<?' in item:
            without_declarations_and_comments.remove(item)
            # print(without_declarations_and_comments)

    return without_declarations_and_comments


# ****************************************************************************************************
#   CLEAN TAGS - utility function
# ****************************************************************************************************
def get_clean_tags():
    """

    [ IMPORTANT:  ASSUMES THAT ALL ANGLE BRACKETS ARE PRESENT!!! AND THAT THERE ARE NO EXTRA ANGLE BRACKETS!
    IF IN DOUBT THEN CHECK THAT ALL ANGLE BRACKETS ARE OKAY FIRST.
     FOR EXAMPLE IF THERE IS EXTRA SINGLE COMMENT TAG, THIS WILL FAIL

     - RUN is_number_of _angle_brackets_even() function first! User needs to fix that first, then run this function.
     ]

    Get all tags
    Clean up so you get a list of element names in order as they appear in xml file top-down
    :return: list
    """
    # get all tags and clean them up
    without_declarations_and_comments = get_all_tags_in_order()

    for item in get_all_tags_in_order():
        #if '-->' in item:         # CAN't FIND AND REMOVE IT!' # ????  --\\> DOES SOMETHING?
         #   without_declarations_and_comments.remove(item)
          #  print('STSTSTST ', without_declarations_and_comments)
        if '<!' in item:
            without_declarations_and_comments.remove(item)
            #print(without_declarations_and_comments)
        if '<?' in item:
            without_declarations_and_comments.remove(item)
            #print(without_declarations_and_comments)

    # remove opening and closing forward slashes (but dont remove any slashes in the name itself!)
    no_slash = [ tag.replace('</', '<') for tag in without_declarations_and_comments ]
    no_slash = [tag.replace('/>', '>') for tag in no_slash]

    split = [tag.split() for tag in no_slash]   # problem: if I split when tag has initial space, it doesn't work. Gives '' for < from >
    first_part = [part[0] for part in split]

    clean = []
    for tag in first_part:
        tag = tag.strip('<')
        tag = tag.strip('>')
        clean.append(tag)

    return clean


# ****************************************************************************************************
#   GET THE ROOT ELEMENT - utility function
# ****************************************************************************************************
def get_root_element():
    """
    Get the root element:
    Iterate through all tags (provided by get_all_tags_in_order() function )
    Get the first tag that doesn't have ? or ! after opening bracket
    Get the very last tag
    :return: root element tuple
    """
    root_opening, root_closing='', ''

    # get the first tag that doesn't have ? or ! after opening bracket
    for i, tag in enumerate(get_all_tags_in_order()):
        if not (tag.startswith('<?') or tag.startswith('<!')):  # inore XML declaration and DTD declar that start with '?' and '!'
            root_opening = tag
            break

    # get the very last tag
    for i, tag in enumerate(get_all_tags_in_order()):
        if tag.endswith('>') and i+1 == len(get_all_tags_in_order()):
            root_closing = tag
            break

    return root_opening, root_closing


# ****************************************************************************************************
#   GET OPENING COMMENT TAG POSITIONS - utility function
# ****************************************************************************************************
def get_opening_comment_tag_positions():
    """
    Get comment tag positions (for opening and closing comment tags).
    - utility function
    :return: list of tuple pairs [(opening1, closing1), ...]
    """
    # get indexes of all opening tags for comments
    comm_opening = [ i for i in range(len(getstring())) if getstring().startswith('<!--', i) ]
    #print('OPENING: ', comm_opening)
    return comm_opening


# ****************************************************************************************************
#   GET CLOSING COMMENT TAG POSITIONS - utility function
# ****************************************************************************************************
def get_closing_comment_tag_positions():
    # get indexs of all closing tags for comments
    comm_closing = [j for j in range(len(getstring())) if getstring().startswith('-->', j)]
    #print('CLOSING: ', comm_closing)
    return comm_closing


# ****************************************************************************************************
#   GET SINGLE ELEMENTS - utility function
# ****************************************************************************************************
def get_single_elements():
    """
    Get single elements (eg <example/> <br       />, <acb />, <child attribute="value" />)
    :return: list of single elements in order of appearance in xml file (top down)
    """
    # get all tags and clean them up
    tags = remove_declaration_doctype_comments()

    # dump singles in a list
    list_of_singles = [ tag for tag in tags if tag.endswith('/>') ]

    # what about singles that don't end with />, like errors such as <br >
    # what about when I have two or more of same (or diff) singles that don't end with /> like <br >, <br >
    return list_of_singles


# ****************************************************************************************************
#   GET DATA CONTENT
# ****************************************************************************************************
def get_data_content():
    """
    TRICKY: < and > in content THROW OFF get_clean_tags() FUNCTION INDEX OUT OF RANGE.
    MAYBE DO FUNCTIONS THAT CHECK FOR EVEN NUMBER OF TAGS ETC FIRST.

    Get data content of each element.
    SImilar to workings of get_all_tags_in_order function.
    :return: list of strings for content in between element tags
    """
    # get positions of opening and closing brackets BUT EXCLUDE ALL TAGS PRIOR TO ROOT ELEMENT.
    # Only take what's inside the root element.

    # assumes the first char is opening bracket and skips to count from the second one on
    # because we need to count like this: ((first closing br, second opening br), (second closing, third opening) etc)
    opening_bracket_positions = [i for i, char in enumerate(getstring()[1:]) if char == '<'
                                    and not char.startswith('<?') and not char.startswith('<!') ]
    closing_bracket_positions = [i for i, char in enumerate(getstring()) if char == '>'
                                    and not char.startswith('<?') and not char.startswith('<!')]

    # pair up closing and opening tag positions into list of tuples
    zipped = zip(closing_bracket_positions, opening_bracket_positions)
    zipped = list(zipped)

    # get content in between closing and opening tag (excluding brackets signs)
    content = [getstring()[ i[0]+1 : i[1]+1 ] for i in zipped]
    return content


# ****************************************************************************************************
#   GET NUMBER OF ALL TAGS EXCLUDING DECLARATIONS, DOCTYPE AND COMMENTS - utility function
# ****************************************************************************************************
def get_number_of_all_tags_excluding_declar_doctype_comments():
    # get all tags and clean them up
    without_declarations_and_comments = get_all_tags_in_order()

    for item in get_all_tags_in_order():
        if '<!' in item:
            without_declarations_and_comments.remove(item)
            #print(without_declarations_and_comments)
        if '<?' in item:
            without_declarations_and_comments.remove(item)
            #print(without_declarations_and_comments)

    return len(without_declarations_and_comments)


# ****************************************************************************************************
#   FIND DUPLICATE TAGS - utility function
# ****************************************************************************************************
def find_duplicate_tags():
    """
    Find duplicate tags.
    :return: list of duplicate tags
    """
    without_declarations_and_comments = get_all_tags_in_order()

    for item in get_all_tags_in_order():
        if '<!' in item:
            without_declarations_and_comments.remove(item)
            # print(without_declarations_and_comments)
        if '<?' in item:
            without_declarations_and_comments.remove(item)
            # print(without_declarations_and_comments)

    without_singles = [tag for tag in without_declarations_and_comments if '/>' not in tag]

    duplicates = set([tag for tag in without_singles if without_singles.count(tag) > 1])
    duplicates = list(duplicates)

    return duplicates

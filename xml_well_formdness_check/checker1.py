"""
    (SPHINX AUTOGENERATED DOC - FAILS FINDING xml_example.txt FILE !!!!!!! - FIX.)
    (htmldom is a nice xml/html parsing python code: source code is interesting-it's in downloads folder)

    This project is a program to validate well-formdness of XML files.
    author: Matjaz Pirnovar

    Rules:
    XML file must start with XML declaration.
        Example: <?xml version="1.0" encoding="UTF-8" standalone="no"?>
D   Must be only one root element and needs to have opening and closing tag.
    Child elements (except XML declar. and !DOCTYPE (any others??)) need to be within the root element as its children.
    Nested child elements need to be within their parents.
    Elements must be properly nested.
    Elements can have opening and closing tag AND can be single!
        <tag></tag>, <dd/>, <acb />, <child attribute="value" />
        (IMPORTANT - NOTE THIS LAST THREE SINGLE EMPTY TAGS - DON'T HAVE THEIR PAIRS!)
    Single elements are empty and have forward slash before closing bracket.
    Single elements can contain attributes.

    Element names must not start with digits, diacritics, the full stop, the hyphen and 'xml' (any letter case).
    Element names must start with letter (uppercase or lowercase), underscore, or colon.
    Element names can contain colon, hyphen-minus, full stop (period), low line (underscore), and middle dot.
    Element names must not contain spaces (<dateofbirth> is correct, <date of birth> is incorrect ).
        Permitted:
            axiom
            _axiom_26
            :axiom_veintiséis
            ora:open.source

            All of these names begin with a letter, an underscore, or a colon,
            followed by any combination of letters, digits, underscores, colons, and periods.
        Not permitted:

            #axiom
            @axiom
            26th_of_month
            axiom#26

            The first three begin with something other than a letter, underscore, or colon; the last starts out all right,
            but falls apart because the # is not a legitimate name character.

    Must be no space between opening bracket and the name of an element.
    Element names must be the same in opening and closing tag.
    Elements must be closed properly: <child>Data</child>, <child attribute="value" />
D   Tags are case sensitive.
    Attributes must have both quotation marks around attribute's value.
    Comments must be within comment tags <!-- -->.
    Comments are not allowed to end with --->.
    An attribute name must not appear more than once in the same start tag.
    Closing tags don't have attributes.
    Attribute values must not contain entity references to external entities.
    '<' character is not allowed in attribute values. ('>' is allowed????)
    All data content must be within element tags (not inside tags).
    XML must allow multiple whitespace characters.
    There may be whitespace between the end of the name or attribute in an opening element tag and the closing
    bracket of that element.
        Example: <body   > is allowed
    Characters to escape in XML - should not appear in xml document content- do flag error, except if replaced
    by char. entity reference:
            "   &quot;
            '   &apos;
            <   &lt;
            >   &gt;
            &   &amp;
    Doctype (DTD) declaration: <!DOCTYPE greeting SYSTEM "hello.dtd">
        Recommended doctype declarations: http://www.w3.org/QA/2002/04/valid-dtd-list.html
        Example why DTD is important:
            If you have created your own XML elements, attributes, and/or entities, then you should create a DTD.
            A DTD consists of a list of syntax definitions for each element in your XML document.
            When you create a DTD, you are creating the syntax rules for any XML document that uses the DTD.
            You are specifying which element names can be included in the document, the attributes that each
            element can have, whether or not these are required or optional, and more.
    Ensure CDATA applies (data is not parsed).
    CDATA sections may occur anywhere character data may occur (in between tags).

    Processing instructions (PI) should not start with 'xml'
    Referencing CSS example: <?xml-stylesheet type="text/css" href="tutorials.css"?>. Check that instead of href,
    a path to file can be used too
    Referencing scripts example: <script type="text/javascript">
    Referencing images
    Referencing links
    Referencing Schemas (XSD)
"""


def getstring():
    """
    put xml content from file into a string (also make sure you use try/except!)
    :return: xml_string
    """
    xml_string = ""
    with open('xml_example.txt', 'r') as f:
        for i in f:
            xml_string = xml_string + i
        return xml_string


# ****************************************************************************************************
#   CHECK THAT FILE STARTS WITH XML DECLARATION
# ****************************************************************************************************
def starts_with_xml_declaration():
    # if anything before '<?xml' check that that is a comment
    xml='<?xml'

    if getstring().startswith(xml):
        #print('XML file immediately starts with XML declaration.')
        return True
    elif getstring()[:getstring().index(xml)].startswith('<!--')\
        and getstring()[:getstring().index(xml)].strip().endswith('-->'):
        #print("XML file starts with a comment(s) and then with XML declaration.")
        return True
    else:
        #print('XML file doesn not start with XML declaration.')
        return False


print('Starts with xml declaration: ', starts_with_xml_declaration())



# ****************************************************************************************************
#   CHECK THAT NUMBER OF < and > IS EVEN
# ****************************************************************************************************

def number_of_angle_brackets_is_even():
    """
    Check that number of angle brackets (<,>) is even.
    :return: sum of all angle brackets (as length of the list)
    """
    number_of_all_angle_brackets = len([char for char in getstring() if char == '<' or char == '>'])
    return number_of_all_angle_brackets

print('Number of angle brackets (even?): ', number_of_angle_brackets_is_even())


# ****************************************************************************************************
#   GET ALL TAGS
# ****************************************************************************************************

def get_all_tags_in_order():
    """
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

#print('All tags in order: ', get_all_tags_in_order())



# ****************************************************************************************************
#   CHECK THAT XML FILE HAS TWO IDENTICAL NAMES FOR EACH ELEMENT (for OPENING AND CLOSING TAG)
# ****************************************************************************************************

def each_element_has_strictly_two_identical_names_for_each_tag():
    """
    More of a helper function.
    Checks that all tag names, opening and closing have their corresponding pair.
    For example, there should not be three names for an element, but strictly two (opening and closing)
    :return: boolean True or False
    """
    l = [ get_all_tags_in_order().count(i) for i in get_all_tags_in_order() ]
    if min(l) < 2 or max(l) > 2:
        return False
    else:
        return True

print('Two identical names for each element:', each_element_has_strictly_two_identical_names_for_each_tag())


# ****************************************************************************************************
#   GET THE ROOT ELEMENT
# ****************************************************************************************************

# get the root element
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

print('Root element: ', get_root_element())


# ****************************************************************************************************
#   COMPARE OPENING AND CLOSING TAGS OF THE ROOT ELEMENT IF THEY MATCH
# ****************************************************************************************************

def root_tags_match():
    """ Compare opening and closing root element if they match.
    """
    # check if the names of the root tags match

    # clean opening and closing tag
    # inthis case it means: transform tuple ("<example id=''>", '</example>') into <example, <example)
    opening = get_root_element()[0] # get opening tag
    opening = opening.split()[0]    # ignore any attributes and closing bracket

    closing = get_root_element()[1].replace('/', '')    # get closing tag and ignore forward slash
    closing = closing.split('>')[0] # ignore closing bracket

    # now tags should be in clean form to be compared (eg <example, <example)
    if opening == closing:
        return True
    else:
        return False


print('Root element tags match: ', root_tags_match())



# ****************************************************************************************************
#   DOES TAG HAVE A CORRECT ATTRIBUTE
# ****************************************************************************************************

def is_attribute_correctly_formed(tag):     # chnge this, to not having to enter a parameter
                                            # but instead function checks all attributes at once
    """
    Only checks if attribute is properly formed, not spaces before the atrribute name.
    """
    # POLISH - NEEDS DEFINE WELL WHAT ATTRIBUTE IS
    attribute = False
    # ALSO VALIDATE AGAINST THAT ATTRIBUTE HAS BOTH QUOTES, STARTING AND ENDING
    if ('\"' in tag and '=' in tag and tag.index('=') < tag.index('\"')): attribute = True
    if ('\'' in tag and '=' in tag and tag.index('=') < tag.index('\'')): attribute = True

    # get tags where tag name goes straight into equals sign without spaces - PUT IN IT'S OWN FUNCTION?????
    if ' ' not in tag and '=' in tag:
        print(tag, 'Equals sign can\'t be part of xml tag name.')
        attribute = False

    return attribute


print('Does a tag have a correctly formed attribute:')
#for tag in get_all_tags_in_order():
    #print(tag, is_attribute_correctly_formed(tag))



# ****************************************************************************************************
#   CHECK THERE ARE NO SPACES IN TAG NAMES
# ****************************************************************************************************

def no_spaces_in_tag_names():   # no spaces in the first part of the term right after the <
    """
    # separate illegal tags with spaces from legal tags with attributes
    # it will be attribute if it contains at least equal sign or two quotes or both

    # it's an attribute if after compact term and after whitespace it has equal sign and/or quote(s)
    # to follow style: <term attribute="">

    # exclude closing tags with space
    # function exits as soon as it hits the first tag with illegal space (doesn't do remaining tags)
    """

    # get all tags that have at least one whitespace
    tags_spaces = [tag for tag in get_all_tags_in_order() if ' ' in tag[1:]]
    # print(tags_spaces)

    # for cases if there is "space-term-space" between name and attribute
    for t in tags_spaces:
        l=t.split()
        #print(l)

        for i, y in enumerate(l):
            if '=' in y:
                if i == 1 and y.startswith('=') :
                    #print(i, t, 'Tag name goes into equals sign, becomes attribute name.')
                    return False

                # FIX THIS PART !!!!!!!!!!!!!!!!!!!!:
                # detects <to a b="111"> as error but doesn't okay <to b ="111">
                if i >= 2:
                    #print(i, t, 'One or more terms in between tag name and attribute name and therefore spaces.')
                    return False


    # some other checks for spaces
    for tag in tags_spaces:
        # check ? (depends on is_attribute_correctly_formed(tag) function)
        if not is_attribute_correctly_formed(tag):
            #print('Tag has spaces but it doesn\'t have an attribute')
            return False

    return True

print('No spaces in tag names: ', no_spaces_in_tag_names())


# ****************************************************************************************************
#   CHECK THAT THERE NO SPACE BETWEEN IN OPENING BRACKET AND NAME IN START TAGS
# ****************************************************************************************************
def no_initial_space_in_opening_tags():
    """
    Check there is no space between opening bracket and the name in opening tags
    :return: boolean
    """

    for tag in get_all_tags_in_order():
        if tag[1] == ' ':
            #print('Space immediatelly after \'<\' not allowed.', tag)
            return False


print('No initial space in opening tags: ', no_initial_space_in_opening_tags())

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
            #print('Closing tag must not have spaces.', tag)
            return False


print('No spaces in closing tags:', no_spaces_in_closing_tags())


# ****************************************************************************************************
#   CHECK FOR INVALID CHARACTERS AT THE BEGINNING OF TAG NAME
# ****************************************************************************************************
def no_invalid_initial_characters_in_opening_tag():
    """
    DOESN'T DO ANYTHING ABOUT &, ^, %, $, # etc. CHECK WHAT TO DO HERE? Specification allows them?

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
                print(tag)
                return False

    # Check that element names DO start with letter (uppercase or lowercase), underscore, or colon.
    for tag in get_all_tags_in_order():
        if tag[1] != '?' and tag[1] != '!':     #make sure that names starting with ? and ! pass through
            if tag[1].isalpha():
                return True
            elif tag[1] == '_':
                return True
            elif tag[1] == ':':
                return True
            else:
                print(tag)
                print('Some other character that needs to be evaluated.')


print('No invalid initial characters in opening tag: ', no_invalid_initial_characters_in_opening_tag())



# ****************************************************************************************************
#   CHECK THAT TAGS ARE CASE SENSITIVE
# ****************************************************************************************************
def no_case_sensitive_tags():
    """
    BUG !!!!!!!!!!!!!!!!  : line not_matching = [ i for i in unique_pairs if clean[i[0]] != clean[i[1]] ].
    WHEN SPACE IS INSERTED INTO TAG NAMES LIST ABOVE GOES OUT OF RANGE.
    This is probably because I'm splitting on spaces. ANd each time whitespace splits a tag
    there is more elements in the list?

    Check that tags are case sensitive.

    # get all tags and clean them up
    # change cleaned list of tags to lowercase
    # create a list of tag pairs (list of lists)
    # remove duplicate pairs
    # remove any single tags (eg remaining unpairable tags, such as those for XML declaration or DTD)
    # make final comparison if pairs match. Returns a list of their indexes.
    # get textual version of mismatched elements, if any. - for informative/ printing purposes.
    # return True of number of mismatches is zero, False otherwise
    """

    # get all tags and clean them up
    without_declarations_and_comments = get_all_tags_in_order()

    for item in get_all_tags_in_order():
        if '<!' in item or '<?' in item:
            without_declarations_and_comments.remove(item)

    no_slash = [ tag.replace('/', '') for tag in without_declarations_and_comments  ]
    split = [ tag.split() for tag in no_slash ]
    first_part = [ part[0] for part in split ]

    clean=[]
    for tag in first_part:
        tag=tag.strip('<')
        tag=tag.strip('>')
        clean.append(tag)

    # change 'clean' list of tags to lowercase
    lowercase = [tag.lower() for tag in clean]

    # create a list of pairs (list of lists)
    pairs2 = []
    for count, tag in enumerate(lowercase):
        pairs1 = []
        for count2, tag2 in enumerate(lowercase):
        # if name occurs more than once, get their indexes
            if tag2 == tag:
                pairs1.append(count2)
        pairs2.append(pairs1)

    # remove duplicate pairs
    pairs2_set = set(tuple(x) for x in pairs2)
    unique_pairs = [list(x) for x in pairs2_set]

    # make final comparison if pairs match. Returns a list of indexes.
    not_matching = [ i for i in unique_pairs if clean[i[0]] != clean[i[1]] ]

    # get textual version of mismatched elements, if any. - for informative/ printing purposes.
    not_matching_text = [ (clean[i[0]], clean[i[1]]) for i in not_matching ]

    # return True of numberof mismatches in zero, False otherwise
    if not_matching == 0:
        print('All tag pairs have the same letter case. No mismatches.')
        return True
    else:
        print('Upper/lower case mismatch in ' + str(len(not_matching)) + ' elements: ' + str(not_matching_text))
        return False


print('No case sensitive tags: ', no_case_sensitive_tags())



# ****************************************************************************************************
#   CHECK IF SEQUENCE OF OPENING ELEMENTS MATCHES THE SEQUENCE OF THE CLOSING ELEMENTS
# ****************************************************************************************************
"""
def check_names_in_opening_and_closing_tags_match():

    Compare name in opening tag to the name in corresponding closing tag

    ex:
    note, to, firstname, lastname, from, heading, body
    (order needs to match)
    note, to, firstname, lastname, from, heading, body
    :return:

    note
    to
    firstname
    firstname
    lastname
    lastname
    to
    from
    from
    heading
    heading
    body
    body
    note
    '''





def check_order_of_opening_tags_matches_order_of_closing_tags():
    '''
    Procedure example (breadth-first approach):
    Traverse through the all opening tags.
    Do the same for the closing tags.
    Orders need to match. -> all opening tags have correct closing tag
    ex:
    note, to, firstname, lastname, from, heading, body
    (equals)
    note, to, firstname, lastname, from, heading, body
    :return:
    '''


def check_nesting():
    '''
    Procedure example (depth-first approach):
    Traverse through the all opening tags.
    Do the same for the closing tags.
    Orders need to match. -> all opening tags have correct closing tag
    ex:
    note, to, firstname, lastname, from, heading, body
    (equals)
    note, to, firstname, lastname, from, heading, body
    :return:
    """













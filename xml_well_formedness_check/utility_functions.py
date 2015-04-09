"""
Utility class and its functions for xml parser.
They provide helpful functionality but don't perform direct parsing of the xml file.
"""

import logging
import sys


class Utility():
    """
    Class Utility encapsulates utility functions that help preparing xml file for parsing.
    """
    def __init__(self, path_to_file):
        self.xml_string = ''
        self.line_numbers = ()
        self.path_to_file=path_to_file

        """
            Read file twice.
            First to get a string of xml file.
            Second to get line numbers and line content.
            These are purposely placed into the initializer so file reading is done only once (for each) and
            then passed to appropriate functions in this module and checker1 module.
            With this we're avoiding to read from file each time a function that requests xml file-string is called
            (previously each function had a call to a function that reads from file -
            hence file was being read many times - bad practice).
        """

        """
            Get xml file as a string.
        """
        logging.basicConfig(level=logging.DEBUG)
        try:
            with open(self.path_to_file, 'r') as f:
                for i in f:
                    self.xml_string = self.xml_string + i

        except IOError as e:
            logging.error(e)
            logging.error(sys.exc_info())

        """
            Get line numbers for each line of XML file
            Counts empty lines too and that is fine (OttoTag does that too).
            Produces list of tuple pairs: line number, line
        """
        try:
            with open(self.path_to_file, 'r') as f:
                # get line numbers
                self.line_numbers = [(num, line) for num, line in enumerate(f, 1)]  # param 1 to start counting lines at 1

        except IOError as e:
            logging.error(e)
            logging.error(sys.exc_info())


    # ****************************************************************************************************
    #   CLASS METHODS
    # ****************************************************************************************************

    # ****************************************************************************************************
    #   GET ALL TAGS - utility function
    # ****************************************************************************************************
    def get_all_tags_in_order(self):
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
        opening_bracket_positions = [i for i, char in enumerate(self.xml_string) if char == '<']
        closing_bracket_positions = [i for i, char in enumerate(self.xml_string) if char == '>']

        # pair up tag positions into list of tuples
        zipped = zip(opening_bracket_positions, closing_bracket_positions)
        zipped = list(zipped)

        # get a list of all tags
        result = [ self.xml_string[i[0] : i[1]+1] for i in zipped ]
        return result


    # ****************************************************************************************************
    #   REMOVE DECLARATIONS, DOCTYPE AND COMMENTS - utility function
    # ****************************************************************************************************
    def remove_declaration_doctype_comments(self):
        """
        Removes xml declartion, doctype and comment tags for easier processing of remaining elements.
        :return: list of elements
        """
        # clean up tags from scratch and remove single elements (they don't affect nesting)
        without_declarations_and_comments = utility.get_all_tags_in_order()

        for item in utility.get_all_tags_in_order():
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
    def get_clean_tags(self):
        """

        [ IMPORTANT:  ASSUMES THAT ALL ANGLE BRACKETS ARE PRESENT!!! AND THAT THERE ARE NO EXTRA ANGLE BRACKETS!
        IF IN DOUBT THEN CHECK THAT ALL ANGLE BRACKETS ARE OKAY FIRST.
         FOR EXAMPLE IF THERE IS EXTRA SINGLE COMMENT TAG, THIS WILL FAIL

         - RUN is_number_of _angle_brackets_even() function first! User needs to fix that first, then run this function.]

        Get all tags
        Clean up so you get a list of element names in order as they appear in xml file top-down
        :return: list
        """
        # get all tags and clean them up
        without_declarations_and_comments = utility.get_all_tags_in_order()
        #print('get all atg in order: ', get_all_tags_in_order())
        for item in utility.get_all_tags_in_order():
            #  print('STSTSTST ', without_declarations_and_comments)
            if '<?' in item:
                without_declarations_and_comments.remove(item)
                # print(without_declarations_and_comments)
            if '<!' in item:
                without_declarations_and_comments.remove(item)
                #print(without_declarations_and_comments)


        # remove opening and closing forward slashes (but dont remove any slashes in the name itself!)
        no_slash = [ tag.replace('</', '<') for tag in without_declarations_and_comments ]
        no_slash = [tag.replace('/>', '>') for tag in no_slash]
        #print('no_slash: ', no_slash)

        split = [ tag.split() for tag in no_slash ]
        #print('split: ', split)

        # remove brackets
        tags = []
        for part in split:
            if not part[0] == '<':
                tags.append(part[0])
            elif part[0] == '<':
                tags.append(part[1])

        clean = []
        for tag in tags:
            tag = tag.strip('<')
            tag = tag.strip('>')
            clean.append(tag)

        return clean


    # ****************************************************************************************************
    #   GET THE ROOT ELEMENT - utility function
    # ****************************************************************************************************
    def get_root_element(self):
        """
        Get the root element:
        Iterate through all tags (provided by get_all_tags_in_order() function )
        Get the first tag that doesn't have ? or ! after opening bracket
        Get the very last tag
        :return: root element tuple
        """
        root_opening, root_closing='', ''

        # get the first tag that doesn't have ? or ! after opening bracket
        for i, tag in enumerate(utility.get_all_tags_in_order()):
            if not (tag.startswith('<?') or tag.startswith('<!')):  # inore XML declaration and DTD declar that start with '?' and '!'
                root_opening = tag
                break

        # get the very last tag
        for i, tag in enumerate(utility.get_all_tags_in_order()):
            if tag.endswith('>') and i+1 == len(utility.get_all_tags_in_order()):
                root_closing = tag
                break

        root_tags = (root_opening, root_closing)

        return root_tags


    # ****************************************************************************************************
    #   GET OPENING COMMENT TAG POSITIONS - utility function
    # ****************************************************************************************************
    def get_opening_comment_tag_positions(self):
        """
        Get comment tag positions (for opening and closing comment tags).
        - utility function
        :return: list of tuple pairs [(opening1, closing1), ...]
        """
        # get indexes of all opening tags for comments
        comm_opening = [ i for i in range(len(self.xml_string)) if self.xml_string.startswith('<!--', i) ]
        #print('OPENING: ', comm_opening)
        return comm_opening


    # ****************************************************************************************************
    #   GET CLOSING COMMENT TAG POSITIONS - utility function
    # ****************************************************************************************************
    def get_closing_comment_tag_positions(self):
        # get indexs of all closing tags for comments
        comm_closing = [j for j in range(len(self.xml_string)) if self.xml_string.startswith('-->', j)]
        #print('CLOSING: ', comm_closing)
        return comm_closing


    # ****************************************************************************************************
    #   GET SINGLE ELEMENTS - utility function
    # ****************************************************************************************************
    def get_single_elements(self):
        """
        Get single elements (eg <example/> <br       />, <acb />, <child attribute="value" />)
        :return: list of single elements in order of appearance in xml file (top down)
        """
        # get all tags and clean them up
        tags = self.remove_declaration_doctype_comments()

        # dump singles in a list
        list_of_singles = [ tag for tag in tags if tag.endswith('/>') ]

        # what about singles that don't end with />, like errors such as <br >
        # what about when I have two or more of same (or diff) singles that don't end with /> like <br >, <br >
        return list_of_singles


    # ****************************************************************************************************
    #   GET DATA CONTENT
    # ****************************************************************************************************
    def get_data_content(self):
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
        opening_bracket_positions = [i for i, char in enumerate(self.xml_string[1:]) if char == '<'
                                        and not char.startswith('<?') and not char.startswith('<!') ]
        closing_bracket_positions = [i for i, char in enumerate(self.xml_string) if char == '>'
                                        and not char.startswith('<?') and not char.startswith('<!')]

        # pair up closing and opening tag positions into list of tuples
        zipped = zip(closing_bracket_positions, opening_bracket_positions)
        zipped = list(zipped)

        # get content in between closing and opening tag (excluding brackets signs)
        content = [self.xml_string[ i[0]+1 : i[1]+1 ] for i in zipped]
        return content


    # ****************************************************************************************************
    #   GET NUMBER OF ALL TAGS EXCLUDING DECLARATIONS, DOCTYPE AND COMMENTS - utility function
    # ****************************************************************************************************
    def get_number_of_all_tags_excluding_declar_doctype_comments(self):
        # get all tags and clean them up
        without_declarations_and_comments = utility.get_all_tags_in_order()

        for item in utility.get_all_tags_in_order():
            if '<!' in item:
                without_declarations_and_comments.remove(item)
                #print(without_declarations_and_comments)
            if '<?' in item:
                without_declarations_and_comments.remove(item)
                #print(without_declarations_and_comments)

        return len(without_declarations_and_comments)

# instantiate Utility class object
utility = Utility('/home/matjaz/PycharmProjects/xml_well_formedness_check/'
                  'xml_well_formedness_check/xml_2.txt')


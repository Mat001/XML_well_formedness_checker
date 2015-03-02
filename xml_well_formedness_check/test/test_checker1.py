'''
Test cases to test checker1 module.
'''


from xml_well_formedness_check.checker1 import *


def test_get_string():
    assert getstring() != None


def test_root_element_opening():
    pass


def test_starts_with_xml_declaration():
    assert starts_with_xml_declaration() == True


def test_root_element_closing():
    pass

def test_root_element_exists_and_matches():
    pass

def test_number_of_angle_brackets_is_even():
    pass

def test_get_all_tags_in_order():
    pass

def test_paired_elements_are_closed_properly_and_names_match():
    pass


def element_names_lowercase():
    pass




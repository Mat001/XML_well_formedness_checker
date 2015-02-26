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

def test_each_element_has_strictly_two_identical_names_for_each_tag():
    #assert each_element_has_strictly_two_identical_names_for_each_tag()
    pass






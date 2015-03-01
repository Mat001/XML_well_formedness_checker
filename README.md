# XML_well_formedness_checker
Python app that checks if XML file is well formed (syntax, nesting).
Written in Python 3.4. Requires min Python 3.
Used IDE PyCharm 4.

The app reads an XML file, parses it and confirms that the file is well formed.
Warning message informs user if any errors.

The app has three main files:
- checker1.py
- utility_functions.py
- sample xml file

The rest are docs and tests (tests currently empty).

To use the app:
Put checker1.py, utility_functions.py and your test file into the same directory.
1. in funtion get_string() in utility_functions.py specify the path to the xml file.
2. on unix systems in terminal go to top directory xml_well_formedness_check.
3. run the program by: python3 xml_well_formedness_check/checker1.py.

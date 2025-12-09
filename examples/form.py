"""
Glossary login query form.

This module assembles a form definition (as plain Python data)
that other parts of the app (and Swagger) can consume.
"""

import examples.form_filler as ff

from examples.form_filler import FLD_NM  # for tests

USERNAME = 'username'
PASSWORD = 'password'

# High-level explanation of what this list represents.
#    This is the full field definition for the login form, in the structure
#    expected by form_filler and by Swagger documentation.
LOGIN_FORM_FLDS = [
    {
        FLD_NM: 'Instructions',
        ff.QSTN: 'Enter your username and password.',
        ff.INSTRUCTIONS: True, # Marks this entry as an instructional (non-input) field.
    },
    {
        FLD_NM: USERNAME,
        ff.QSTN: 'User name:', # Prompt shown to the user.
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,       # This field is required.
    },
    {
        FLD_NM: PASSWORD,
        ff.QSTN: 'Password:',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
]


def get_form() -> list:
    return LOGIN_FORM_FLDS


def get_form_descr() -> dict:
    """
    For Swagger!
    """
    return ff.get_form_descr(LOGIN_FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(LOGIN_FORM_FLDS)


def main():
    # print(f'Form: {get_form()=}\n\n')
    print(f'Form: {get_form_descr()=}\n\n')
    # print(f'Field names: {get_fld_names()=}\n\n')


if __name__ == "__main__":
    main()

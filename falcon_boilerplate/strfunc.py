import re


def untrailing_slash_it(string):
    return string.rstrip('/')


def trailing_slash_it(string):
    return untrailing_slash_it(string) + '/'


def unleading_slash_it(string):
    return string.lstrip('/')


def leading_slash_it(string):
    return '/' + unleading_slash_it(string)


def unduplicate_slash_it(string):
    return string.replace('//', '/')


def proper_slash_it(string):
    return unduplicate_slash_it(leading_slash_it(untrailing_slash_it(string)))


def camel_case_it(string):
    return "".join(x.capitalize() for x in string.lower().split("_"))


def lower_camel_case_it(string):
    camel_string = camel_case_it(string)
    return string[0].lower() + camel_string[1:]


def camel_case_to_snake_case(string):
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    string = re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()
    return string

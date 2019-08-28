import re


def snake_to_camel_case(column_name):
    return re.sub('_([a-z])',
                  lambda match: match.group(1).upper(),
                  column_name)

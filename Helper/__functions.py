import datetime

import discord
import discord as dc

BOT_DEVELOPERS = [
    184768535107469314,  # Dark#7316
    179686717534502913,  # Neonic#1410
    183331874670641152  # Purplegaze#0007
]


def split_escape(s, delimiter):
    '''
    Function to split strings but with a string-escape feature using quotation marks. Uses a tab
    character as a reserved character.
    '''

    if delimiter == '"':
        return s.split('"')

    parsed = ""
    escaped = ""
    backslashed = False

    for c in s:
        add_to_parsed = True

        if c == '"' and not backslashed:
            escaped = not escaped
            add_to_parsed = False

        if c == '\\' and not backslashed:
            backslashed = True
            continue

        if backslashed:
            backslashed = False

        if not add_to_parsed:
            continue

        if c == delimiter and not escaped:
            parsed += "\t"
        else:
            parsed += c

    return [s.strip() for s in parsed.split("\t")]


def f_caps(s):
    '''
    Shorthand to express any string in lowercase with the first character capitalized.
    '''

    return s[0].upper() + s[1:].lower()


def smart_lookup(needle, haystack, case_ins=True, startstr=True, substr=True, aliases=[]):
    '''
    Lookup function that can optionally handle case sensitivity, ambiguity between substrings at
    the start or middle of a haystack entry, and aliases for haystack entries. Returns an
    [index, value] pair or False if nothing is found.
    '''

    lookup_needle = needle.lower() if case_ins else needle
    lookup_haystack = [hay.lower() for hay in haystack] if case_ins else needle
    lookup_aliases = [
        [alias.lower() for alias in alias_list] for alias_list in aliases
    ] if case_ins else aliases

    matching_haystack = [hay for hay in lookup_haystack if hay == lookup_needle]
    matching_aliases = [
        [alias for alias in a_list if alias == lookup_needle]
        for a_list in lookup_aliases
    ]
    matching_aliases_trim = [a_list for a_list in matching_aliases if len(a_list) > 0]

    if len(matching_haystack) == 1:
        ind = lookup_haystack.index(matching_haystack[0])
        return [ind, haystack[ind]]

    if len(matching_aliases_trim) == 1:
        ind = matching_aliases.index(matching_aliases_trim[0])
        return [ind, haystack[ind]]

    if startstr:
        matching_haystack = [hay for hay in lookup_haystack if hay.startswith(lookup_needle)]
        matching_aliases = [
            [alias for alias in a_list if alias.startswith(lookup_needle)]
            for a_list in lookup_aliases
        ]
        matching_aliases_trim = [a_list for a_list in matching_aliases if len(a_list) > 0]

        if len(matching_haystack) == 1:
            ind = lookup_haystack.index(matching_haystack[0])
            return [ind, haystack[ind]]

        if len(matching_aliases_trim) == 1:
            ind = matching_aliases.index(matching_aliases_trim[0])
            return [ind, haystack[ind]]

    if substr:
        matching_haystack = [hay for hay in lookup_haystack if lookup_needle in hay]
        matching_aliases = [
            [alias for alias in a_list if lookup_needle in alias]
            for a_list in lookup_aliases
        ]
        matching_aliases_trim = [a_list for a_list in matching_aliases if len(a_list) > 0]

        if len(matching_haystack) == 1:
            ind = lookup_haystack.index(matching_haystack[0])
            return [ind, haystack[ind]]

        if len(matching_aliases_trim) == 1:
            ind = matching_aliases.index(matching_aliases_trim[0])
            return [ind, haystack[ind]]

    return False


def grammar_list(listed, conj="and"):
    '''
    Returns a single string listing several elements with correct grammar and custom conjunction.
    '''

    if len(listed) == 0: return "none"
    if len(listed) == 1: return listed[0]

    comma_section = ", ".join(listed[:-1])
    final_element = listed[-1]

    final_str = f" {conj} ".join([comma_section, final_element])

    return final_str


def is_dm(ctx):
    '''
    Shortened form of the function to check whether or not a command was sent in DMs.
    '''

    return isinstance(ctx.channel, dc.DMChannel)


def is_slash_cmd(ctx):
    '''
    Bridge function for determining whether a command usage is slash or prefixed.
    '''

    return type(ctx).__name__.endswith('ApplicationContext')


def command_user(ctx):
    '''
    Bridge function for determining a command's author for both slash and prefixed commands, as
    well as component interactions.
    '''

    if not is_slash_cmd(ctx):
        return ctx.message.author
    else:
        return ctx.user


async def command_response_timestamp(ctx, response):
    '''
    Function to get a timestamp of the response message sent by the bot for both slash and prefixed
    commands.
    '''

    if not is_slash_cmd(ctx):
        return response.created_at.timestamp()
    else:
        response_msg = await response.original_response()
        return response_msg.created_at.timestamp()


def m_line(s):
    '''
    Function to parse multi-line strings in a more convenient way for code readability and
    to avoid long lines.
    '''

    return s.replace("\t", "").replace("\n\n", "/n//n/").replace("\n", "").replace(
        "/n/", "\n").replace("/t/", "\t")


def plural(i, si='', pl='s'):
    '''
    Shorthand to correctly pluralize the word for some quantity i.
    '''

    return si if float(i) == 1 else pl


def is_dev(ctx):
    '''
    CMD module check for commands that need developer perms.
    '''

    return command_user(ctx).id in BOT_DEVELOPERS


def is_whole(s):
    '''
    Shorthand to check if a string or float is equivalent to an integer.
    '''

    try:
        s_c = float(s)
    except ValueError:
        return False

    return s_c.is_integer()


def is_number(s):
    '''
    Shorthand to check if a string can be parsed as a number.
    '''

    try:
        s_c = float(s)
        return True
    except ValueError:
        return False


def get_dollar_strings(s):
    """
    Turns a string with $s (like $this$) into an array with all the strings contained in dollar signs.
    Example usage:
    print(get_dollar_strings("$hello$ world"))  # Output: ["hello"]
    print(get_dollar_strings("$one$ $two$ $three$ four five"))  # Output: ["one", "two", "three"]
    """
    string_list = []
    current_string = ""
    in_dollar = False

    for i in range(len(s)):
        if s[i] == "$":
            if in_dollar:
                in_dollar = False
                string_list.append(current_string)
                current_string = ""
            else:
                in_dollar = True
        elif in_dollar:
            current_string += s[i]

    if in_dollar:
        string_list.append(current_string)

    return string_list


def replace_dollar_strings(s, replacement_list):
    """
    Turns a string with $s (like $this$) and replaces them using a list in sequential order.

    Example usage:
    print(replace_dollar_strings("$one$ $two$ $three$ four five", ["1", "2", "3"]))  # Output: "1 2 3 four five"

    If there are too few elements in the replacement list compared to the number of "$" substrings in the input string, the remaining substrings will be left as-is in the output string.

    For example, if the input string is "$one$ $two$ $three$" and the replacement list is ["1"], the resulting output string will be "1 $two$ $three$".

    If there are too many elements in the replacement list compared to the number of "$" substrings in the input string, the extra elements will be ignored and not used in the output string.

    For example, if the input string is "$one$ $two$" and the replacement list is ["1", "2", "3"], the resulting output string will be "1 2".
    :param s: The string to replace.
    :param replacement_list: The array to replace the elements with.
    :return: The string with elements replaced.
    """
    string_list = get_dollar_strings(s)
    new_string = ""
    for i in range(len(string_list)):
        if i < len(replacement_list):
            new_string += replacement_list[i]
        new_string += s[s.find(string_list[i]) + len(string_list[i]):s.find(string_list[i + 1])] if i < len(
            string_list) - 1 else s[s.find(string_list[i]) + len(string_list[i]):]
    return new_string

def create_timestamped_embed(title, description):
    """
    Creates an embed with a description and title with a timestamp.
    """
    return discord.Embed(
        title = title,
        description = description,
        color = discord.Color.green(),
        timestamp = datetime.now()
    )
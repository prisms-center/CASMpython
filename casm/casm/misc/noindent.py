import json
import six
import uuid

# ---------------------------------------------------
# Some code to keep parts of a json string from being spread across multiple lines
# code from: http://stackoverflow.com/questions/13249415/can-i-implement-custom-indentation-for-pretty-printing-in-python-s-json-module
# answer: http://stackoverflow.com/a/25935321
# code by: http://stackoverflow.com/users/247623/erik-allik


class NoIndent(object):
    def __init__(self, value):
        self.value = value


class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key, )
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in six.iteritems(self._replacement_map):
            result = result.replace('"@@%s@@"' % (k, ), v)
        return result

def singleline_arrays_json_printable(input):
    """Makes a copy of a list or dict ready nicer JSON printing

    Usage:
        from casm.misc import noindent
        with open(filename, 'w') as f:
            data = singleline_arrays_json_printable(input)
            f.write(json.dumps(data, cls=noindent.NoIndentEncoder, indent=2, sort_keys=True))

    Arguments
    ---------
      input: dict or list
        Input data, as from JSON

      property_type: str
        One of "atom", "mol", or "global"

    Returns
    -------
        data:
            A copy of input that prints without indenting innermost arrays.
    """

    def _recurs_list(data):
        subobjects = False
        for i in range(len(data)):
            if isinstance(data[i], dict):
                subobjects = True
                _recurs_dict(data[i])
            elif isinstance(data[i], list):
                subobjects = True
                if not _recurs_list(data[i]):
                    data[i] = NoIndent(data[i])
        return subobjects

    def _recurs_dict(data):
        for key in data:
            if isinstance(data[key], dict):
                _recurs_dict(data[key])
            if isinstance(data[key], list):
                if not _recurs_list(data[key]):
                    data[key] = NoIndent(data[key])

    import copy
    data = copy.deepcopy(input)
    if isinstance(input, dict):
        _recurs_dict(data)
    elif isinstance(input, list):
        _recurs_list(data)
    return data

# ---------------------------------------------------

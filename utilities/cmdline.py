"""Command line utilities"""

import sys
import json

def _autocast(x):
    """Automatically cast a string to python object"""
    for dtype in ("basic","dict","list","str"):
        match dtype:
            case "basic":
                try:
                    return json.loads(x)
                except Exception as err:
                    pass
            case "dict":
                try:
                    if ":" in x:
                        items = x.split(",")
                        return {y:_autocast(z) for y,z in [v.split(":",1) for v in items]}
                except Exception as err:
                    pass
            case "list":
                try:
                    if "," in x:
                        return [_autocast(y) for y in x.split(",")]
                except Exception as err:
                    pass
            case "str":
                return str(x)
    raise ValueError(f"unable to autocast {x=}")

def _getargs(argv):
    """Get args, kwargs, flags, and values from argument list

    Extracts the various parts of the command line as follows.

    - `args` have no leading dash or equal sign embedded.

    - `kwargs` have a leading double dash. If an equal sign is embedded the
      item of kwargs is set to the value that follows the equal sign.
      Otherwise, the item is set to `True`.

    - `flags` have a single dash. The list entry is the value following the
      dash.

    - `values` have an equal sign embedded with no leading dash. The key is
      the portion before the equal sign and value is everything after the
      equal sign.

    Values are automatically converted to python values as follows.

    1. Basic values, i.e., `None`, `bool, `int`, `float` as interpreted by the
    JSON loader. Values in double-quotes are interpreted as `str`.

    2. Dictionaries, i.e., `key:value` comma-separated strings.

    3. Lists, i.e., comma-separated values.

    4. String, everything else is simply interpreted as a string.
    """

    # convert position arguments (not starting with a dash)
    args = tuple(_autocast(x) for x in argv if x[0] != "-" and "=" not in x)
    
    # convert keyword arguments (starting with double dash)
    kwargs = {}
    for value in (y[2:] for y in argv if y.startswith("--")):
        if "=" in value:
            key,value = value.split("=",1)
            kwargs[key] = _autocast(value)
        else:
            kwargs[value] = True
    
    # convert flags (starting with single dash)
    flags = tuple(_autocast(x[1:]) for x in argv if x[0]=="-" and x[1] != "-")
    
    # values (no leading dash but has equal sign)
    values = {}
    for key,value in (x.split("=",1) for x in argv if "=" in x and not x.startswith("-")):
        values[key] = _autocast(value)

    return args,kwargs,flags,values

class CommandLine:
    """Command line parser"""
    def __init__(self,argv=sys.argv):
        """Construct command line parser and parse arguments"""
        self.argv = argv
        self.command = argv[0]
        self.args,self.kwargs,self.flags,self.values = _getargs(argv[1:])

    def __repr__(self):
        return f"cmdline.CommandLine(argv={repr(self.argv)})"

if __name__ == '__main__':
    
    test = CommandLine(["test","abc","456","78.9","null","true","false",
        "--key1=value1","--key2=123","--key3=45.6","--key4=null","--key5=true","--key5=false",
        "-a","-bcd=123","-123","-123.45","-null","-true","-false",
        "value1=123","value2=45.6","value3=abc","value4=null","value5=true","value6=false","value7=",
        "value8=123,45.6,def,null,true,false",
        "value9=int:123,float:45.6,string:ghi,none:null,true:true,false:false",
        ])

    n_errors = 0
    def check_eq(a,b,msg=None):
        if msg is None:
            msg = f"check_eq({a=},{b=}) failed"
        if not a == b:
            print("ERROR:",msg.format(a=a,b=b))
            global n_errors
            n_errors +=1

    check_eq(repr(test),"cmdline.CommandLine(argv=['test', 'abc', '456', '78.9', 'null', 'true', 'false', '--key1=value1', '--key2=123', '--key3=45.6', '--key4=null', '--key5=true', '--key5=false', '-a', '-bcd=123', '-123', '-123.45', '-null', '-true', '-false', 'value1=123', 'value2=45.6', 'value3=abc', 'value4=null', 'value5=true', 'value6=false', 'value7=', 'value8=123,45.6,def,null,true,false', 'value9=int:123,float:45.6,string:ghi,none:null,true:true,false:false'])", f"{repr(test)=} is incorrect")
    check_eq(test.argv,['test', 'abc', '456', '78.9', 'null', 'true', 'false', '--key1=value1', '--key2=123', '--key3=45.6', '--key4=null', '--key5=true', '--key5=false', '-a', '-bcd=123', '-123', '-123.45', '-null', '-true', '-false', 'value1=123', 'value2=45.6', 'value3=abc', 'value4=null', 'value5=true', 'value6=false', 'value7=', 'value8=123,45.6,def,null,true,false', 'value9=int:123,float:45.6,string:ghi,none:null,true:true,false:false'], f"{test.argv=} is incorrect")
    check_eq(test.command,'test', f"{test.command=} is incorrect")
    check_eq(test.args,('abc', 456, 78.9, None, True, False), f"{test.args=} is incorrect")
    check_eq(test.kwargs,{'key1': 'value1', 'key2': 123, 'key3': 45.6, 'key4': None, 'key5': False}, f"{test.kwargs=} is incorrect")
    check_eq(test.flags,('a', 'bcd=123', 123, 123.45, None, True, False), f"{test.flags=} is incorrect")
    check_eq(test.values,{'value1': 123, 'value2': 45.6, 'value3': 'abc', 'value4': None, 'value5': True, 'value6': False, 'value7': '', 'value8': [123, 45.6, 'def', None, True, False], 'value9': {'int': 123, 'float': 45.6, 'string': 'ghi', 'none': None, 'true': True, 'false': False}}, f"{test.values=} is incorrect")

    print(f"CommandLine() tests: {n_errors} errors")

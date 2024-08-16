# Enum the pre-Python 3.4 way.
def enum(**enums):
    return type("ProcStatus", (), enums)
ProcStatus = enum(OK = 0, ERROR = 1)

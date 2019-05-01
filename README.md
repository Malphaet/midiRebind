# gmaPy
Get/send midi commands to a GrandMA but can be configured to bind any custom SysEx message
To do so add a custom patch (or use a currently defined one, but chances are patches made for one SysEx won't work on another) and add a parser in the mapping directory

# Depends
* Mostly mido (pip install mido) for the midi binding and blessings for the testing (pip install belssings)
* test.py depends on the submodule minitest witch also depends on blessings but is not necessary

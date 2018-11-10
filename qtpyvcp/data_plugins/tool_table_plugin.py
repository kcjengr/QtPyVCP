import os
import json

from qtpy.QtCore import QFileSystemWatcher

from qtpyvcp.data_plugins import QtPyVCPDataPlugin, QtPyVCPDataChannel

DEFAULT_TOOL =  {
        "T": -1,
        "P": -1,
        "Z": 0.0,
        "comment": ""
    }

DEFAULT_TOOL.update({d:0.0 for d in 'XYZABCUVWDIJQ'})

# example interface
# tooltable:current_tool?       # will return the current tool number
# tooltable:current_tool?diameter    # will return the current tool diameter

# toollife:current_tool?hours

# stat:tool_in_spindle?
# stat:spindle[0].override?     # will return current override of spindle 0
# cmd:spindle[0].override=100   # set spindle override
# hal:halui.machine.is-on?      # get the value of a HAL pin

class ToolTable(QtPyVCPDataPlugin):

    protocol = 'tooltable'

    current_tool = QtPyVCPDataChannel()

    TOOL_TABLE = {}

    def __init__(self):
        super(ToolTable, self).__init__()

        file = '/home/kurt/dev/cnc/QtPyVCP/sim/tool.tbl'

        self.tool_table_file = file

        if self.TOOL_TABLE == {}:
            self.loadToolTable(file)

    def loadToolTable(self, file=None):

        if file is None:
            file = self.tool_table_file

        if not os.path.exists(file):
            return

        with open(file, 'r') as fh:
            lines = fh.readlines()

        table = {}

        for line in lines:

            line = line.strip()
            data, sep, comment = line.partition(';')

            tool = DEFAULT_TOOL.copy()
            for item in data.split():
                descriptor = item[0]
                if descriptor in 'TPXYZABCUVWDIJQ':
                    value = item.lstrip(descriptor)
                    if descriptor in ('T', 'P'):
                        try:
                            tool[descriptor] = int(value)
                        except:
                            print 'Error converting value to int'
                            break
                    else:
                        try:
                            tool[descriptor] = float(value)
                        except:
                            print 'Error converting value to float'
                            break

            tool['comment'] = comment.strip()

            tnum = tool['T']
            if tnum == -1:
                continue

            # add the tool to the table
            table[tnum] = tool

        self.__class__.TOOL_TABLE = table

        print json.dumps(table, sort_keys=True, indent=4)



def main():

    tool_table_file = '/home/kurt/dev/cnc/QtPyVCP/sim/tool.tbl'

    import sys
    from qtpy.QtCore import QCoreApplication


    tool_table = ToolTable(tool_table_file)

    def file_changed(path):
        print('File Changed: %s' % path)
        tool_table.loadToolTable(tool_table_file)

    app = QCoreApplication(sys.argv)

    fs_watcher = QFileSystemWatcher([tool_table_file,])
    fs_watcher.fileChanged.connect(file_changed)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

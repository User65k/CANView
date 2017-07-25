import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class LastMessagesWindow(Gtk.Window):

    def __init__(self, start_button_clicked, selection_button_clicked, open_history_wnd):
        Gtk.Window.__init__(self, title="CAN Viewer")
        self.set_border_width(10)

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        #Creating the ListStore model
        self.software_liststore = Gtk.ListStore(int, str, str, str, int, float, float)
        self.id_refs = {}
        #self.lock = allocate_lock()

        self.current_filter_bits = 1
        self.current_filter_mask = 0

        #Creating the filter, feeding it with the liststore model
        self.canid_filter = self.software_liststore.filter_new()
        #setting the filter function, note that we're not using the
        self.canid_filter.set_visible_func(self.canid_filter_func)

        #creating the treeview, making it use the filter as a model, and adding the columns
        self.treeview = Gtk.TreeView.new_with_model(self.canid_filter)
        for i, column_title in enumerate(["ID", "Hex", "Str","Count","Period"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i+1)
            self.treeview.append_column(column)
            #first row is sortable
            if i==1:
                column.set_sort_column_id(0)

        #make tree clickable
        #select = self.treeview.get_selection()
        #select.connect("changed", self.on_tree_selection_changed)
        self.treeview.connect("row-activated", self.row_activated)

        #creating buttons
        self.buttons = list()
        #-connect
        button = Gtk.Button("Start")
        self.buttons.append(button)
        button.connect("clicked", start_button_clicked)
        #-filter
        button = Gtk.Button("Filter IDs")
        self.buttons.append(button)
        button.connect("clicked", selection_button_clicked)
        #-history
        button = Gtk.Button("Message Log")
        self.buttons.append(button)
        button.connect("clicked", self.on_log_button_clicked)
        self.open_history = open_history_wnd

        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.grid.attach(self.scrollable_treelist, 0, 0, 8, 10)
        self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.buttons[1:]):
            self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.scrollable_treelist.add(self.treeview)

        self.show_all()

    def add_frame(self, frame):

        #display format
        if frame.id_type:
            # Extended arbitrationID
            c_id = "{0:08x}".format(frame.arbitration_id)
        else:
            c_id = "{0:03x}".format(frame.arbitration_id)

        c_ascii = "".join(chr(c) if (c >=0x20 and c<=0x7E) else '.' for c in frame.data)
        #c_ascii = re.sub(r'[^\x20-\x7E]','.', frame['Data'])
        c_hex = " ".join("{:02x}".format(c) for c in frame.data)
        #remember canIDs
        
        #self.lock.acquire()
        if frame.arbitration_id in self.id_refs:
            old = self.software_liststore[self.id_refs[frame.arbitration_id]]
            #print old[:]
            cnt = old[4]+1
            frequ = frame.timestamp - old[6]
            new_set = (frame.arbitration_id, c_id, c_hex, c_ascii, cnt, frequ, frame.timestamp)
            self.software_liststore[self.id_refs[frame.arbitration_id]] = new_set
        else:
            new_set = (frame.arbitration_id, c_id, c_hex, c_ascii, 1, 0, frame.timestamp)
            self.id_refs[frame.arbitration_id]= self.software_liststore.append( new_set )
        #self.lock.release()

    def canid_filter_func(self, model, iter, data):
        #check id & mask = bits & mask
        return model[iter][0]&self.current_filter_mask == self.current_filter_bits&self.current_filter_mask

    def on_log_button_clicked(self, widget):
        self.open_history(None)
    def row_activated(self, widget, row, col):
        #CAN ID in list selected
        model = widget.get_model()
        self.open_history(model[row][0])
        return True
#    def on_tree_selection_changed(self, selection):
#        model, treeiter = selection.get_selected()
#        if treeiter != None:
#            print("You selected", model[treeiter][0])

if __name__ == "__main__":
    import time, random
    from can.message import Message
    from thread import start_new_thread, allocate_lock

    def set_display_filter(widget):
        #we set the current language filter to the button's label
        win.current_filter_bits = 0x123
        win.current_filter_mask = 0xfff
        print("%02x&%02x selected!" % (win.current_filter_bits, win.current_filter_mask))
        #we update the filter, which updates in turn the view
        win.canid_filter.refilter()

    def on_start_button_clicked(widget):
        widget.set_label("Stop")

    def open_history(can_id):
        if can_id is not None:
            print(hex(can_id)+" History")
        else:
            print("Message History")

    def can_sim(win):
        while Gtk.main_level()!=0:
            win.add_frame(Message(timestamp=time.time(), extended_id=False, arbitration_id=0x123, dlc=4, data=[0x45, 0xc3, 0x77, 0x53]))
            time.sleep(0.2)
            win.add_frame(Message(timestamp=time.time(), extended_id=False, arbitration_id=0x123, dlc=4, data=[0x98, 0xa3, 0x24, 0xd3]))
            time.sleep(0.2)

    win = LastMessagesWindow(on_start_button_clicked, set_display_filter, open_history)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()

    win.add_frame(Message(timestamp=time.time(), extended_id=False, arbitration_id=0x12f, dlc=3, data=[0x31,0x39,0x40]))
    win.add_frame(Message(timestamp=time.time(), extended_id=False, arbitration_id=0x6fb, dlc=4, data=[0x20,0x05,0x41,0x89]))
    win.add_frame(Message(timestamp=time.time(), extended_id=False, arbitration_id=0x90, dlc=5, data=[0x10,0xde,0xad,0xbe,0xef]))

    start_new_thread(can_sim,(win,))

    Gtk.main()
<template><v-app>
    <!-- Navigation drawer to move from home to solution and back -->
    <v-navigation-drawer
        app
        dark
        temporary
        v-model="navOpen"
    >
        <v-list>
            <v-list-item
                v-for="item in navItems"
                :key="item.title"
                @click="changePage(item.title)"
                :disabled="item.disabled"
            >
                <v-list-item-icon>
                    <v-icon>{{ item.icon }}</v-icon>
                </v-list-item-icon>
  
                <v-list-item-content>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
    <!-- App bar and error bar -->
    <div><v-app-bar color="blue">
        <v-app-bar-nav-icon @click="navOpen = !navOpen"></v-app-bar-nav-icon>

        <v-toolbar-title>Event Scheduler</v-toolbar-title>
    </v-app-bar></div>
    <v-alert type="error" v-model="error" dismissible>{{ errorText }}</v-alert>
    <!-- Home page -->
    <span v-if="currentPage == 'Home'"><v-container>
        <v-row>
            <!-- Data table to show imported rooms -->
            <v-col><v-card flat>
                <v-card-title>Rooms</v-card-title>
                <v-data-table
                    :headers="roomHeaders"
                    :items="roomsData"
                    :items-per-page="-1"
                    hide-default-footer
                    :loading="loading"
                >
                    <!-- Slot in room item to edit or delete -->
                    <template v-slot:[`item.actions`]="{ item }">
                        <v-icon
                            small
                            class="mr-2"
                            @click="editItem(item, 'room')"
                        >mdi-pencil</v-icon>
                        <v-icon
                            small
                            @click="deleteItem(item, 'room')"
                        >mdi-delete</v-icon>
                    </template>
                </v-data-table>
            </v-card></v-col>
            <v-divider vertical></v-divider>
            <!-- Data table to show imported events -->
            <v-col><v-card flat>
                <v-card-title>Events</v-card-title>
                <v-data-table
                    :headers="eventsHeaders"
                    :items="eventsData"
                    :items-per-page="-1"
                    hide-default-footer
                    :loading="loading"
                >
                    <!-- Slot in event item to edit or delete -->
                    <template v-slot:[`item.actions`]="{ item }">
                        <v-icon
                            small
                            class="mr-2"
                            @click="editItem(item, 'event')"
                        >mdi-pencil</v-icon>
                        <v-icon
                            small
                            @click="deleteItem(item, 'event')"
                        >mdi-delete</v-icon>
                    </template>
                </v-data-table>
            </v-card></v-col>
        </v-row>
    </v-container>
    <!-- Dialog box that opens when deleting an item -->
    <v-dialog v-model="deleteOpen" max-width="500px">
        <v-card>
            <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeDelete">Cancel</v-btn>
                <v-btn color="blue darken-1" text @click="deleteItemConfirm">OK</v-btn>
                <v-spacer></v-spacer>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <!-- Dialog box that opens when editing an item -->
    <v-dialog v-model="editOpen" width="600px">
        <v-card>
            <v-card-title><span class="text-h5">Edit {{ whichDialog.charAt(0).toUpperCase() + whichDialog.slice(1) }}</span></v-card-title>
            <v-card-text>
                <v-container v-if="whichDialog == 'room'"><v-row class="mt-5">
                    <v-col>
                        <v-text-field v-model="editRoom.name" label="Room name" :rules="rules.names"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editRoom.capacity" label="Capacity" type="number" :rules="rules.people"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editRoom.opens" label="Opens (24h)" type="number" :rules="rules.times"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editRoom.closes" label="Closes (24h)" type="number" :rules="rules.times"></v-text-field>
                    </v-col>
                </v-row></v-container>
                <v-container v-else><v-row class="mt-5">
                    <v-col>
                        <v-text-field v-model="editEvent.name" label="Event name" :rules="rules.names"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editEvent.attendance" label="Attendance" type="number" :rules="rules.people"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editEvent.starts" label="Starts (24h)" type="number" :rules="rules.times"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-text-field v-model="editEvent.ends" label="Ends (24h)" type="number" :rules="rules.times"></v-text-field>
                    </v-col>
                </v-row></v-container>
            </v-card-text>
  
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="close" class="mb-2">Cancel</v-btn>
                <v-btn color="blue darken-1" text @click="save" :disabled="!validateEdit" class="mb-2">Save</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    <!-- Buttons to open the input navigation drawer or start the schedule algorithm -->
    <v-container><v-row>
        <v-col><v-btn
            outlined
            rounded
            :color="!roomsData.length || !eventsData.length ? 'green' : ''"
            @click="inputOpen = !inputOpen"
        >
            <v-icon class="pr-2">mdi-table-large-plus</v-icon>Input
        </v-btn></v-col>
        <v-col><v-btn
            outlined
            rounded
            :disabled="!(roomsData.length && eventsData.length)"
            color="light-blue"
            @click="callAlgorithm"
            class="float-right"
        >
            <v-icon class="pr-2">mdi-calendar-arrow-right</v-icon>Schedule
        </v-btn></v-col>
    </v-row></v-container>
    </span>
    <!-- Navigation drawer that contains room and event importing -->
    <v-navigation-drawer
        app
        right
        temporary
        v-model="inputOpen"
        width="500"
    >
        <v-btn icon class="mr-5 my-1" style="float: right" @click="inputOpen = false"><v-icon>mdi-close</v-icon></v-btn>
        <v-expansion-panels accordion flat multiple v-model="openPanels">
            <!-- Expansion panel where you can upload room or event files -->
            <v-expansion-panel>
                <v-divider></v-divider>
                <v-expansion-panel-header :disable-icon-rotate="panelIcon(0) == 'mdi-check'">Upload Files
                    <template v-slot:actions><v-icon :color="panelIcon(0) == 'mdi-check' ? 'green' : ''">{{panelIcon(0)}}</v-icon></template>
                </v-expansion-panel-header>
                <v-divider></v-divider>
                <v-expansion-panel-content>
                    <v-container>
                        <v-card flat>
                            <v-card-title>Upload room and event files here</v-card-title>
                            <v-card-text>Supported filetypes are: JSON, csv, tsv, xmls, and txt</v-card-text>
                            <v-file-input label="Upload Rooms" :accept="fileTypes" v-model="roomsFile"></v-file-input>
                            <v-spacer></v-spacer>
                            <v-file-input label="Upload Events" :accept="fileTypes" v-model="eventsFile"></v-file-input>
                        </v-card>
                    </v-container>
                </v-expansion-panel-content>
            </v-expansion-panel>
            <!-- Expansion panel where you can manually input rooms -->
            <v-expansion-panel readonly>
                <v-divider></v-divider>
                <v-expansion-panel-header>Input Rooms Manually</v-expansion-panel-header>
                <v-divider></v-divider>
            </v-expansion-panel>
            <!-- Expansion panel where you can manually input events -->
            <v-expansion-panel readonly>
                <v-divider></v-divider>
                <v-expansion-panel-header>Input Events Manually</v-expansion-panel-header>
                <v-divider></v-divider>
            </v-expansion-panel>
        </v-expansion-panels>
        <!-- Imports inputted rooms and events into the page -->
        <v-btn
            outlined
            rounded
            @click="inputData"
            :color="roomsFile || eventsFile || roomsManual.length || eventsManual.length ? 'blue' : 'black'"
            :disabled="!validateInput"
            class="mt-3 ml-2"
        >
            <v-icon class="pr-2">mdi-application-import</v-icon>Import
        </v-btn>
    </v-navigation-drawer>
    <!-- Solution page -->
    <span v-if="currentPage == 'Solution'"><v-container fluid><v-row class="fill-width">
        <!-- Shows rooms in a calendar format -->
        <v-col v-for="(room, i) in solution" :key="i">
            <v-card flat min-width="300">
                <v-card-title>{{ room.name }}</v-card-title>
                <v-calendar
                    color="primary"
                    type="day"
                    hide-header
                    start="2021-01-01"
                    :events="getEvents(room.events)"
                    :event-color="getEventColor"
                    :first-time="decimalToTime(room.opens-1)"
                    :interval-count="room.closes-Math.max(room.opens-2, 0)"
                >
                </v-calendar>
            </v-card>
        </v-col>
    </v-row></v-container>
    </span>
</v-app>
</template>

<script>
import axios from 'axios'

export default {

    // Runs when the html of the page has been loaded and mounted to the browser
    mounted() {
        // Changes title of tab to "Event Scheduler"
        document.title = "Event Scheduler"
    },

    // Holds all the values of the Vue page, all the data you want the page to remember
    data: () => ({
        error: false,               // Whether to display the error bar
        errorText: "",              // The text to display in the error
        navOpen: false,             // Whether the page navigation drawer is open
        inputOpen: false,           // Whether the input navigation drawer is open
        loading: false,             // Wether the page is loading a solution
        currentPage: "Home",        // The current page being displayed. Either "Home" or "Solution"
        roomHeaders: [              // The headers for the rooms data table
            {text: "Name", value: "name", sortable: true, align: "start"},
            {text: "Capacity", value: "capacity", sortable: true},
            {text: "Opens (24h)", value: "opens", sortable: true},
            {text: "Closes (24h)", value: "closes", sortable: true},
            {text: "Actions", value: "actions", sortable: false},
        ],
        eventsHeaders: [            // The headers for the events data table
            {text: "Name", value: "name", sortable: true, align: "start"},
            {text: "Attendance", value: "attendance", sortable: true},
            {text: "Starts (24h)", value: "starts", sortable: true},
            {text: "Ends (24h)", value: "ends", sortable: true},
            {text: "Actions", value: "actions", sortable: false},
        ],
        openPanels: [0],            // Which expansion panels are open currently in the input nav drawer
        whichDialog: "",            // Which table has an open edit/delete dialog. Either "room" or "event"
        deleteIndex: -1,            // The index of the item being deleted
        deleteOpen: false,          // Whether the delete dialog is open
        editIndex: -1,              // The index of the item being edited
        editOpen: false,            // Whether the edit dialog is open
        editRoom: {                 // The values of the room being edited
            name: '',
            capacity: -1,
            opens: 0,
            closes: 24,
        },
        editEvent: {                // The values of the event being edited
            name: '',
            attendance: -1,
            starts: 0,
            ends: 24,
        },
        rules: {                    // Different validation rules for the editing dialog
            names: [v => v.length > 0 || "Name Required"],
            people: [
                v => parseFloat(v) > 0 || "Must be greater than 0",
                v => parseInt(v) === parseFloat(v) || "Must be a whole number"
            ],
            times: [v => (parseFloat(v) >= 0 && parseFloat(v) <= 24) || "Time must be between 0 and 24"]
        },
        roomsData: [                // Holds the room items (currently has toy data in)
            {name: "Room1",  capacity: 30, opens: 8, closes: 17}, {name: "Room2",  capacity: 30, opens: 8, closes: 17}, {name: "Room3",  capacity: 30, opens: 8, closes: 17}, {name: "Room4",  capacity: 30, opens: 8, closes: 17}, {name: "Room5",  capacity: 30, opens: 8, closes: 17}, {name: "Room7",  capacity: 30, opens: 8, closes: 17}, {name: "Room8",  capacity: 30, opens: 8, closes: 17}],
        eventsData: [               // Holds the event items (currently has toy data in)
            {name: "meeting1", attendance: 23, starts: 10, ends: 10.5}, {name: "meeting2", attendance: 23, starts: 10, ends: 11.5}],
        fileTypes: ".json,.csv,.tsv,.txt,.xmls",    // Supported file types
        colors: [                   // Different colors the events can be, chosen randomly
            "red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green", "light-green", "lime", "amber", "orange", "deep-orange", "brown", "blue-grey"
        ],
        roomsFile: null,            // The room file being uploaded
        eventsFile: null,           // The event file being uploaded
        roomsManual: [],            // Will hold room items being added manually
        eventsManual: [],           // Will gold event items being added manually
        solution: null,             // Holds a list of room items with lists of event items inside
    }),

    // Functions that can be called using the vue data, not cached, don't need to return
    methods: {
        changePage(pageTitle) {
            /*
            * This function changes the current page from the page navigation drawer
            * 
            * Arguments-
            * pageTitle (string):   the name of the page to be changed to. Either "Home" or "Solution"
            */
            this.currentPage = pageTitle
            this.navOpen = false
        },
        panelIcon(panel) {
            /*
            * Calculates which icon to display next to each expansion panel. If there is data that will be imported
            * and the panel is closed, will display a check mark, otherwise the correct arrow icon
            * 
            * Arguments-
            * panel (int):      the index of the panel being calculated
            * 
            * Returns -
            * (string):         the string associated with the mdi-icon to be displayed
            */
            switch(panel) {
                case 0:
                    return this.openPanels.includes(0) ? 'mdi-chevron-up' : ((this.roomsFile || this.eventsFile) ? 'mdi-check' : 'mdi-chevron-up')
                default:
                    return 'mdi-chevron-down'
            }
        },
        editItem(item, which) {
            /*
            * Prepares an item to be edited and opens the edit dialog. Specifies which type of items and assigns
            * the appropriate values to the data objects
            * 
            * Arguments-
            * item (object):        the object associated with the item that was clicked on
            * which (string):       whether the item is a room or event. Ether "room" or "event"
            */
            this.whichDialog = which
            if (which == "room") {
                this.editRoom.name = item.name
                this.editRoom.capacity = item.capacity
                this.editRoom.opens = item.opens
                this.editRoom.closes = item.closes
                this.editIndex = this.roomsData.indexOf(item)
            } else {
                this.editEvent.name = item.name
                this.editEvent.attendance = item.attendance
                this.editEvent.starts = item.starts
                this.editEvent.ends = item.ends
                this.editIndex = this.eventsData.indexOf(item)
            }
            this.editOpen = true
        },
        close() {
            // Closes the edit dialog
            this.editOpen = false
            this.editIndex = -1
        },
        save() {
            /*
            * Completes an edit, assigns the new values to the correct item and closes the dialog
            */
            var edited
            if (this.whichDialog == "room") {
                edited = this.roomsData[this.editIndex]
                edited.name = this.editRoom.name
                edited.capacity = this.editRoom.capacity
                edited.opens = this.editRoom.opens
                edited.closes = this.editRoom.closes
            } else {
                edited = this.eventsData[this.editIndex]
                edited.name = this.editEvent.name
                edited.attendance = this.editEvent.attendance
                edited.starts = this.editEvent.starts
                edited.ends = this.editEvent.ends
            }
            this.editOpen = false
            this.editIndex = -1
        },
        deleteItem(item, which) {
            /*
            * Prepares an item to be deleted and opens the delete dialog. Specifies which type of item is to be deleted
            *
            * Arguments-
            * item (object):        the object associated with the item that was clicked on
            * which (string):       whether the item is a room or event. Ether "room" or "event"
            */
            this.whichDialog = which
            if (which == "room") {
                this.deleteIndex = this.roomsData.indexOf(item)
            } else {
                this.deleteIndex = this.eventsData.indexOf(item)
            }
            this.deleteOpen = true
            this.deleteIndex = -1
        },
        deleteItemConfirm() {
            // Completes a delete, removing the corresponding item from its list
            if (this.whichDialog == "room") {
                this.roomsData.splice(this.deleteIndex)
            } else {
                this.eventsData.splice(this.deleteIndex)
            }
            this.deleteOpen = false
            this.deleteIndex = -1
        },
        closeDelete() {
            // Closes the delete dialog
            this.deleteOpen = false
            this.deleteIndex = -1
        },
        callAlgorithm() {
            //Calls the backend to schedule events into rooms and changes the page to the solution page
            this.loading = true
            axios({
                // Call the backend /schedule url
                method: "post",
                url: "http://localhost:8000/schedule",
                data: {rooms: this.roomsData, events: this.eventsData}
            }).then( r=> {
                // Check if an error occured, otherwise set the solution
                if ("error" in r.data) {
                    this.error = true
                    this.errorText = r.data.error
                    return
                }
                this.solution = r.data.solution
                this.changePage("Solution")
                console.log(this.solution)
            }).catch(error => {
                // Check if an error occured in the http request
                this.error = true
                this.errorText = error
            }).finally(() => {
                // Finished loading
                this.loading = false
            })
        },
        inputData() {
            // Inputs data into the data table. Loads data from files if necessary and from manual input if necessary
            if (this.roomsFile || this.eventsFile) {
                // Create a formdata to hold the files
                var formData = new FormData()
                if (this.roomsFile) {
                    formData.append("rooms", this.roomsFile)
                }
                if (this.eventsFile) {
                    formData.append("events", this.eventsFile)
                }
                axios({
                    // Call the backend /upload url
                    method: "post",
                    url: "http://localhost:8000/upload",
                    data: formData
                }).then( r=> {
                    // Check if an error occurred, otherwise add data to the corresponding list
                    if ("error" in r.data) {
                        this.error = true
                        this.errorText = r.data.error
                        return
                    }
                    if (this.roomsData.length) {
                        this.roomsData = this.roomsData.concat(r.data.rooms)
                    } else {
                        this.roomsData = r.data.rooms
                    }
                    if (this.eventsData.length) {
                        this.eventsData = this.eventsData.concat(r.data.events)
                    } else {
                        this.eventsData = r.data.events
                    }
                    this.roomsFile = null
                    this.eventsFile = null
                }).catch(error => {
                    // Check if an error occured in the http request
                    this.error = true
                    this.errorText = error
                })
            }
            this.inputOpen = false
        },
        decimalToTime(decimal) {
            /*
            * Converts decimal 24h time into a hh:mm string format to be consumed by the v-calendar component
            *
            * Arguments-
            * decimal (float):      decimal 24h time to be converted
            * 
            * Returns-
            * (string):         string representing the hh:mm formatted version of the input decimal
            */
            var hour = Math.floor(decimal)
            var remainder = decimal - hour
            var minute = Math.round(remainder*(60)).toString()

            if (minute.length < 2) {
                minute = "0" + minute
            }

            return hour.toString() + ":" + minute
        },
        getEvents(eventList) {
            /*
            * Converts a list of event objects into one that can be consumed by the v-calendar component
            *
            * Arguments-
            * eventList (array):        array of event objects returned by the algorithm
            * 
            * Returns-
            * (array):      array of event objects that are visualized in the room calendar
            */
            var out = []
            for (var i=0; i<eventList.length; i++) {
                // Choose a random color to assign to the event
                if (!("color" in eventList[i])) {
                    eventList[i].color = this.colors[Math.floor(Math.random() * this.colors.length)]
                }
                // Convert times and add an arbitrary date
                out.push({
                    name: eventList[i].name,
                    start: "2021-01-01 " + this.decimalToTime(eventList[i].starts),
                    end: "2021-01-01 " + this.decimalToTime(eventList[i].ends),
                    color: eventList[i].color
                })
            }
            return out
        },
        getEventColor(event) {
            // Helper function for v-calendar
            return event.color
        },
    },

    // Functions that calculate specific data values that sometimes change, are cached, need to return something
    computed: {
        validateInput() {
            /*
            * Validates the input in the input nav drawer, determines whether the button is disabled or not
            *
            * Returns-
            * (bool):       whether the data input into the input nav drawer is valid
            */
            return this.roomsFile || this.eventsFile
        },
        validateEdit() {
            /*
            * Valiates the input to the edit dialog
            *
            * Returns-
            * (bool):       whether the new values of the edited object are valid or not
            */
            var edited
            if (this.whichDialog == "room") {
                edited = this.editRoom
                var opens = parseFloat(edited.opens)
                var closes = parseFloat(edited.closes)
                return edited.name.length && (parseInt(edited.capacity) === parseFloat(edited.capacity)) && parseFloat(edited.capacity) > 0 && 0 <= opens && 24 >= opens && 0 <= closes && 24 >= closes && opens < closes
            } else {
                edited = this.editEvent
                var starts = parseFloat(edited.starts)
                var ends = parseFloat(edited.ends)
                return edited.name.length && (parseInt(edited.attendance) === parseFloat(edited.attendance)) && parseFloat(edited.attendance) > 0 && 0 <= starts && 24 >= starts && 0 <= ends && 24 >= ends && starts < ends
            }
        },
        navItems() {
            /*
            * Determines the different options in the page nav drawer. Required because sometimes Solution is disabled
            *
            * Returns-
            * (list):       list of objects corresponding to the different pages
            */
            return [
                {title: "Home", icon: "mdi-home", disabled: false},
                {title: "Solution", icon: "mdi-calendar-check", disabled: this.solution === null},
            ]
        },
    }
};
</script>

<style scoped>
/* Lets the rooms in the solution overflow horizontally */
.fill-width {
  overflow-x: auto;
  flex-wrap: nowrap;
}
</style>
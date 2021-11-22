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
                    item-key="tableId"
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
                    item-key="tableId"
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
                            <v-card-text>Supported filetypes are: JSON, csv, tsv, xlsx, and txt</v-card-text>
                            <v-file-input label="Upload Rooms" :accept="fileTypes" v-model="roomsFile"></v-file-input>
                            <v-spacer></v-spacer>
                            <v-file-input label="Upload Events" :accept="fileTypes" v-model="eventsFile"></v-file-input>
                        </v-card>
                    </v-container>
                </v-expansion-panel-content>
            </v-expansion-panel>
            <!-- Expansion panel where you can manually input rooms -->
            <v-expansion-panel>
                <v-divider></v-divider>
                <v-expansion-panel-header :disable-icon-rotate="panelIcon(1) == 'mdi-check'">Input Rooms Manually
                    <template v-slot:actions><v-icon :color="panelIcon(1) == 'mdi-check' ? 'green' : ''">{{panelIcon(1)}}</v-icon></template>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <v-container>
                        <v-card flat>
                            <v-card-title>Room Input Form</v-card-title>
                            <v-container>
                                <v-row><v-col>
                                    <v-text-field v-model="newRoom.name" label="Room name" :rules="rules.names"></v-text-field>
                                </v-col>
                                <v-col>
                                    <v-text-field v-model="newRoom.capacity" label="Capacity" type="number" :rules="rules.people"></v-text-field>
                                </v-col></v-row>
                                <v-row><v-col>
                                    <v-text-field v-model="newRoom.opens" label="Opens (24h)" type="number" :rules="rules.times"></v-text-field>
                                </v-col>
                                <v-col>
                                    <v-text-field v-model="newRoom.closes" label="Closes (24h)" type="number" :rules="rules.times"></v-text-field>
                                </v-col></v-row>
                                <v-row><v-col>
                                    <v-text-field v-model="newRoom.amount" label="How many to add" type="number" :rules="rules.people"></v-text-field>
                                </v-col></v-row>
                            </v-container>
                        </v-card>
                    </v-container>
                </v-expansion-panel-content>
                <v-divider></v-divider>
            </v-expansion-panel>
            <!-- Expansion panel where you can manually input events -->
            <v-expansion-panel>
                <v-divider></v-divider>
                <v-expansion-panel-header :disable-icon-rotate="panelIcon(2) == 'mdi-check'">Input Events Manually
                    <template v-slot:actions><v-icon :color="panelIcon(2) == 'mdi-check' ? 'green' : ''">{{panelIcon(2)}}</v-icon></template>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                    <v-container>
                        <v-card flat>
                            <v-card-title>Event Input Form</v-card-title>
                            <v-container>
                                <v-row><v-col>
                                    <v-text-field v-model="newEvent.name" label="Event name" :rules="rules.names"></v-text-field>
                                </v-col>
                                <v-col>
                                    <v-text-field v-model="newEvent.attendance" label="Attendance" type="number" :rules="rules.people"></v-text-field>
                                </v-col></v-row>
                                <v-row><v-col>
                                    <v-text-field v-model="newEvent.starts" label="Starts (24h)" type="number" :rules="rules.times"></v-text-field>
                                </v-col>
                                <v-col>
                                    <v-text-field v-model="newEvent.ends" label="Ends (24h)" type="number" :rules="rules.times"></v-text-field>
                                </v-col></v-row>
                                <v-row><v-col>
                                    <v-text-field v-model="newEvent.amount" label="How many to add" type="number" :rules="rules.people"></v-text-field>
                                </v-col></v-row>
                            </v-container>
                        </v-card>
                    </v-container>
                </v-expansion-panel-content>
                <v-divider></v-divider>
            </v-expansion-panel>
        </v-expansion-panels>
        <!-- Imports inputted rooms and events into the page -->
        <v-btn
            outlined
            rounded
            @click="inputData"
            :color="validateInput ? 'blue' : 'black'"
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
                <v-card-title>{{ room.name + " - (Capacity: " + room.capacity + ")" }}</v-card-title>
                <v-calendar
                    color="primary"
                    type="day"
                    hide-header
                    start="2021-01-01"
                    :events="getEvents(room.events)"
                    :event-color="getEventColor"
                    :first-time="decimalToTime(room.opens-1)"
                    :interval-count="room.closes-Math.max(room.opens-2, 0)"
                    :ref="'calendar'+i"
                >
                    <template v-slot:[`day-body`]="{ }">
                        <div
                            class="v-line"
                            :style="{ top: getFirstY(i) }"
                        ></div>
                        <div
                            class="v-line"
                            :style="{ top: getLastY(i) }"
                        ></div>
                    </template>
                </v-calendar>
            </v-card>
        </v-col>
    </v-row></v-container>
    <v-container>
        <v-card flat>
            <!-- Table with list of unassigned events and suggestions on how to fix -->
            <v-card-title>Suggestions
                <v-btn
                    outlined
                    rounded
                    @click="resetParameters()"
                    class="ml-2"
                    v-if="rejectedOnce"
                >
                    <v-icon class="pr-2">mdi-refresh</v-icon>Reset Suggestions
                </v-btn>
            </v-card-title>
            <v-data-table
                :headers="suggestionHeaders"
                :items="suggestions"
                :items-per-page="-1"
                group-by="suggestion_id"
                hide-default-footer
                :loading="loading"
                no-data-text="No unassigned events"
            >
            <template v-slot:[`group.header`]="{items, isOpen, toggle}">
                <th colspan="4" style="fontSize: 15px; padding-top: 10px;">
                    <v-icon @click="toggle"
                        >{{ isOpen ? 'mdi-minus' : 'mdi-plus' }}
                    </v-icon>
                    {{ items[0].suggestion_string }}
                    <v-btn
                        outlined
                        rounded
                        color="red"
                        @click="rejectSuggestion(items[0].suggestion_id)"
                        class="ml-2"
                        style="float: right; margin-top: -6px"
                        :disabled="items[0].suggestion_string == 'No suggestion available'"
                    >
                        <v-icon class="pr-2">mdi-delete-forever</v-icon>Reject
                    </v-btn>
                    <v-btn
                        outlined
                        rounded
                        @click="completeSuggestion(items[0].suggestion_id)"
                        class="ml-2"
                        style="float: right; margin-top: -6px"
                        :disabled="items[0].suggestion_string == 'No suggestion available'"
                    >
                        <v-icon class="pr-2">mdi-application-cog-outline</v-icon>Complete
                    </v-btn>
                </th>
            </template>
            </v-data-table>
        </v-card>
    </v-container>
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
        suggestionHeaders: [        // The headers for the unassigned events suggestions
            {text: "", value: "suggestion_id", sortable: true, align: "start"},
            {text: "Name", value: "unassigned.name", sortable: false},
            {text: "Attendance", value: "unassigned.attendance", sortable: false},
            {text: "Starts (24h)", value: "unassigned.starts", sortable: false},
            {text: "Ends (24h)", value: "unassigned.ends", sortable: false},
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
        newRoom: {                  // The values of a room being manually input
            name: '',
            capacity: -1,
            opens: 0,
            closes: 24,
            amount: 1,
        },
        editEvent: {                // The values of the event being edited
            name: '',
            attendance: -1,
            starts: 0,
            ends: 24,
        },
        newEvent: {                 // The values of an event being manually input
            name: '',
            attendance: -1,
            starts: 0,
            ends: 24,
            amount: 1,
        },
        rules: {                    // Different validation rules for the editing dialog
            names: [v => v.length > 0 || "Name Required"],
            people: [
                v => parseFloat(v) > 0 || "Must be greater than 0",
                v => parseInt(v) === parseFloat(v) || "Must be a whole number"
            ],
            times: [v => (parseFloat(v) >= 0 && parseFloat(v) <= 24) || "Time must be between 0 and 24"]
        },
        roomsData: [],              // Holds the room items (currently has toy data in)
        eventsData: [],             // Holds the event items (currently has toy data in)
        fileTypes: ".json,.csv,.tsv,.txt,.xlsx",    // Supported file types
        colors: [                   // Different colors the events can be, chosen randomly
            "red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green", "light-green", "lime", "amber", "orange", "deep-orange", "brown", "blue-grey"
        ],
        roomsFile: null,            // The room file being uploaded
        eventsFile: null,           // The event file being uploaded
        roomsManual: [],            // Will hold room items being added manually
        eventsManual: [],           // Will hold event items being added manually
        solution: null,             // Holds a list of room items with lists of event items inside
        suggestions: [],            // Holds list of suggestions made by algorithm II
        unassignedEvents: [],       // Holds list of unassigned event objects
        suggestionParameters: [     // List of parameters that algorithm II should iterate over [capacity_tolerance, self_tolerance, event_tolerance, event_length_tolerance, boost]
            [0, 0, 0, 0, -1],
            [5, 0.5, 0, 0, 400],
            [10, 1, 0.5, 0, 300],
            [20, 2, 1, 0, 200],
            [30, 5, 3, 0.25, 100],
            [40, 10, 10, 0.5, 0],
        ],
        rejectedOnce: false,        // Whether a suggestion has been rejected
        defaultParameters: [        // Default parameters for reset
            [0, 0, 0, 0, -1],
            [5, 0.5, 0, 0, 400],
            [10, 1, 0.5, 0, 300],
            [20, 2, 1, 0, 200],
            [30, 5, 3, 0.25, 100],
            [40, 10, 10, 0.5, 0],
        ]
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
                    return this.openPanels.includes(0) ? 'mdi-chevron-down' : ((this.roomsFile || this.eventsFile) ? 'mdi-check' : 'mdi-chevron-down')
                case 1:
                    return this.openPanels.includes(1) ? 'mdi-chevron-down' : ((this.validateRoom) ? 'mdi-check' : 'mdi-chevron-down')
                case 2:
                    return this.openPanels.includes(2) ? 'mdi-chevron-down' : ((this.validateEvent) ? 'mdi-check' : 'mdi-chevron-down')
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
            this.solution = null
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
        },
        deleteItemConfirm() {
            // Completes a delete, removing the corresponding item from its list
            if (this.whichDialog == "room") {
                this.roomsData.splice(this.deleteIndex, 1)
            } else {
                this.eventsData.splice(this.deleteIndex, 1)
            }
            this.deleteOpen = false
            this.deleteIndex = -1
            this.solution = null
        },
        closeDelete() {
            // Closes the delete dialog
            this.deleteOpen = false
            this.deleteIndex = -1
        },
        callAlgorithm() {
            // Calls the backend to schedule events into rooms and changes the page to the solution page
            this.loading = true
            this.resetParameters()
            this.solution = []
            this.unassignedEvents = []
            axios({
                // Call the backend /schedule url
                method: "post",
                url: "http://" + this.host + ":8000/schedule",
                data: {rooms: this.roomsData, events: this.eventsData}
            }).then( r=> {
                // Check if an error occured, otherwise set the solution
                if ("error" in r.data) {
                    this.error = true
                    this.errorText = r.data.error
                    return
                }
                this.solution = r.data.solution
                this.unassignedEvents = r.data.unassigned
                this.getSuggestions()
                this.changePage("Solution")
            }).catch(error => {
                // Check if an error occured in the http request
                this.error = true
                this.errorText = error
            }).finally(() => {
                // Finished loading
                this.loading = false
            })
        },
        getSuggestions() {
            // Calls the backend to get suggestions from algorithm II
            this.suggestions = []
            if (this.unassignedEvents.length == 0) {
                return
            }
            this.loading = true
            axios({
                // Call the backend /suggest url
                method: "post",
                url: "http://" + this.host + ":8000/suggest",
                data: {rooms: this.solution, unassigned: this.unassignedEvents, parameters: this.suggestionParameters}
            }).then( r=> {
                // Check if an error occured, otherwise set the solution
                if ("error" in r.data) {
                    this.error = true
                    this.errorText = r.data.error
                    return
                }
                this.suggestions = r.data.suggestions
            }).catch(error => {
                // Check if an error occured in the http request
                this.error = true
                this.errorText = error
            }).finally(() => {
                // Finished loading
                this.loading = false
            })
        },
        completeSuggestion(suggestion_id) {
            /*
            * Completes the suggestion automatically
            * 
            * Arguments-
            * suggestion_id (int):      index of the suggestion that was clicked on
            */
            var suggestion = this.suggestions[suggestion_id]
            // Update any events that are changed in events data
            for (var index in suggestion.changed_events) {
                this.eventsData[index] = suggestion.changed_events[index]
            }
            // Update any changed events in the room's event list
            var newList = []
            for (var i=0; i<suggestion.room.events.length; i++) {
                var newEvent = suggestion.room.events[i]
                newList.push(this.eventsData[newEvent.id])
            }
            suggestion.room.events = newList
            // Change the room in the solution and data to the changed room
            this.solution[suggestion.room.id] = suggestion.room
            this.roomsData[suggestion.room.id] = suggestion.room
            // Remove unassigned events that got assigned by this suggestion
            var nowAssignedIDs = []
            if ("multiple" in suggestion) {
                for (i=0; i<suggestion.multiple.length; i++) {
                    nowAssignedIDs.push(suggestion.multiple[i].id)
                }
            } else {
                nowAssignedIDs.push(suggestion.unassigned.id)
            }
            this.unassignedEvents = this.unassignedEvents.filter(event => !nowAssignedIDs.includes(event.id))
            // Update solution calendars with splice()
            this.solution.splice()
            // Get new suggestions with new set of unassigned events
            this.getSuggestions()
        },
        rejectSuggestion(suggestion_id) {
            /*
            * Rejects the suggestion and prevents suggestions from being less strict than the one suggested
            * 
            * Arguments-
            * suggestion_id (int):      index of the suggestion that was clicked on
            */
            this.rejectedOnce = true
            var suggestion = this.suggestions[suggestion_id]
            // Get rejected parameter and rejected value
            var parameter = suggestion.parameter[0]
            var parameterValue = suggestion.parameter[1]
            var minVal = 0
            for (var i=0; i<this.suggestionParameters.length; i++) {
                // Get the previous parameter value that is less than rejected value
                if (this.suggestionParameters[i][parameter] < parameterValue && this.suggestionParameters[i][parameter] > minVal) {
                    minVal = this.suggestionParameters[i][parameter]
                } else {
                    // Set the all parameter values to ones that are less than rejected value
                    this.suggestionParameters[i][parameter] = minVal
                }
            }
            // Get suggestions with new parameters
            this.getSuggestions()
        },
        resetParameters() {
            // Resets the suggestion parameters if rejections changed them
            if (!this.rejectedOnce) {
                return
            }
            this.rejectedOnce = false
            var i, j
            for (i=0; i<this.suggestionParameters.length; i++) {
                for (j=0; j<this.suggestionParameters[i].length; j++) {
                    this.suggestionParameters[i][j] = this.defaultParameters[i][j]
                }
            }
            this.getSuggestions()
        },
        inputData() {
            // Inputs data into the data table. Loads data from files if necessary and from manual input if necessary
            if (this.validateRoom) {
                // Adds a new room from the manual input panel
                var canExtendNumber = false
                var stem = this.newRoom.name
                var i, newName, number, diff
                if (this.newRoom.amount > 1) {
                    // Check for a number on the end of the name
                    for (i=0; i<this.newRoom.name.length; i++) {
                        if (!isNaN(parseInt(this.newRoom.name.slice(i)))) {
                            canExtendNumber = true
                            stem = this.newRoom.name.slice(0, i)
                            number = parseInt(this.newRoom.name.slice(i))
                            diff = this.newRoom.name.slice(i).length - String(number).length
                            if (diff > 0) {
                                stem = stem + " ".repeat(diff)
                            }
                            break
                        }
                    }
                }
                // For each copy of new room
                for (i=0; i<this.newRoom.amount; i++) {
                    // Extend room name stem
                    if (canExtendNumber) {
                        newName = stem + String(number + i)
                    } else {
                        newName = stem + (i > 0 ? (" (" + String(i+1) + ")") : "")
                    }
                    var newRoom = {
                        name: newName,
                        capacity: parseInt(this.newRoom.capacity),
                        opens: parseFloat(this.newRoom.opens),
                        closes: parseFloat(this.newRoom.closes)
                    }
                    this.roomsData.push(newRoom)
                }
                this.newRoom.name = ''
                this.newRoom.capacity = -1
                this.newRoom.opens = 0
                this.newRoom.closes = 24
                this.newRoom.amount = 1
            }
            if (this.validateEvent) {
                // Adds a new event from the manual input panel
                canExtendNumber = false
                stem = this.newEvent.name
                if (this.newEvent.amount > 1) {
                    // Check for a number on the end of the name
                    for (i=0; i<this.newEvent.name.length; i++) {
                        if (!isNaN(parseInt(this.newEvent.name.slice(i)))) {
                            canExtendNumber = true
                            stem = this.newEvent.name.slice(0, i)
                            number = parseInt(this.newEvent.name.slice(i))
                            diff = this.newEvent.name.slice(i).length - String(number).length
                            if (diff > 0) {
                                stem = stem + " ".repeat(diff)
                            }
                            break
                        }
                    }
                }
                // For each copy of new event
                for (i=0; i<this.newEvent.amount; i++) {
                    // Extend event name stem
                    if (canExtendNumber) {
                        newName = stem + String(number + i)
                    } else {
                        newName = stem + (i > 0 ? (" (" + String(i+1) + ")") : "")
                    }
                    var newEvent = {
                        name: newName,
                        attendance: parseInt(this.newEvent.attendance),
                        starts: parseFloat(this.newEvent.starts),
                        ends: parseFloat(this.newEvent.ends)
                    }
                    this.eventsData.push(newEvent)
                }
                this.newEvent.name = ''
                this.newEvent.attendance = -1
                this.newEvent.starts = 0
                this.newEvent.ends = 24
                this.newEvent.amount = 1
            }
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
                    url: "http://" + this.host + ":8000/upload",
                    data: formData
                }).then( r=> {
                    // Check if an error occurred, otherwise add data to the corresponding list
                    if ("error" in r.data) {
                        this.error = true
                        this.errorText = r.data.error
                        this.inputOpen = false
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
                    this.inputOpen = false
                }).catch(error => {
                    // Check if an error occured in the http request
                    this.error = true
                    this.errorText = error
                    this.inputOpen = false
                })
            }
            for (i=0; i<this.roomsData.length; i++) {
                this.roomsData.tableId = "room"+i
            }
            for (i=0; i<this.eventsData.length; i++) {
                this.eventsData.tableId = "event"+i
            }
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
        getFirstY(index) {
            /*
            * Returns the height to place a line that shows the time a room opens
            * 
            * Arguments-
            * index (int):      the index of the room's calendar
            *
            * Returns-
            * (string):     string representing the number of pixels above where the line should be
            */
            if (!this.$refs['calendar'+index] || !this.$refs['calendar'+index][0]) {
                return "-100px"
            }
            var calendar = this.$refs['calendar'+index][0]
            var room = this.solution[index]
            return calendar.timeToY(this.decimalToTime(room.opens))-1 + "px"
        },
        getLastY(index) {
            /*
            * Returns the height to place a line that shows the time a room closes
            * 
            * Arguments-
            * index (int):      the index of the room's calendar
            *
            * Returns-
            * (string):     string representing the number of pixels above where the line should be
            */
            if (!this.$refs['calendar'+index] || !this.$refs['calendar'+index][0]) {
                return "-100px"
            }
            var calendar = this.$refs['calendar'+index][0]
            var room = this.solution[index]
            return calendar.timeToY(this.decimalToTime(room.closes))-1 + "px"
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

            return this.roomsFile || this.eventsFile || this.validateRoom || this.validateEvent
        },
        validateRoom(){
            /*
            * Validates the input to the manual Room input
            *
            * Returns-
            * (bool):       whether the manual Room input is valid or not
            */
            var manualRoom = this.newRoom
            var opens = parseFloat(manualRoom.opens)
            var closes = parseFloat(manualRoom.closes)
            return manualRoom.name.length && parseInt(manualRoom.amount) > 0 && (parseInt(manualRoom.amount) == parseFloat(manualRoom.amount)) && (parseInt(manualRoom.capacity) === parseFloat(manualRoom.capacity)) && parseFloat(manualRoom.capacity) > 0 && 0 <= opens && 24 >= opens && 0 <= closes && 24 >= closes && opens < closes
        },
        validateEvent(){
            /*
            * Validates the input to the manual Event input
            *
            * Returns-
            * (bool):       whether the manual Event input is valid or not
            */
            var manualEvent = this.newEvent
            var starts = parseFloat(manualEvent.starts)
            var ends = parseFloat(manualEvent.ends)
            return manualEvent.name.length && parseInt(manualEvent.amount) > 0 && (parseInt(manualEvent.amount) == parseFloat(manualEvent.amount)) && (parseInt(manualEvent.attendance) === parseFloat(manualEvent.attendance)) && parseFloat(manualEvent.attendance) > 0 && 0 <= starts && 24 >= starts && 0 <= ends && 24 >= ends && starts < ends
        },
        validateEdit() {
            /*
            * Validates the input to the edit dialog
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
        host() {
            return window.location.host.substring(0, window.location.host.length-5)
        }
    }
};
</script>

<style scoped>
/* Lets the rooms in the solution overflow horizontally */
.fill-width {
  overflow-x: auto;
  flex-wrap: nowrap;
}

/* Line drawn on rooms to show when they start and end */
.v-line {
    height: 2px;
    background-color: #ea4335;
    position: absolute;
    left: -1px;
    right: 0;
    pointer-events: none;
}

</style>
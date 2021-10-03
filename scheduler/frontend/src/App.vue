<template><v-app>
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
    <div><v-app-bar color="blue">
        <v-app-bar-nav-icon @click="navOpen = !navOpen"></v-app-bar-nav-icon>

        <v-toolbar-title>Event Scheduler</v-toolbar-title>
    </v-app-bar></div>
    <v-alert type="error" v-model="error" dismissible>{{ errorText }}</v-alert>
    <span v-if="currentPage == 'Home'"><v-container>
        <v-row>
            <v-col><v-card flat>
                <v-card-title>Rooms</v-card-title>
                <v-data-table
                    :headers="roomHeaders"
                    :items="roomsData"
                    :items-per-page="-1"
                    hide-default-footer
                >
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
            <v-col><v-card flat>
                <v-card-title>Events</v-card-title>
                <v-data-table
                    :headers="eventsHeaders"
                    :items="eventsData"
                    :items-per-page="-1"
                    hide-default-footer
                >
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
    <v-navigation-drawer
        app
        right
        temporary
        v-model="inputOpen"
        width="500"
    >
        <v-btn icon class="mr-5 my-1" style="float: right" @click="inputOpen = false"><v-icon>mdi-close</v-icon></v-btn>
        <v-expansion-panels accordion flat multiple v-model="openPanels">
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
            <v-expansion-panel readonly>
                <v-divider></v-divider>
                <v-expansion-panel-header>Input Rooms Manually</v-expansion-panel-header>
                <v-divider></v-divider>
            </v-expansion-panel>
            <v-expansion-panel readonly>
                <v-divider></v-divider>
                <v-expansion-panel-header>Input Events Manually</v-expansion-panel-header>
                <v-divider></v-divider>
            </v-expansion-panel>
        </v-expansion-panels>
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
    <span v-if="currentPage == 'Solution'"><v-container fluid><v-row class="fill-width">
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
                    :interval-count="room.closes-room.opens+2"
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

    mounted() {
        document.title = "Event Scheduler"
    },

    data: () => ({
        error: false,
        errorText: false,
        navOpen: false,
        inputOpen: false,
        currentPage: "Home",
        roomHeaders: [
            {text: "Name", value: "name", sortable: true, align: "start"},
            {text: "Capacity", value: "capacity", sortable: true},
            {text: "Opens (24h)", value: "opens", sortable: true},
            {text: "Closes (24h)", value: "closes", sortable: true},
            {text: "Actions", value: "actions", sortable: false},
        ],
        eventsHeaders: [
            {text: "Name", value: "name", sortable: true, align: "start"},
            {text: "Attendance", value: "attendance", sortable: true},
            {text: "Starts (24h)", value: "starts", sortable: true},
            {text: "Ends (24h)", value: "ends", sortable: true},
            {text: "Actions", value: "actions", sortable: false},
        ],
        openPanels: [0],
        whichDialog: "",
        deleteIndex: -1,
        deleteOpen: false,
        editIndex: -1,
        editOpen: false,
        editRoom: {
            name: '',
            capacity: -1,
            opens: 0,
            closes: 24,
        },
        editEvent: {
            name: '',
            attendance: -1,
            starts: 0,
            ends: 24,
        },
        rules: {
            names: [v => v.length > 0 || "Name Required"],
            people: [
                v => parseFloat(v) > 0 || "Must be greater than 0",
                v => parseInt(v) === parseFloat(v) || "Must be a whole number"
            ],
            times: [v => (parseFloat(v) >= 0 && parseFloat(v) <= 24) || "Time must be between 0 and 24"]
        },
        roomsData: [{name: "Room1",  capacity: 30, opens: 8, closes: 17}, {name: "Room2",  capacity: 30, opens: 8, closes: 17}, {name: "Room3",  capacity: 30, opens: 8, closes: 17}, {name: "Room4",  capacity: 30, opens: 8, closes: 17}, {name: "Room5",  capacity: 30, opens: 8, closes: 17}, {name: "Room7",  capacity: 30, opens: 8, closes: 17}, {name: "Room8",  capacity: 30, opens: 8, closes: 17}],
        eventsData: [{name: "meeting1", attendance: 23, starts: 10, ends: 10.5}, {name: "meeting2", attendance: 23, starts: 10, ends: 11.5}],
        fileTypes: ".json,.csv,.tsv,.txt,.xmls",
        colors: ["red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue", "cyan", "teal", "green", "light-green", "lime", "amber", "orange", "deep-orange", "brown", "blue-grey"],
        roomsFile: null,
        eventsFile: null,
        roomsManual: [],
        eventsManual: [],
        solution: null,
    }),

    methods: {
        changePage(pageTitle) {
            this.currentPage = pageTitle
            this.navOpen = false
        },
        panelIcon(panel) {
            switch(panel) {
                case 0:
                    return this.openPanels.includes(0) ? 'mdi-chevron-up' : ((this.roomsFile || this.eventsFile) ? 'mdi-check' : 'mdi-chevron-up')
                default:
                    return 'mdi-chevron-down'
            }
        },
        editItem(item, which) {
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
            this.editOpen = false
            this.editIndex = -1
        },
        save() {
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
            if (this.whichDialog == "room") {
                this.roomsData.splice(this.deleteIndex)
            } else {
                this.eventsData.splice(this.deleteIndex)
            }
            this.deleteOpen = false
            this.deleteIndex = -1
        },
        closeDelete() {
            this.deleteOpen = false
            this.deleteIndex = -1
        },
        callAlgorithm() {
            axios({
                method: "post",
                url: "http://localhost:8000/schedule",
                data: {rooms: this.roomsData, events: this.eventsData}
            }).then( r=> {
                if ("error" in r.data) {
                    this.error = true
                    this.errorText = r.data.error
                    return
                }
                this.solution = r.data.solution
                this.changePage("Solution")
                console.log(this.solution)
            }).catch(error => {
                console.log(error)
            })
        },
        inputData() {
            if (this.roomsFile || this.eventsFile) {
                var formData = new FormData()
                if (this.roomsFile) {
                    formData.append("rooms", this.roomsFile)
                }
                if (this.eventsFile) {
                    formData.append("events", this.eventsFile)
                }
                axios({
                    method: "post",
                    url: "http://localhost:8000/upload",
                    data: formData
                }).then( r=> {
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
                    this.error = true
                    this.errorText = error
                })
            }
            this.inputOpen = false
        },
        decimalToTime(decimal) {
            var hour = Math.floor(decimal)
            var remainder = decimal - hour
            var minute = Math.round(remainder*(60)).toString()

            if (minute.length < 2) {
                minute = "0" + minute
            }

            return hour.toString() + ":" + minute
        },
        getEvents(eventList) {
            var out = []
            for (var i=0; i<eventList.length; i++) {
                if (!("color" in eventList[i])) {
                    eventList[i].color = this.colors[Math.floor(Math.random() * this.colors.length)]
                }
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
            return event.color
        },
    },

    computed: {
        validateInput() {
            return this.roomsFile || this.eventsFile
        },
        validateEdit() {
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
            return [
                {title: "Home", icon: "mdi-home", disabled: false},
                {title: "Solution", icon: "mdi-calendar-check", disabled: this.solution === null},
            ]
        },
    }
};
</script>

<style scoped>
.fill-width {
  overflow-x: auto;
  flex-wrap: nowrap;
}
</style>
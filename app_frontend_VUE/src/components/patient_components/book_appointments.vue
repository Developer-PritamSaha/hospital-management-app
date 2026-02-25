<script setup>
import { ref, onMounted} from "vue";
import router from "@/router";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    doc_name: '',
    availabilities: [],
    availCount: 0,
    week_start_date: '0000-00-00',
    week_end_date: '0000-00-00',
    isLoading: false,
    error: null,
})

async function loadAvailabilities() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/book-appointment", 
          {
            params: {
                "doctor_public_id": globalTemp.get("doctor_public_id")
            }
          })
        data.value.doc_name = response.data?.doctor_name
        data.value.availCount = response.data?.count
        data.value.week_start_date = response.data?.week_start_date
        data.value.week_end_date = response.data?.week_end_date
        data.value.availabilities = response.data?.availabilities
    } catch (err) {
        data.value.availCount = 0
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Doctor availability schedule loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

const alertPlaceholder = ref(null)
function appendAlert(message, type, icon) {
    if (!alertPlaceholder.value) return

    alertPlaceholder.value.innerHTML = `
    <div class="position-fixed top-1 end-0 p-4" style="z-index: 1055">
        <div class="alert alert-${type} alert-dismissible fade show text-center" role="alert">
            <i class="bi ${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    </div>
    `
  // disappear after 5 seconds
  setTimeout(() => {
    if (alertPlaceholder.value) {
      alertPlaceholder.value.innerHTML = ''
    }
  }, 5000)
}

const selectedSlot = ref(null)
function selectTimeSlot(slot_id, date, start_time, end_time){
    if (selectedSlot.value?.slot_id === slot_id){
        selectedSlot.value = null
    } else {
        selectedSlot.value = {
            slot_id: slot_id,
            slot_date: date,
            slot_start_time: start_time,
            slot_end_time: end_time
        }
    }
}

const isProcessing = ref(false)
async function bookAppointment() {
    if (isProcessing.value || selectedSlot.value === null) return

    isProcessing.value = true
    try {
        const response = await axios_instance.post("/api/dashboard/patient/book-appointment", 
          {
            "doctor_public_id": globalTemp.get("doctor_public_id"),
            "slot_id": selectedSlot.value.slot_id,
            "slot_date": selectedSlot.value.slot_date,
            "slot_start_time": selectedSlot.value.slot_start_time,
            "slot_end_time": selectedSlot.value.slot_end_time
          }
        )
        
        globalTemp.set('PatientBookingStatus', "success")
        globalTemp.set('BookingDate', `${selectedSlot.value.slot_date}`)
        globalTemp.set('BookingStartTime', `${selectedSlot.value.slot_start_time}`)
        globalTemp.set('BookingEndTime', `${selectedSlot.value.slot_end_time}`)
        router.replace("/dashboard/patient/appointments")

        // appendAlert(`Slot ${selectedSlot.value.slot_id} booked!`, "success", "bi-check-circle")

    } catch (err) {
        let msg = err.response?.data?.message || "Appointment failed"
        if(err.response?.status === 409){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
        } else{
            // console.log(err)
            appendAlert("Failed to book the appointment.", "danger", "bi-exclamation-triangle")
        }
    } finally {
        isProcessing.value = false
    }
}


onMounted(() => {
    loadAvailabilities()
})

const refreshAvailability = () => {
  loadAvailabilities()
}

</script>

<template>
    <div class="container-fluid">
        <div class="row g-3">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-1">
                <div class="d-flex align-items-center">
                    <router-link v-if="globalTemp.get('from') == 'doctor-list'" to="/dashboard/patient/doctor-list">
                        <button type="button" class="btn btn-sm border-0 text-secondary" title="Back">
                            <i class="bi bi-arrow-left-square fs-4 pe-2"></i>
                        </button>
                    </router-link>

                    <router-link v-else-if="globalTemp.get('from') == 'appointments'" to="/dashboard/patient/appointments">
                        <button type="button" class="btn btn-sm border-0 text-secondary" title="Back">
                            <i class="bi bi-arrow-left-square fs-4 pe-2"></i>
                        </button>
                    </router-link>

                   <h2 class="h4 fw-bold" style="color: #220349;">{{ data.doc_name }}'s Availability</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshAvailability" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                    
                <span class="badge week-badge-bg px-3 py-2 text-info">From {{ data.week_start_date }} to {{ data.week_end_date }}</span>
            </div>

            <div class="table-container shadow border-2">
                <div class="table-responsive ">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Date (Y-M-D)</th>
                                <th class="text-center">Weekday</th>
                                <th class="text-center">Time Slot 1</th>
                                <th class="text-center">Time Slot 2</th>
                                <th class="text-center">Time Slot 3</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-if="data.isLoading">
                                <td colspan="5" class="py-5 text-center text-muted">
                                    <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                                </td>
                            </tr>

                            <tr v-else-if="data.error">
                                <td colspan="5" class="py-5 text-center text-danger fw-medium">
                                    {{ data.error }}
                                </td>
                            </tr>

                            <tr v-else-if="data.availCount !== 7">
                                <td colspan="5" class="py-5 text-center text-primary fw-medium">Doctor has not provided availabilities for this week yet.</td>
                            </tr>

                            <tr v-else v-for="(avail) in data.availabilities" :key="avail.weekday">
                                <td class="text-center"><div class="date-badge fw-bold">{{ avail.date }}</div></td>
                                <td class="text-center"><span class="fw-bold highlight-text fs-6">{{ avail.weekday }}</span></td>

                                <td class="text-muted text-center">
                                  <button @click="selectTimeSlot(avail.slots[0].slot_id,avail.date, avail.slots[0].start_time, avail.slots[0].end_time)" class="border-0 btn" title="Select Time Slot" :id="avail.slots[0].slot_id"
                                  :disabled="!avail.slots[0].status || (selectedSlot && selectedSlot.slot_id !== avail.slots[0].slot_id)">
                                    <div class="time-slot-pill" 
                                    :class="avail.slots[0].status ? 'available' : 'unavailable',
                                    selectedSlot?.slot_id === avail.slots[0].slot_id ? 'selected' : 'not-selected' " >
                                        {{ avail.slots[0].start_time  }} to {{ avail.slots[0].end_time }}
                                    </div>
                                  </button>
                                </td>


                                <td class="text-muted text-center">
                                  <button @click="selectTimeSlot(avail.slots[1].slot_id, avail.date, avail.slots[1].start_time, avail.slots[1].end_time)" class="border-0 btn" title="Select Time Slot" :id="avail.slots[1].slot_id"
                                  :disabled="!avail.slots[1].status || (selectedSlot && selectedSlot.slot_id !== avail.slots[1].slot_id)">
                                    <div class="time-slot-pill" 
                                    :class="avail.slots[1].status ? 'available' : 'unavailable',
                                    selectedSlot?.slot_id === avail.slots[1].slot_id ? 'selected' : 'not-selected' ">
                                        {{ avail.slots[1].start_time  }} to {{ avail.slots[1].end_time }}
                                    </div>
                                  </button>
                                </td>

                                
                                <td class="text-muted text-center">
                                  <button @click="selectTimeSlot(avail.slots[2].slot_id, avail.date, avail.slots[2].start_time, avail.slots[2].end_time)" class="border-0 btn" title="Select Time Slot" :id="avail.slots[2].slot_id"
                                  :disabled="!avail.slots[2].status || (selectedSlot && selectedSlot.slot_id !== avail.slots[2].slot_id)">
                                    <div class="time-slot-pill" 
                                    :class="avail.slots[2].status ? 'available' : 'unavailable',
                                    selectedSlot?.slot_id === avail.slots[2].slot_id ? 'selected' : 'not-selected' ">
                                        {{ avail.slots[2].start_time  }} to {{ avail.slots[2].end_time }}
                                    </div>
                                  </button>
                                </td>

                            </tr>
                          
                        </tbody>
                    </table>
                </div>

                <div v-if="!data.isLoading & !data.error & data.availCount === 7" class="col-12 p-3 d-flex justify-content-center gap-2">
                    <router-link to="/dashboard/patient/doctor-list"><button type="button" class="btn px-4 rounded-pill clear-btn">
                        Back
                    </button></router-link>
                    <button @click="bookAppointment" class="btn px-4 text-white rounded-pill shadow-sm book-btn" v-if="isProcessing" :disabled="isProcessing" id="clicked">
                        <span>Booking...</span>
                    </button>
                    <button @click="bookAppointment"" class="btn px-4 text-white rounded-pill shadow-sm book-btn" v-else 
                    :disabled="selectedSlot === null">
                        <span>Book</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.table-container {
    background: white;
    border-radius: 15px;
    overflow: hidden;
}

.table-style {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}

.table-style thead th {
    background-color: #b4e3f569;
    color: #40576b;
    font-weight: 650;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
    padding: 16px 20px;
    border-bottom: 1px solid #edf2f7;
}

.table-style tbody td {
    padding: 16px 20px;
    border-bottom: 1px solid #f1f3f5;
    vertical-align: middle;
    color: #495057;
    font-size: 0.9rem;
}

.table-style tbody tr:hover {
    background-color: #f9faff;
}

.time-slot-pill {
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 600;
}

.time-slot-pill.available.selected {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #109670;
}

.time-slot-pill.available {
    background-color: #f8fdfd;
    color: #531cb9;
    border-style: solid;
    border-color: #9e7ff3;
}

.time-slot-pill.unavailable {
    background-color: #dad6d6a9;
    color: #4e4e4e;
    border-style: solid;
    border-color: #524f4f88;
    cursor: not-allowed;
}

.book-btn {
    align-items: center;
    background: linear-gradient(135deg,#7652b4, #4b2c89, #3b1e79); 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.book-btn:hover {
    background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
    color:white;
}
#clicked {
    background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
    color:white;
    cursor:not-allowed;
}
.clear-btn{
    background:#eaeafa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(154, 153, 153);
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.clear-btn:hover{
    background:#e2e2fa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(116, 115, 115);
}

.date-badge {
    background: #acb0ee96;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #08305ffa;
}

.week-badge-bg{
  background-color: #012c55c2;
}

.highlight-text{
    color: #7845d6;
    font-weight: 600;
}

</style>
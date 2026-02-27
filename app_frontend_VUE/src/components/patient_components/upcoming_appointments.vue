<script setup>
import { ref, onMounted} from "vue";
import axios_instance from "@/axiosSetup";
import router from "@/router";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    appointments: [],
    appointCount: 0,
    week_start_date: '0000-00-00',
    week_end_date: '0000-00-00',
    isLoading: false,
    error: null,
})

async function loadAppointments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/upcoming-appointments")
        data.value.appointCount = response.data?.count
        data.value.week_start_date = response.data?.week_start_date
        data.value.week_end_date = response.data?.week_end_date
        data.value.appointments = response.data?.appointments
        // appendAlert("Upcoming Appointments Loaded Succesfully", "success", "bi-check-circle")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.appointCount = 0
        appendAlert("Upcoming Appointments Loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredAppointments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/upcoming-appointments/search",
        {  
            params: {
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.appointCount = response.data?.count
        data.value.week_start_date = response.data?.week_start_date
        data.value.week_end_date = response.data?.week_end_date
        data.value.appointments = response.data?.appointments
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.appointCount = 0
        
        if (err.response?.status === 404){
            appendAlert("Searched appointment(s) not found.", "info", "bi-info-circle")
        }
        else{
            appendAlert("Searched Upcoming Appointments Loading failed.", "danger", "bi-exclamation-triangle")
        }
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

const appointToBeCanceled = ref(null)
const selectAppoint = (appoint_pub_id) => {
    appointToBeCanceled.value = appoint_pub_id
}

// Handle appointments canceling
async function changeAppointmentStatus(appoint_pub_id, appoint_status) {
    try {
        const response = await axios_instance.patch("/api/dashboard/patient/upcoming-appointments", 
          {
            "appointment_public_id": appoint_pub_id,
            "status": appoint_status
          }
        )
        appendAlert(`Appointment ${appoint_pub_id} has been canceled.`,'success',"bi-check-circle")
        loadAppointments()
    } catch (err) {
        let msg = err.response?.data?.message || "Failed to cancel the appointment"
        if(err.response?.status === 409){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
            loadAppointments()
        } 
        else if(err.response?.status === 400){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
        } 
        else {
            appendAlert(`Appointment ${appoint_pub_id} cannot be canceled.`, "danger", "bi-exclamation-triangle")
        }
    }
}

// Load Completed Appointment treatment data
const treatmentData = ref(null)
const ap_doc_name = ref("NA")
const treatmentDataLoading = ref(false)
const treatmentDataError = ref(null)
async function loadTreatmentData(ap_pub_id, doc_name) {
    treatmentData.value = "Empty"
    treatmentDataLoading.value = true
    treatmentDataError.value = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/appointment-treatment",{
            params: {
                "appointment_public_id": ap_pub_id
            }
        })
        if (response?.data.status === "available"){
            treatmentData.value = response?.data
            ap_doc_name.value = doc_name
        }
        else{
            treatmentDataError.value = "Treatment Data Unavailable."
        }

    } catch (err) {
        treatmentDataError.value = err.response?.data?.message || err.message
        appendAlert("Treatment Data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        treatmentDataLoading.value = false
    }
}

// Handle Reschedule Appointment
function rescheduleAppointment(doc_public_id){
    globalTemp.set("doctor_public_id", doc_public_id)
    globalTemp.set("from", "appointments")
    router.replace('/dashboard/patient/book-appointment')
}

onMounted(() => {
    if(globalTemp.get('PatientBookingStatus') === 'success'){
        appendAlert(`Doctor Appointment on ${globalTemp.get('BookingDate')} from (${globalTemp.get('BookingStartTime')} - ${globalTemp.get('BookingEndTime')}) booked successfully!`, "info", "bi-check-circle")

        globalTemp.reset('PatientBookingStatus')
        globalTemp.reset('BookingDate')
        globalTemp.reset('BookingStartTime')
        globalTemp.reset('BookingEndTime')
        globalTemp.reset('department_name')
        globalTemp.reset('from')
    }
    if(globalTemp.get('searchResource') === 'upcoming-appointments'){
        globalTemp.reset('searchResource')
        loadFilteredAppointments()
    }
    else{
        loadAppointments()
    }
   
})

const refreshAppointments = () => {
  loadAppointments()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-1">
                <div class="d-flex align-items-center">
                    <h2 class="h4 fw-bold" style="color: #220349;">Upcoming Appointments</h2> 
                    
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshAppointments" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                <span class="badge week-badge-bg px-3 py-2 text-info">From {{ data.week_start_date }} to {{ data.week_end_date }}</span>
                <!-- <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.appointCount }}</span> -->
            </div>
            
            <div class="table-container shadow-sm border-1">
                <div class="table-responsive">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Id</th>
                                <th class="text-center">Doctor Info</th>
                                <th class="text-center">Department</th>
                                <th class="text-center">Date (Y-M-D)</th>
                                <th class="text-center">Time (24 hr.)</th>
                                <th class="text-center">Status</th>
                                <th class="text-center">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-if="data.isLoading">
                                <td colspan="7" class="py-5 text-center text-muted">
                                    <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                                </td>
                            </tr>

                            <tr v-else-if="data.error">
                                <td colspan="7" class="py-5 text-center text-danger fw-medium">
                                    {{ data.error }}
                                </td>
                            </tr>

                            <tr v-else-if="data.appointCount === 0">
                                <td colspan="7" class="py-5">
                                    <div class="d-flex flex-column align-items-center justify-content-center">
                                        <img src="@/assets/images/undraw_workout_wqgp.svg" 
                                            class="img-fluid mb-4" 
                                            style="max-width: 550px; width: 100%;" 
                                            alt="No appointments">
                                        <small class="fs-6 text-primary fw-medium">No doctor appointment booked yet.</small>
                                    </div>
                                </td>
                            </tr>

                            <tr v-else v-for="(appoint) in data.appointments" 
                            :key="appoint.appointment_public_id">
                                <td><div class="text-center highlight-text fw-bold">{{ appoint.appointment_public_id }}</div></td>
                                <td>
                                    <div class="d-flex flex-column">
                                        <span class="text-center fw-bold" style="color: #6b27d9;">
                                            {{ appoint.doctor_full_name }}
                                        </span>
                                        <small class="text-center text-muted fw-bold">{{ appoint.doctor_public_id }}</small>
                                    </div>
                                </td>
                                <td><div class="text-center spec-tag">{{ appoint.doctor_department }}</div></td>
                                <td><div class="text-center text-primary fw-medium">{{ appoint.date }}</div></td>
                                <td><div class="text-center text-success fw-medium">
                                    {{ appoint.start_time }} to {{ appoint.end_time }}
                                </div></td>

                                <td class="text-center">
                                    <div v-if="appoint.status === 'completed'" class="status-pill completed">
                                        Completed
                                    </div>
                                    <div v-else-if="appoint.status === 'canceled'" class="status-pill canceled">
                                        Canceled
                                    </div>
                                    <div v-else class="status-pill booked">
                                        Booked
                                    </div>
                                </td>
                                
                                <td class="text-center">
                                    <div>
                                        <button @click="selectAppoint(appoint.appointment_public_id)" type="button" class="cancel-appointment-btn px-4 rounded-pill btn" 
                                        title="Cancel Appointment" data-bs-toggle="modal" data-bs-target="#cancelAppointmentModal" v-if="appoint.status === 'booked'">
                                            <div>
                                                <i class="bi bi-calendar-x pe-1 "></i>
                                                Cancel
                                            </div>
                                        </button>

                                        <button @click="loadTreatmentData(appoint.appointment_public_id,appoint.doctor_full_name)" type="button" class="view-treatment-btn px-4 rounded-pill btn" 
                                        title="View Treatment" data-bs-toggle="modal" data-bs-target="#treatmentDataModal" v-if="appoint.status === 'completed'">
                                            <div>
                                                <i class="bi bi-clipboard2-check pe-1 "></i>
                                                View
                                            </div>
                                        </button>

                                        <button @click="rescheduleAppointment(appoint.doctor_public_id)" type="button" class="reschedule-appointment-btn px-4 rounded-pill btn" 
                                        title="Reschedule Appointment" v-if="appoint.status === 'canceled'">
                                            <div>
                                                <i class="bi bi-calendar-check pe-1 "></i>
                                                Reschedule
                                            </div>
                                        </button>
                                    </div>
                                </td>
                                
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Confirm Appointment Cancel Modal -->
            <div class="modal fade" id="cancelAppointmentModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-sm"> 
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-body text-center p-3">
                        <div class="delete-icon-wrapper mb-3">
                            <i class="bi bi-exclamation-circle text-danger"></i>
                        </div>
                        
                        <h5 class="fw-bold mb-2">Confirm Cancel</h5>
                        <p class="text-muted mb-0">Are you sure you want to cancel</p>
                        <p class="fw-bold text-dark" v-if="appointToBeCanceled">{{ appointToBeCanceled }}?</p>
                        <small class="text-secondary d-block mt-2">This action cannot be undone.</small>
                    </div>
                    
                    <div class="modal-footer border-0 d-flex justify-content-center pb-4">
                        <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm back-btn" data-bs-dismiss="modal">Back</button>
                        <button @click="changeAppointmentStatus(appointToBeCanceled, 'canceled')" type="button" class="btn px-4 mx-2 rounded-pill shadow-sm cancel-btn" data-bs-dismiss="modal">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
            </div>

            <!-- Treatment Data Modal -->
            <div class="modal fade" id="treatmentDataModal" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered modal-lg"> 
                <div class="modal-content border-1 shadow-lg" v-if="treatmentData">
                    <div class="modal-header">
                        <h5 class="modal-title h5 fw-bold mb-0" style="color: #220349;">Treatment Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div v-if="treatmentDataLoading" class="modal-body text-center p-3">
                        <div class="text-center p-4">
                            <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                        </div>
                        
                    </div>

                    <div v-else-if="treatmentDataError" class="modal-body text-center p-3">
                        <p class="text-danger fw-medium p-4">{{ treatmentDataError }}</p>
                    </div>

                    <div v-else class="modal-body p-3">
                        <div class="row g-2">
                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-bold small highlight-text">Appointment ID</label>
                                <input :value="treatmentData.appointment_public_id" type="text" class="form-control fw-bold input-fields" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>
                            <div class="col-md-5 mb-2">
                                <label class="form-label fw-bold small highlight-text">Doctor Name</label>
                                <input :value="ap_doc_name" type="text" class="form-control fw-semibold input-fields" 
                                style="border: 1px solid #b59ff3" disabled>
                            </div>
                            <div class="col-md-4 mb-2">
                                <label class="form-label fw-bold small highlight-text">Visit Type</label>
                                <input :value="treatmentData.visit_type" type="text" class="form-control fw-semibold input-fields" 
                                style="border: 1px solid #b59ff3" disabled>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Tests Done</label>
                                <textarea :value="treatmentData.test_done" type="text" class="form-control text-primary fw-semibold input-fields" rows="3"
                                disabled></textarea>
                            </div>
                            
                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Diagnosis</label>
                                <textarea :value="treatmentData.diagnosis" type="text" class="form-control text-danger fw-semibold input-fields" rows="3"
                                disabled></textarea>
                            </div>
                            
                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Medicines</label>
                                <textarea :value="treatmentData.medicine" type="text" class="form-control text-success fw-semibold input-fields" rows="3"
                                disabled></textarea>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Prescription</label>
                                <textarea :value="treatmentData.prescription" type="text" class="form-control text-muted fw-semibold input-fields" rows="3"
                                disabled></textarea>
                            </div>

                            <div class="col-md-12 mb-3">
                                <label class="form-label fw-bold small highlight-text">Notes</label>
                                <textarea :value="treatmentData.notes" type="text" class="form-control text-muted fw-semibold input-fields" rows="3"
                                disabled></textarea>
                            </div>
                      </div>
                      
                      <div class="modal-footer border-0 d-flex justify-content-center pb-2">
                          <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm back-btn" data-bs-dismiss="modal">Close</button>
                      </div>
                    </div>
                </div>
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
    background-color: #eaf1fd;
    color: #40576b;
    font-weight: 600;
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
    background-color: #f9ffff;
}


.highlight-text{
    color: #341079;
    font-weight: 700;
}

.cancel-appointment-btn{
    align-items: center;
    background: linear-gradient(135deg,#c77e7eee, #bb4e4eec, #a13c3ce8); 
    color: white;
    border: 1px solid rgb(150, 149, 149);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    min-width: 145px;
}
.cancel-appointment-btn:hover{
    background: linear-gradient(135deg,#dd9696f3, #d37070f3, #b16363f3);
    color:white;
    border: 1px solid rgb(131, 130, 130);
}

.reschedule-appointment-btn{
    align-items: center;
    background: linear-gradient(135deg,#8d88cfee, #4e50bbec, #3e3ca1e8); 
    color: white;
    border: 1px solid rgb(136, 135, 135);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    min-width: 145px;
}
.reschedule-appointment-btn:hover{
    background: linear-gradient(135deg,#9697ddf6, #7a70d3f6, #6364b1f6);
    color:white;
    border: 1px solid rgb(131, 130, 130);
}

.view-treatment-btn{
    align-items: center;
    background: linear-gradient(135deg,#479481ee, #297260ec, #225e57e8); 
    color: white;
    border: 1px solid rgb(163, 162, 162);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    min-width: 145px;
}
.view-treatment-btn:hover{
    background: linear-gradient(135deg,#58ac97ee, #31816dec, #276860e8);
    color:white;
    border: 1px solid rgb(131, 130, 130);
}

.spec-tag {
    background: #f4f1f9;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #123567;
}

.status-pill {
    padding: 4px 8px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-pill.completed {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #15b98b;
}

.status-pill.booked {
    background-color: #faf4c1;
    color: #a3560e;
    border-style: solid;
    border-color: #d4ae2f;
}

.status-pill.canceled {
    background-color: #ffcdcda9;
    color: #9c1b1b;
    border-style: solid;
    border-color: #f8333388;
}

.count-bg{
  background-color: #9e81ec;
}
.week-badge-bg{
  background-color: #012c55c2;
}

.back-btn{
    background:#eaeafa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(154, 153, 153);
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.back-btn:hover{
    background:#e2e2fa;
    border: 1px solid rgb(116, 115, 115);
}

.cancel-btn {
    align-items: center;
    background: #cc3d33; 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.cancel-btn:hover {
    background: #b93030;
    color:white;
}

</style>
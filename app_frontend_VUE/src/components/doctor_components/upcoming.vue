<script setup>
import { ref, onMounted, inject} from "vue";
import axios_instance from "@/axiosSetup";
import router from "@/router";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()
const triggerAlert = inject('triggerChildAlert')

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
        const response = await axios_instance.get("/api/dashboard/doctor/appointments")
        data.value.appointCount = response.data?.count
        data.value.week_start_date = response.data?.week_start_date
        data.value.week_end_date = response.data?.week_end_date
        data.value.appointments = response.data?.appointments
        // triggerAlert("Upcoming Appointments Loaded Succesfully", "success", "bi-check-circle")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.appointCount = 0
        triggerAlert("Upcoming Appointments Loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredAppointments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/appointments/search",
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
            triggerAlert("Searched appointment(s) not found.", "info", "bi-info-circle")
        }
        else{
            triggerAlert("Searched Upcoming Appointments Loading failed.", "danger", "bi-exclamation-triangle")
        }
    } finally {
        data.value.isLoading = false
    }
}

const appointToBeCanceled = ref(null)
const selectAppoint = (appoint_pub_id) => {
    appointToBeCanceled.value = appoint_pub_id
}

// Handle appointments canceling or completing
async function changeAppointmentStatus(appoint_pub_id, appoint_status) {
    try {
        const response = await axios_instance.patch("/api/dashboard/doctor/appointments", 
          {
            "appointment_public_id": appoint_pub_id,
            "status": appoint_status
          }
        )
        if(appoint_status === 'completed'){
            triggerAlert(`Appointment ${appoint_pub_id} marked as completed.`,'success',"bi-check-circle")
        } else{
            appointToBeCanceled.value = null
            triggerAlert(`Appointment ${appoint_pub_id} has been canceled.`,'success',"bi-check-circle")
        }
        loadAppointments()
    } catch (err) {
        let msg = err.response?.data?.message || "Failed to change the appointment status"
        if(err.response?.status === 409){
            triggerAlert(msg, "warning", "bi-exclamation-octagon")
            loadAppointments()
        } 
        else if(err.response?.status === 400){
            triggerAlert(msg, "warning", "bi-exclamation-octagon")
        } 
        else {
            if(appoint_status === 'completed'){
                triggerAlert(`Appointment ${appoint_pub_id} cannot be marked as completed.`, "danger", "bi-exclamation-triangle")
            } else{
                triggerAlert(`Appointment ${appoint_pub_id} cannot be canceled.`, "danger", "bi-exclamation-triangle")
            }
        }
    }
}

// Handle patient data updatation
function updatePatientHistory(ap) {
    globalTemp.set("appointment_details", ap)
    // triggerAlert(`Appointment ${ap.appointment_public_id} patient history updated.`,'success',"bi-check-circle")
    router.push('/dashboard/doctor/patient-treatment')
}

onMounted(() => {
     if(globalTemp.get('PatientHistoryUpdated') === 'success'){
        triggerAlert(`${globalTemp.get('PatDetails').name}(${globalTemp.get('PatDetails').pub_id}) history updated successfully!`, "info", "bi-check-circle")
        globalTemp.reset('PatientHistoryUpdated')
        globalTemp.reset('PatDetails')
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
    <div class="row g-2">        
        <div class="d-flex justify-content-between align-items-center mb-2">
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
                            <th class="text-center">Patient Info</th>
                            <th class="text-center">Date (Y-M-D)</th>
                            <th class="text-center">Time (24 hr.)</th>
                            <th class="text-center">Patient History</th>
                            <th class="text-center">Actions</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-if="data.isLoading">
                            <td colspan="6" class="py-5 text-center text-muted">
                                <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                            </td>
                        </tr>

                        <tr v-else-if="data.error">
                            <td colspan="6" class="py-5 text-center text-danger fw-medium">
                                {{ data.error }}
                            </td>
                        </tr>

                        <tr v-else-if="data.appointCount === 0">
                            <td colspan="6" class="py-5">
                                <div class="d-flex flex-column align-items-center justify-content-center">
                                    <img src="@/assets/images/undraw_medicine_hqqg.svg" 
                                        class="img-fluid mb-4" 
                                        style="max-width: 500px; width: 100%;" 
                                        alt="No appointments">
                                    <small class="fs-6 text-primary fw-medium">No patient booked appointment yet.</small>
                                </div>
                            </td>
                        </tr>

                        <tr v-else v-for="(appoint) in data.appointments" 
                        :key="appoint.appointment_public_id">
                            <td class="text-center text-muted fw-bold">{{ appoint.appointment_public_id }}</td>
                            <td>
                                <div class="d-flex flex-column">
                                    <span class="text-center fw-bold" style="color: #6b27d9;">
                                        {{ appoint.patient_full_name }}
                                    </span>
                                    <small class="text-center text-muted fw-bold">{{ appoint.patient_public_id }}</small>
                                </div>
                            </td>
                            <td><div class="text-center date-tag fw-medium">{{ appoint.date }}</div></td>
                            <td><div class="text-center text-success fw-medium">
                                {{ appoint.start_time }} to {{ appoint.end_time }}
                            </div></td>

                            <td class="text-center">
                                <div>
                                    <button 
                                    @click="updatePatientHistory(appoint)" class="border-0 btn" title="Update History">
                                        <div class="button-pill history">
                                            <i class="bi bi-clipboard2-plus pe-1"></i>
                                             Update
                                        </div>
                                    </button>
                                </div>
                            </td>
                            
                            <td class="text-center">
                                <div>
                                    <button @click="changeAppointmentStatus(appoint.appointment_public_id, 'completed')" class="border-0 btn" title="Mark Complete" :disabled="!appoint.is_treatment_exist">
                                        <div class="button-pill complete">
                                            <i class="bi bi-check2-circle pe-1"></i>
                                             Mark Complete
                                        </div>
                                    </button>
                                    <button @click="selectAppoint(appoint.appointment_public_id)" class="border-0 btn" title="Mark Cancel" data-bs-toggle="modal" data-bs-target="#cancelAppointmentModal">
                                        <div class="button-pill cancel">
                                            <i class="bi bi-x-circle pe-1 "></i>
                                            Mark Cancel
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

.button-pill {
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

.button-pill.complete {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #15b98b;
}

.button-pill.cancel {
    background-color: #fef2f2;
    color: #b91c1c;
    border-style: solid;
    border-color: #f06868;
}

.button-pill.history {
    background-color: #f2f2fe;
    color: #1c24b9;
    border-style: solid;
    border-color: #7e8eeb;
}

.date-tag {
    background: #f4f1f9;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #123567;
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
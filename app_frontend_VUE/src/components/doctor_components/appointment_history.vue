<script setup>
import { ref, onMounted, inject} from "vue";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()
const triggerAlert = inject('triggerChildAlert')

const data = ref({
    appointments: [],
    appointCount: 0,
    isLoading: false,
    error: null,
})

async function loadAppointments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/appointments",
        {  
            params: {
                "duration": "history"
            }
        })
        data.value.appointCount = response.data?.count
        data.value.appointments = response.data?.appointments
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.appointCount = 0
        triggerAlert("Appointment history loading failed.", "danger", "bi-exclamation-triangle")
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
                "duration": "history",
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.appointCount = response.data?.count
        data.value.appointments = response.data?.appointments
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.appointCount = 0
        
        if (err.response?.status === 404){
            triggerAlert("Searched appointment(s) not found.", "info", "bi-info-circle")
        }
        else{
            triggerAlert("Searched Appointment history loading failed.", "danger", "bi-exclamation-triangle")
        }
    } finally {
        data.value.isLoading = false
    }
}


// Load Appointment treatment data
const treatmentData = ref(null)
const ap_pat_name = ref("NA")
const treatmentDataLoading = ref(false)
const treatmentDataError = ref(null)
async function loadTreatmentData(ap_pub_id, pat_name) {
    treatmentData.value = "Empty"
    treatmentDataLoading.value = true
    treatmentDataError.value = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/treatment-data",{
            params: {
                "appointment_public_id": ap_pub_id
            }
        })
        if (response?.data.status === "available"){
            treatmentData.value = response?.data
            ap_pat_name.value = pat_name
        }
        else{
            treatmentDataError.value = "Treatment Data Unavailable."
        }

        // globalTemp.reset("patient_public_id")
    } catch (err) {
        treatmentDataError.value = err.response?.data?.message || err.message
        appendAlert("Treatment Data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        treatmentDataLoading.value = false
    }
}

onMounted(() => {
    
    if(globalTemp.get('searchResource') === 'appointment-history'){
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
                <h2 class="h4 fw-bold" style="color: #220349;">Appointment History</h2> 
                
                <button class="btn btn-sm border-0 text-primary" 
                @click="refreshAppointments" v-if="!data.isLoading" title="Refresh">
                    <i class="bi bi-arrow-clockwise fs-6"></i>
                </button>
                <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                    <i class="bi bi-arrow-repeat fs-6"></i>
                </button>
            </div>
            <!-- <span class="badge week-badge-bg px-3 py-2 text-info">From {{ data.week_start_date }} to {{ data.week_end_date }}</span> -->
            <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.appointCount }}</span>
        </div>
        
        <div class="table-container shadow-sm border-1">
            <div class="table-responsive">
                <table class="table-style">
                    <thead>
                        <tr>
                            <th class="text-center">Id</th>
                            <th class="text-center">Patient Info</th>
                            <th class="text-center">Gender</th>
                            <th class="text-center">Age</th>
                            <th class="text-center">Date (Y-M-D)</th>
                            <th class="text-center">Time (24 hr.)</th>
                            <th class="text-center">Status</th>
                            <th class="text-center">Prescription</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-if="data.isLoading">
                            <td colspan="8" class="py-5 text-center text-muted">
                                <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                            </td>
                        </tr>

                        <tr v-else-if="data.error">
                            <td colspan="8" class="py-5 text-center text-danger fw-medium">
                                {{ data.error }}
                            </td>
                        </tr>

                        <tr v-else-if="data.appointCount === 0">
                            <td colspan="8" class="py-5">
                                <div class="d-flex flex-column align-items-center justify-content-center">
                                    <img src="@/assets/images/undraw_medicine_hqqg.svg" 
                                        class="img-fluid mb-4" 
                                        style="max-width: 500px; width: 100%;" 
                                        alt="No appointments">
                                    <small class="fs-6 text-primary fw-medium">No appointments history available yet.</small>
                                </div>
                            </td>
                        </tr>

                        <tr v-else v-for="(appoint) in data.appointments" 
                        :key="appoint.appointment_public_id">
                            <td><div class="text-center highlight-text fw-bold">{{ appoint.appointment_public_id }}</div></td>
                            <td>
                                <div class="d-flex flex-column">
                                    <span class="text-center fw-bold" style="color: #6b27d9;">
                                        {{ appoint.patient_full_name }}
                                    </span>
                                    <small class="text-center text-muted fw-bold">{{ appoint.patient_public_id }}</small>
                                </div>
                            </td>
                            <td><div class="text-center text-success fw-medium">{{ appoint.patient_gender }}</div></td>
                            <td><div class="text-center text-primary fw-medium">{{ appoint.patient_age }}</div></td>
                            <td><div class="text-center date-tag fw-medium">{{ appoint.date }}</div></td>
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
                                <button @click="loadTreatmentData(appoint.appointment_public_id, appoint.patient_full_name)" type="button" class="view-treatment-btn px-4 rounded-pill btn" 
                                title="View" data-bs-toggle="modal" data-bs-target="#treatmentDataModal" :disabled="appoint.status === 'canceled'">
                                    <div>
                                        <i class="bi bi-clipboard-data pe-1"></i>
                                        View
                                    </div>
                                </button>
                            </td>
                            
                        </tr>
                    </tbody>
                </table>
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
                            <label class="form-label fw-bold small highlight-text">Patient Name</label>
                            <input :value="ap_pat_name" type="text" class="form-control fw-semibold input-fields" 
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
                        <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm close-btn" data-bs-dismiss="modal">Close</button>
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

.view-treatment-btn{
    align-items: center;
    background: linear-gradient(135deg,#8f6ec7ee, #724ebbec, #5c3ca1e8); 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
}
.view-treatment-btn:hover{
    background: linear-gradient(135deg,#ab8fe7, #9170d3, #7f63b1);
    color:white;
}

.view-treatment-btn:disabled{
    background: #ab8be2;
    color:white;
    border: 1px solid rgb(71, 71, 71);
    cursor:not-allowed;
}

.date-tag {
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

.input-fields {
    background-color: #f3f6fa;
    border: 1px solid #cee3fc;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    transition: all 0.2s ease;
}
.input-fields:disabled{
    background-color: #f8fcfb;
    border: 1px solid #bdd5f1;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    transition: all 0.2s ease;
}

.close-btn{
    background:#eaeafa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(154, 153, 153);
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.close-btn:hover{
    background:#e2e2fa;
    border: 1px solid rgb(116, 115, 115);
}

</style>
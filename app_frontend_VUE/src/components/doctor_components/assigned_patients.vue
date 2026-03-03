<script setup>
import { ref, onMounted} from "vue";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    assigned_patients: [],
    patCount: 0,
    isLoading: false,
    error: null,
})

async function loadAssignedPatients() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/assigned-patients")
        data.value.patCount = response.data.count
        data.value.assigned_patients = response.data.assigned_patients
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Patients data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredAssignedPatients() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/assigned-patients/search",
        {  
            params: {
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.patCount = response.data.count
        data.value.assigned_patients = response.data.assigned_patients
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        if (err.response?.status === 404){
            appendAlert("Searched patient(s) not found.", "info", "bi-info-circle")
        }
        else{
            appendAlert("Patients data loading failed.", "danger", "bi-exclamation-triangle")
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


// Handle View Patient Medical History 
function viewPatientMedicalHistory(pat_public_id){
    globalTemp.set("patient_public_id", pat_public_id)
}

onMounted(() => {
    if(globalTemp.get('searchResource') === 'assigned-patients'){
        globalTemp.reset('searchResource')
        loadFilteredAssignedPatients()
    }
    else{
        loadAssignedPatients()
    }

})

const refreshPatients = () => {
  loadAssignedPatients()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                   <h2 class="h4 fw-bold" style="color: #220349;">Assigned Patients</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshPatients" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                
                <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.patCount }}</span>
            </div>

            <div class="table-container shadow-sm border-1">
                <div class="table-responsive">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Patient Info</th>
                                <th class="text-center">Appointment ID</th>
                                <th class="text-center">Date</th>
                                <th class="text-center">Gender</th>
                                <th class="text-center">Age</th>
                                <th class="text-center">Height (cm.)</th>
                                <th class="text-center">Weight (kg.)</th>
                                <th class="text-center">Medical History</th>
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

                            <tr v-else-if="data.patCount === 0">
                                <td colspan="8" class="py-5 text-center text-primary fw-medium">No patient assigned yet.</td>
                            </tr>

                            <tr v-else v-for="(patient) in data.assigned_patients" :key="patient.patient_public_id">
                                <td>
                                    <div class="d-flex flex-column">
                                        <div class="text-center fw-bold" style="color: #6b27d9;">
                                            {{ patient.patient_full_name }}
                                        </div>
                                        <small class="text-center text-muted fw-bold">{{ patient.patient_public_id }}</small>
                                    </div>
                                </td>
                                <td><div class="text-center highlight-text fw-bold">{{ patient.appointment_public_id }}</div></td>
                                <td><div class="text-center date-tag fw-medium">{{ patient.date }}</div></td>
                                <td><div class="text-center text-success fw-medium">{{ patient.patient_gender }}</div></td>
                                <td><div class="text-center text-danger fw-medium">{{ patient.patient_age }} yrs</div></td>
                                <td><div class="text-center text-primary fw-semibold">{{ patient.patient_height }}</div></td>
                                <td><div class="text-center text-primary fw-semibold">{{ patient.patient_weight }}</div></td>

                                <td class="text-center">
                                    <div>
                                        <router-link to="/dashboard/doctor/patient-history">
                                            <button 
                                            @click="viewPatientMedicalHistory(patient.patient_public_id)" type="button" class="view-records-btn px-4 rounded-pill btn" 
                                            title="View Records">
                                                <div >
                                                    <i class="bi bi-clipboard-data pe-1"></i>
                                                    View Records
                                                </div>
                                            </button>  
                                        </router-link>
                                    </div>
                                </td>

                            </tr>
                        </tbody>
                    </table>
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

.view-records-btn{
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
.view-records-btn:hover{
    background: linear-gradient(135deg,#58ac97ee, #31816dec, #276860e8);
    color:white;
    border: 1px solid rgb(131, 130, 130);
}

.count-bg{
  background-color: #9e81ec;
}

.date-tag {
    background: #f4f1f9;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #123567;
}


</style>
<script setup>
import { ref, onMounted} from "vue";
import axios_instance from "@/axiosSetup";
import router from "@/router";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    patients: [],
    patCount: 0,
    isLoading: true,
    error: null,
})

async function loadPatients() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/admin/patients")
        data.value.patCount = response.data.count
        data.value.patients = response.data.patients
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Patients data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredPatients() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/admin/patients/search",
        {  
            params: {
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.patCount = response.data.count
        data.value.patients = response.data.patients
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


// Action Handlers

// Handle Patient Info
const patientToBeSelected = ref(null)
const selectPat = (patient) => {
    patientToBeSelected.value = patient
}

// Handle Patient Edit 
function editPatient(patient){
    globalTemp.set("patient_id", patient.patient_id)
}

// Handle Patient Delete
const patientToBeDeleted = ref(null)
const chooseDeleteDoc = (patient) => {
    patientToBeDeleted.value = patient
}
async function deletePatient() {
    if (!patientToBeDeleted.value) return
    
    try {
        const response = await axios_instance.delete("/api/dashboard/admin/patient", 
          {
            params: {
                "patient_user_id": patientToBeDeleted.value.user_id
            }
          }
        )
        
        // Refresh the patient list
        loadPatients()
        appendAlert(`${patientToBeDeleted.value.full_name}(${patientToBeDeleted.value.patient_public_id}) has been deleted successfully.`,'success',"bi-check-circle")
    } catch (err) {
        appendAlert(`${patientToBeDeleted.value.full_name}(${patientToBeDeleted.value.patient_public_id}) deletion failed.`, "danger", "bi-exclamation-triangle")
    } finally{
        patientToBeDeleted.value = null
    }
}

// Handle Patient block or unblock
async function blockPatient(patient) {
    try {
        const response = await axios_instance.post("/api/dashboard/admin/patient", 
          {
            "patient_user_id": patient.user_id,
            "is_active": !patient.is_active
          }
        )
        if(patient.is_active){
            appendAlert(`${patient.full_name}(${patient.patient_public_id}) has been blocked successfully.`,'success',"bi-check-circle")
        } else{
            appendAlert(`${patient.full_name}(${patient.patient_public_id}) has been unblocked successfully.`,'success',"bi-check-circle")
        }

        patient.is_active = !patient.is_active

    } catch (err) {
        if(patient.is_active){
            appendAlert(`${patient.full_name}(${patient.patient_public_id}) blocking failed.`, "danger", "bi-exclamation-triangle")
        } else{
            appendAlert(`${patient.full_name}(${patient.patient_public_id}) unblocking failed.`, "danger", "bi-exclamation-triangle")
        }
    }
}

// Handle View Patient Medical History 
function viewPatientMedicalHistory(pat_public_id){
    globalTemp.set("patient_public_id", pat_public_id)
    globalTemp.set("from", "patients")
    router.replace("/dashboard/admin/patient-records")
}

onMounted(() => {
    
    if(globalTemp.get('PatientEditStatus') === 'success'){
        appendAlert(`${globalTemp.get('PatientName')} edited successfully!`, "info", "bi-check-circle")
        globalTemp.reset('PatientEditStatus')
        globalTemp.reset('PatientName')
    }

    if(globalTemp.get('searchResource') === 'patient'){
        // console.log("Searching Patient....")
        globalTemp.reset('searchResource')
        loadFilteredPatients()
    }
    else{
        loadPatients()
    }


})

const refreshPatients = () => {
  loadPatients()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                   <h2 class="h4 fw-bold" style="color: #220349;">Patient Management</h2> 
                   
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
                                <th class="text-center">Id</th>
                                <th class="text-center">Patient Info</th>
                                <th class="text-center">Contact number</th>
                                <th class="text-center">Gender</th>
                                <th class="text-center">D.O.B (Y-M-D)</th>
                                <th class="text-center">Block/Unblock</th>
                                <th class="text-center">Actions</th>
                                <th class="text-center">Treatment History</th>
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
                                <td colspan="8" class="py-5 text-center text-primary fw-medium">No patient registered yet.</td>
                            </tr>

                            <tr v-if="!data.isLoading && !data.error" v-for="(patient) in data.patients" :key="patient.patient_id">
                                <td><div class="text-center fw-bold highlight-text">{{ patient.patient_public_id }}</div></td>
                                <td>
                                    <div class="d-flex flex-column">
                                        <div class="text-center fw-bold" style="cursor: pointer;color: #6b27d9;" data-bs-toggle="modal" data-bs-target="#infoDocModal" @click="selectPat(patient)">
                                            {{ patient.full_name }}
                                        </div>
                                        <small class="text-center text-muted fw-semibold">{{ patient.email }}</small>
                                    </div>
                                </td>
                                <td><div class="text-center text-primary fw-semibold">+91 {{ patient.contact }}</div></td>
                                <td><div class="text-center text-success fw-medium">{{ patient.gender }}</div></td>
                                <td><div class="text-center dob-tag fw-medium">{{ patient.dob }}</div></td>
                
                                <td class="text-center">
                                  <button @click="blockPatient(patient)" class="border-0 btn" title="Block/Unblock">
                                    <div class="status-pill" :class="patient.is_active ? 'active' : 'inactive'">
                                        {{ patient.is_active ? "Active" : "Inactive" }}
                                    </div>
                                  </button>
                                </td>
                                <td>
                                    <div class="action-buttons">
                                        <router-link to="/dashboard/admin/edit-patient"><button @click="editPatient(patient)" class="btn-action edit" title="Edit">
                                            <i class="bi bi-pencil-square"></i>
                                        </button></router-link>
                                        <button class="btn-action delete" title="Delete" data-bs-toggle="modal" data-bs-target="#deleteDocModal" @click="chooseDeleteDoc(patient)">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                        <button class="btn-action info" title="Info" data-bs-toggle="modal" data-bs-target="#infoDocModal" @click="selectPat(patient)">
                                            <i class="bi bi-info-circle"></i>
                                        </button>
                                    </div>
                                </td>

                                <td class="text-center">
                                    <button @click="viewPatientMedicalHistory(patient.patient_public_id)" type="button" class="view-treatment-btn px-4 rounded-pill btn" 
                                    title="View Records">
                                        <div>
                                            <i class="bi bi-clipboard-data pe-1"></i>
                                            View Records
                                        </div>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Patient Info Modal -->
            <div class="modal fade" id="infoDocModal" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered"> 
                <div class="modal-content border-1 shadow-lg" v-if="patientToBeSelected">
                    <div class="modal-header">
                        <h5 class="modal-title h5 fw-bold mb-0" style="color: #220349;">{{ patientToBeSelected.full_name }}'s Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                      <div class="modal-body p-3">
                        <div class="row g-2">
                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Patient ID</label>
                                <input :value="patientToBeSelected.patient_public_id" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Email Address</label>
                                <input :value="patientToBeSelected.email" type="text" class="form-control fw-semibold bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">D.O.B (Y-M-D)</label>
                                <input :value="patientToBeSelected.dob" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Phone Number</label>
                                <input :value="'+91 ' + patientToBeSelected.contact" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>
                                  
                            <div class="col-md-4 mb-2">
                                <label class="form-label fw-bold small highlight-text">Gender</label>
                                <input :value="patientToBeSelected.gender" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-4 mb-2">
                                <label class="form-label fw-bold small highlight-text">Height (cm.)</label>
                                <input :value="patientToBeSelected.height_cm" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-4 mb-2">
                                <label class="form-label fw-bold small highlight-text">Weight (kg.)</label>
                                <input :value="patientToBeSelected.weight_kg" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3"  
                                disabled>
                            </div>

                        </div>
                      </div>
                      
                      <div class="modal-footer border-0 d-flex justify-content-center pb-4">
                          <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm close-btn" data-bs-dismiss="modal">Close</button>
                          <router-link to="/dashboard/admin/edit-patient"><button @click="editPatient(patientToBeSelected)" type="button" class="btn px-4 mx-2 rounded-pill shadow-sm edit-btn" data-bs-dismiss="modal">
                              Edit
                          </button></router-link>
                      </div>
                  </div>
              </div>
            </div>

            <!-- Confirm Patient Deletion Modal -->
            <div class="modal fade" id="deleteDocModal" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered modal-sm"> 
                <div class="modal-content border-0 shadow-lg">
                      <div class="modal-body text-center p-3">
                          <div class="delete-icon-wrapper mb-3">
                              <i class="bi bi-exclamation-circle text-danger"></i>
                          </div>
                          
                          <h5 class="fw-bold mb-2">Confirm Delete</h5>
                          <p class="text-muted mb-0">Are you sure you want to delete</p>
                          <p class="fw-bold text-dark" v-if="patientToBeDeleted">{{ patientToBeDeleted.full_name }}?</p>
                          <small class="text-secondary d-block mt-2">This action cannot be undone.</small>
                      </div>
                      
                      <div class="modal-footer border-0 d-flex justify-content-center pb-4">
                          <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm close-btn" data-bs-dismiss="modal">Cancel</button>
                          <button @click="deletePatient" type="button" class="btn px-4 mx-2 rounded-pill shadow-sm delete-btn" data-bs-dismiss="modal">
                              Delete
                          </button>
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

/* Status Pills */
.status-pill {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-pill.active {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #15b98b;
}

.status-pill.inactive {
    background-color: #fef2f2;
    color: #b91c1c;
    border-style: solid;
    border-color: #f06868;
}

.dob-tag {
    background: #f4f1f9;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #475569;
}

/* Action Buttons Styling */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
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

.count-bg{
  background-color: #9e81ec;
}

.highlight-text{
    color: #341079;
    font-weight: 700;
}
.btn-action {
    border: none;
    background: none;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    cursor: pointer;
}

.btn-action.edit { color: #3b82f6; }
.btn-action.edit:hover { background: #eff6ff; }

.btn-action.info { color: #09821b; }
.btn-action.info:hover { background: #ebffef; }

.btn-action.delete { color: #ef4444; }
.btn-action.delete:hover { background: #fef2f2; }

.btn-action i { font-size: 1.1rem; }

.edit-btn {
    background: #a274ec; 
    color: white;
    border: 1px solid rgb(128, 124, 143);
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.edit-btn:hover {
    background: rgb(152, 96, 241);
    border: 1px solid rgb(99, 96, 109);
    color:white;
}

.delete-btn {
    align-items: center;
    background: #cc3d33; 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.delete-btn:hover {
    background: #e63f3f;
    color:white;
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
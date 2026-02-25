<script setup>
import { ref, onMounted} from "vue";
import router from "@/router";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    doctors: [],
    docCount: 0,
    department: null,
    isLoading: true,
    error: null,
})

async function loadAvailableDoctors() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/doctor-list",
        {  
            params: {
                "department": globalTemp.get("department_name")
            }
        })
        data.value.docCount = response.data.count
        data.value.doctors = response.data.doctors
        data.value.department = response.data.department
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.docCount = 0
        appendAlert("Department doctors data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredDoctors() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/doctor-list/search",
        {  
            params: {
                "department": globalTemp.get("department_name"),
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.docCount = response.data.count
        data.value.doctors = response.data.doctors
        data.value.department = response.data.department
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.docCount = 0
        if (err.response?.status === 404){
            appendAlert("Searched doctor(s) not found.", "info", "bi-info-circle")
        }
        else{
            appendAlert("Doctors data loading failed.", "danger", "bi-exclamation-triangle")
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

// Handle Doctor Info
const doctorToBeSelected = ref(null)
const selectDoc = (doctor) => {
    doctorToBeSelected.value = doctor
}

// Handle Doctor Booking
function bookAppointment(doctor){
    globalTemp.set("doctor_public_id", doctor.doctor_public_id)
    globalTemp.set("from", "doctor-list")
    router.replace('/dashboard/patient/book-appointment')
}


onMounted(() => {

    if(globalTemp.get('searchResource') === 'doctors'){
        globalTemp.reset('searchResource')
        loadFilteredDoctors()
    }
    else{
        loadAvailableDoctors()
    }
})

const refreshDoctors = () => {
  loadAvailableDoctors()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">

                    <router-link to="/dashboard/patient/department-list">
                        <button type="button" class="btn btn-sm border-0 text-secondary" title="Back">
                            <i class="bi bi-arrow-left-square fs-4 pe-2"></i>
                        </button>
                    </router-link>

                   <h2 class="h4 fw-bold" style="color: #220349;">{{ data.department }} Doctors</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshDoctors" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                
                <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.docCount }}</span>
            </div>

            <div class="table-container shadow-sm border-1">
                <div class="table-responsive">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Id</th>
                                <th class="text-center">Doctor Name</th>
                                <th class="text-center">Qualification</th>
                                <th class="text-center">Specialization</th>
                                <th class="text-center">Experience</th>
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

                            <tr v-else-if="data.docCount === 0">
                                <td colspan="6" class="py-5 text-center text-primary fw-medium">No doctor in the current department yet.</td>
                            </tr>

                            <tr v-if="!data.isLoading && !data.error" v-for="(doctor) in data.doctors" :key="doctor.doctor_id">
                                <td class="text-center text-muted fw-bold">{{ doctor.doctor_public_id }}</td>
                                <td class="text-center">
                                    <div class="fw-bold" style="cursor: pointer;color: #6b27d9;" data-bs-toggle="modal" data-bs-target="#infoDocModal" @click="selectDoc(doctor)">
                                        {{ doctor.full_name }}
                                    </div>
                                </td>
                                <td><div class="text-center text-success fw-medium">{{ doctor.qualification }}</div></td>
                                <td><div class="text-center spec-tag">{{ doctor.specialization }}</div></td>
                                <td><div class="text-center text-primary fw-medium">{{ doctor.experience }} yrs</div></td>
                                
                                <td class="text-center">
                                    <div class="d-flex justify-content-center gap-2">
                                        <button @click="bookAppointment(doctor)" class="btn px-4 rounded-pill check-btn" title="Check Availability">
                                            <div>
                                                <i class="bi bi-calendar4-week pe-1"></i>
                                                Check Availability
                                            </div>
                                        </button>
                                        <button @click="selectDoc(doctor)" class="btn px-4 rounded-pill view-btn" title="View Details" data-bs-toggle="modal" data-bs-target="#infoDocModal">
                                            <div>
                                                <i class="bi bi-info-circle pe-1 "></i>
                                                View Details
                                            </div>
                                        </button>
                                    </div>
                                </td>

                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Doctor Info Modal -->
            <div class="modal fade" id="infoDocModal" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered modal-lg"> 
                <div class="modal-content border-1 shadow-lg" v-if="doctorToBeSelected">
                    <div class="modal-header">
                        <h5 class="modal-title h5 fw-bold mb-0" style="color: #220349;">{{ doctorToBeSelected.full_name }}'s Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-3">
                    <div class="row g-2">
                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">Doctor ID</label>
                            <input :value="doctorToBeSelected.doctor_public_id" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">Doctor Name</label>
                            <input :value="doctorToBeSelected.full_name" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">License Number</label>
                            <input :value="doctorToBeSelected.license" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3"  
                            disabled>
                        </div>

                        
                        <div class="col-md-6 mb-2">
                            <label class="form-label fw-bold small highlight-text">Department</label>
                            <input :value="doctorToBeSelected.department" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>
                        
                        <div class="col-md-6 mb-2">
                            <label class="form-label fw-bold small highlight-text">Specialization</label>
                            <input :value="doctorToBeSelected.specialization" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">Qualification</label>
                            <input :value="doctorToBeSelected.qualification" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3"  
                            disabled>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">Gender</label>
                            <input :value="doctorToBeSelected.gender" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-bold small highlight-text">Years of Experience</label>
                            <input :value="doctorToBeSelected.experience" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                            disabled>
                        </div>

                        <div class="col-12">
                            <label class="form-label fw-bold small highlight-text">Professional Biography</label>
                            <textarea type="text" rows="3" :value="doctorToBeSelected.description" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3" 
                            disabled></textarea>
                        </div>
                    </div>
                    </div>
                    <div class="modal-footer border-0 d-flex justify-content-center pb-4">
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

.check-btn{
    background:#d0d9ff;
    color: #072175;
    border: 1px solid #2847d3;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
}
.check-btn:hover{
    background:#c6cffa;
    color: #030f55;
    border: 1px solid #0d2a79;
}

.view-btn{
    background:#d8fac8;
    color: #387507;
    border: 1px solid #238817;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
}
.view-btn:hover{
    background:#ccfcb6;
    color: #285503;
    border: 1px solid #13570b;
}

/* Specialization Tag */
.spec-tag {
    background: #f4f1f9;
    padding: 5px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #123567;
}

.count-bg{
  background-color: #9e81ec;
}

.highlight-text{
    color: #341079;
    font-weight: 700;
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
<script setup>
import { ref, onMounted} from "vue";
import router from "@/router";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    doctors: [],
    docCount: 0,
    isLoading: true,
    error: null,
})

async function loadAvailableDoctors() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/doctor-list")
        data.value.docCount = response.data.count
        data.value.doctors = response.data.doctors
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Doctors data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredDoctors() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/admin/doctors/search",
        {  
            params: {
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.docCount = response.data.count
        data.value.doctors = response.data.doctors
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
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
    router.replace('/dashboard/patient/book-appointment')
}


onMounted(() => {

    if(globalTemp.get('PatientBookingStatus') === 'success'){
        appendAlert(`Doctor Appointment on ${globalTemp.get('BookingDate')} from (${globalTemp.get('BookingStartTime')} - ${globalTemp.get('BookingEndTime')}) booked successfully!`, "info", "bi-check-circle")

        globalTemp.reset('PatientBookingStatus')
        globalTemp.reset('BookingDate')
        globalTemp.reset('BookingStartTime')
        globalTemp.reset('BookingEndTime')
    }

    if(globalTemp.get('searchResource') === 'doctor'){
        // console.log("Searching Doctor....")
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
                   <h2 class="h4 fw-bold" style="color: #220349;">Available Doctors</h2> 
                   
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
                                <th>Id</th>
                                <th>Doctor Info</th>
                                <th>Contact number</th>
                                <th>License</th>
                                <th>Specialization</th>
                                <th>Experience</th>
                                <th class="text-center">Consult</th>
                                <th class="text-center">Info</th>
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

                            <tr v-else-if="data.docCount === 0">
                                <td colspan="8" class="py-5 text-center text-primary fw-medium">No doctor registered yet.</td>
                            </tr>

                            <tr v-if="!data.isLoading && !data.error" v-for="(doctor) in data.doctors" :key="doctor.doctor_id">
                                <td class="text-muted fw-bold">{{ doctor.doctor_public_id }}</td>
                                <td>
                                    <div class="d-flex flex-column">
                                        <span class="fw-bold" style="cursor: pointer;color: #6b27d9;" data-bs-toggle="modal" data-bs-target="#infoDocModal" @click="selectDoc(doctor)">
                                            {{ doctor.full_name }}
                                        </span>
                                        <small class="text-muted fw-semibold">{{ doctor.email }}</small>
                                    </div>
                                </td>
                                <td><span class="text-primary fw-semibold">+91 {{ doctor.contact }}</span></td>
                                <td><span class="text-success fw-medium">{{ doctor.license }}</span></td>
                                <td><span class="spec-tag">{{ doctor.specialization }}</span></td>
                                <td><span class="fw-medium">{{ doctor.experience }} yrs</span></td>
                                <td class="text-center">
                                  <button @click="bookAppointment(doctor)" class="border-2 btn-primary btn-ouline-info fw-bold btn rounded-pill" title="Book Appointment">
                                    Book Appointment
                                  </button>
                                </td>
                                <td>
                                    <div class="action-buttons">
                                        <button class="btn-action info" title="Info" data-bs-toggle="modal" data-bs-target="#infoDocModal" @click="selectDoc(doctor)">
                                            <i class="bi bi-info-circle"></i>
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
                            <div class="col-md-2 mb-2">
                                <label class="form-label fw-bold small highlight-text">Doctor ID</label>
                                <input :value="doctorToBeSelected.doctor_public_id" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-4 mb-2">
                                <label class="form-label fw-bold small highlight-text">Phone Number</label>
                                <input :value="'+91 ' + doctorToBeSelected.contact" type="text" class="form-control fw-semibold bg-light" style="border: 1px solid #b59ff3" 
                                disabled>
                            </div>

                            <div class="col-md-6 mb-2">
                                <label class="form-label fw-bold small highlight-text">Email Address</label>
                                <input :value="doctorToBeSelected.email" type="text" class="form-control fw-semibold bg-light fw-semibold" style="border: 1px solid #b59ff3" 
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
                                <label class="form-label fw-bold small highlight-text">License Number</label>
                                <input :value="doctorToBeSelected.license" type="text" class="form-control bg-light fw-semibold" style="border: 1px solid #b59ff3"  
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

/* Specialization Tag */
.spec-tag {
    background: #f4f1f9;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #475569;
}

/* Action Buttons Styling */
.action-buttons {
    display: flex;
    gap: 8px;
    justify-content: center;
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
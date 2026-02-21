<script setup>
import { onMounted} from "vue";
import { ref, computed } from 'vue';
import axios_instance from "@/axiosSetup"
import router from "@/router";
import VueSelect from "vue3-select-component";
import "vue3-select-component/styles";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()
const appointmentDetails = ref(null)
const treatmentDataStatus = ref(null)

const data = ref({
appointment_public_id: '',
visit_type: '',
test_done: '',
diagnosis: '',
prescription: '',
medicine: '',
notes: ''
});

const data_invalid_flag = ref({
visit_type: false,
test_done: false,
diagnosis: false,
prescription: false,
medicine: false,
notes: false
});

function resetInvalidFlags(){
    data_invalid_flag.value = {
        visit_type: false,
        test_done: false,
        diagnosis: false,
        prescription: false,
        medicine: false,
        notes: false
    }
}

const isDataValid = computed(() => {
return (
    data.value.medicine.trim() !== '' &&
    data.value.test_done.trim() !== '' &&
    data.value.diagnosis.trim() !== '' &&
    data.value.prescription.trim() !== '' &&
    data.value.visit_type !== '' &&
    data.value.notes.trim() !== '' &&
    appointmentDetails !== null
)
})

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

const visit_types = ref([
    { label: 'In-Person', value: 'In-Person' },
    { label: 'Online', value: 'Online' }
])

async function loadTreatmentData() {
    try {
        appointmentDetails.value = globalTemp.get("appointment_details")

        const response = await axios_instance.get("/api/dashboard/doctor/treatment-data",{
            params: {
                "appointment_public_id": appointmentDetails?.value.appointment_public_id
            }
          })
        
        treatmentDataStatus.value = response.data?.status

        if (treatmentDataStatus.value === "available"){
            data.value.appointment_public_id = response.data.appointment_public_id
            data.value.visit_type = response.data.visit_type
            data.value.medicine = response.data.medicine
            data.value.test_done = response.data.test_done
            data.value.diagnosis = response.data.diagnosis
            data.value.prescription = response.data.prescription 
            data.value.notes = response.data.notes
        }
        else {
            data.value.appointment_public_id = response.data.appointment_public_id
        }
        

    } catch (err) {
        appendAlert("Treatment data loading failed.", "danger", "bi-exclamation-triangle")
    }
}

onMounted(() => {
    loadTreatmentData()
})

const isProcessing = ref(false)
async function saveChanges(){
    if (isProcessing.value) return

    isProcessing.value = true
    resetInvalidFlags()
    try {
        if (treatmentDataStatus.value === 'unavailable'){
            const response = await axios_instance.post("/api/dashboard/doctor/patient-history", data.value)
        } else{
            const response = await axios_instance.patch("/api/dashboard/doctor/patient-history", data.value)
        }
        
        globalTemp.set('PatientHistoryUpdated', "success")
        globalTemp.set('PatDetails', {
            name: appointmentDetails.value.patient_full_name,
            pub_id: appointmentDetails.value.patient_public_id
        })

        globalTemp.reset("appointment_details")
        router.replace("/dashboard/doctor/appointments")
    } catch(error) {
        let msg = error.response?.data?.message || "Patient History Update failed"
        if(typeof msg === 'object'){
            if(msg?.appointment_public_id){
                msg = msg.appointment_public_id
            }
            if(msg?.medicine){
                msg = msg.medicine
                data_invalid_flag.value.medicine = true
            }
            if(msg?.visit_type){
                msg = msg.visit_type
                data_invalid_flag.value.visit_type = true
            }
            if(msg?.test_done){
                msg = msg.test_done
                data_invalid_flag.value.test_done = true
            }
            if(msg?.diagnosis){
                msg = msg.diagnosis
                data_invalid_flag.value.diagnosis = true
            }
            if(msg?.prescription){
                msg = msg.prescription
                data_invalid_flag.value.prescription = true
            }
            if(msg?.notes){
                msg = msg.notes
                data_invalid_flag.value.notes = true
            }
        }
        
        if(error.response?.status === 400 || error.response?.status === 404){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
        } else{
            appendAlert(msg, "danger", "bi-exclamation-triangle")
        }
        
    } finally {
        isProcessing.value = false
    }
}

</script>

<template>
    <div class="container-fluid">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex align-items-center ">
                <div>
                    <h3 class="h4 fw-bold mb-0" style="color: #220349;">Update Patient History</h3>
                    <p class="text-muted small mb-0">Fill the treatment details to save</p>
                </div>
            </div>
            <div class="card border-0 shadow-sm rounded-4 p-4">
                <div class="col-12">
                    <form @submit.prevent="saveChanges">
                        <div class="row g-2">
                        <div class="col-md-3 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Appointment ID</label>
                            <input :value="appointmentDetails?.appointment_public_id" type="text" class="form-control custom-input" disabled>
                        </div>
                        
                        <div class="col-md-3 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Patient Name</label>
                            <input :value="appointmentDetails?.patient_full_name" type="text" class="form-control custom-input" disabled>
                        </div>
                        <div class="col-md-2 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Gender</label>
                            <input :value="appointmentDetails?.patient_gender" type="text" class="form-control custom-input" disabled>
                        </div>
                        <div class="col-md-2 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Height (cm.)</label>
                            <input :value="appointmentDetails?.patient_height" type="number" class="form-control custom-input" disabled>
                        </div>
                        <div class="col-md-2 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Weight (kg.)</label>
                            <input :value="appointmentDetails?.patient_weight" type="number" class="form-control custom-input" disabled>
                        </div>
                        <div class="col-md-2 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Age</label>
                            <input :value="appointmentDetails?.patient_age" type="number" class="form-control custom-input" disabled>
                        </div>

                        <div class="col-md-3 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Visit Type</label>
                            <VueSelect
                            v-model="data.visit_type"
                            :options="visit_types"
                            placeholder="Select Type" class="custom-select" 
                            :class="{ 'filled': data.visit_type }, {'unfilled': data_invalid_flag.visit_type}" required
                            />
                        </div>

                        <div class="col-md-3 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Tests Done</label>
                            <textarea v-model="data.test_done" type="text" class="form-control custom-input" 
                            :class="{ 'filled': data.test_done.trim() }, {'unfilled': data_invalid_flag.test_done}" placeholder="Please Fill Tests.." required></textarea>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Diagnosis</label>
                            <textarea v-model="data.diagnosis" type="text" class="form-control custom-input" 
                            :class="{ 'filled': data.diagnosis.trim() }, {'unfilled': data_invalid_flag.diagnosis}" placeholder="Please Fill Diagnosis.." required></textarea>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Medicines</label>
                            <textarea v-model="data.medicine" type="text" class="form-control custom-input"
                            :class="{ 'filled': data.medicine.trim() }, {'unfilled': data_invalid_flag.medicine}" rows="3" placeholder="Please Fill Medicines.." required></textarea>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Prescription</label>
                            <textarea v-model="data.prescription" type="text" class="form-control custom-input" 
                            :class="{ 'filled': data.prescription.trim() }, {'unfilled': data_invalid_flag.prescription}" rows="3" placeholder="Please Fill Prescription.." required></textarea>
                        </div>

                        <div class="col-md-4 mb-2">
                            <label class="form-label fw-semibold small highlight-text">Notes</label>
                            <textarea type="text" v-model="data.notes" class="form-control custom-input" 
                            :class="{ 'filled': data.notes.trim() }, {'unfilled': data_invalid_flag.notes}" rows="3" placeholder="Briefly describe the things patient has to follow.." required></textarea>
                        </div>

                        <div class="col-12 mt-4 d-flex justify-content-end gap-2 ">
                            <router-link to="/dashboard/doctor/appointments"><button type="button" class="btn px-4 rounded-pill back-btn">
                                Back
                            </button></router-link>
                            <button type="submit" class="btn px-4 text-white rounded-pill shadow-sm submit-btn" v-if="isProcessing" :disabled="isProcessing" id="clicked">
                                <span>Saving...</span>
                            </button>
                            <button type="submit" class="btn px-4 text-white rounded-pill shadow-sm submit-btn" v-else :disabled="!isDataValid">
                                <span>Save</span>
                            </button>
                        </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.custom-input {
    background-color: #f3f6fa;
    border: 1px solid #cee3fc;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    transition: all 0.2s ease;
}
.custom-input:disabled{
    background-color: #f8fcfb;
    border: 1px solid #bdd5f1;
    padding: 0.75rem 1rem;
    border-radius: 12px;
    transition: all 0.2s ease;
}

.custom-input.filled{
    border: 1px solid green;
    background-color: #f7f9fc;
}
.custom-input.unfilled{
    border: 1px solid red;
    background-color: #f6f8fc;
}
.custom-input:focus {
  background-color: #fff;
  border-color: #635bff;
  box-shadow: 0 0 0 4px rgba(99, 91, 255, 0.1);
}

.card {
  transition: transform 0.2s ease;
}
.highlight-text{
    color: #341079;
    font-weight: 700;
}

.custom-select {
  --vs-outline-width: 1px solid;
  --vs-outline-color: #635bff;
  --vs-min-height: 50px;
  --vs-background-color: #f3f6fa;
  --vs-border-radius: 12px;
  --vs-border: 1px solid #d3e5fa;
  --vs-text-color: #12233b;
  --vs-option-focused-background-color: #eee5fd;
  --vs-option-selected-background-color: #af9cf3;
  --vs-option-selected-text-color: white;
  --vs-option-disabled-background-color: #eeeef7;
  --vs-menu-offset-top: 2px;
  --vs-menu-border: 1px solid #7771ee;
}
.custom-select.filled{
    --vs-background-color: #f7f9fc;
    --vs-border: 1px solid green;
}
.custom-select.unfilled{
    --vs-background-color: #f7f9fc;
    --vs-border: 1px solid red;
}

.submit-btn {
    align-items: center;
    background: linear-gradient(135deg,#7652b4, #4b2c89, #3b1e79); 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.submit-btn:hover {
    background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
    color:white;
}
#clicked {
    background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
    color:white;
    cursor:not-allowed;
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
    color: rgb(23, 2, 2);
    border: 1px solid rgb(116, 115, 115);
}
</style>
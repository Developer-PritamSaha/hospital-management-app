<script setup>
import { onMounted} from "vue";
import { ref, computed } from 'vue';
import axios_instance from "@/axiosSetup"
import router from "@/router";
import VueSelect from "vue3-select-component";
import "vue3-select-component/styles";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()
const currentPatientData = ref(null)

const data = ref({
patient_public_id: '',
full_name: '',
gender: '',
dob: '',
height_cm: '',
weight_kg: '',
contact: ''
});

const data_invalid_flag = ref({
full_name: false,
gender: false,
dob: false,
height_cm: false,
contact: false,
weight_kg: false
});

function resetInvalidFlags(){
    data_invalid_flag.value = {
        full_name: false,
        gender: false,
        dob: false,
        height_cm: false,
        contact: false,
        weight_kg: false
    }
}

const isDataValid = computed(() => {
return (
    data.value.full_name.trim() !== '' &&
    data.value.contact.trim() !== '' &&
    data.value.dob.trim() !== '' &&
    data.value.height_cm !== '' &&
    data.value.gender !== '' &&
    data.value.weight_kg !== '' &&
    currentPatientData !== null
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

const genders = ref([
    { label: 'Male', value: 'male' },
    { label: 'Female', value: 'female' },
    { label: 'Trans', value: 'trans' }
])

async function loadPatientDetails() {
    try {
        const response = await axios_instance.get("/api/dashboard/patient")
        currentPatientData.value = response.data

        data.value.patient_public_id = response.data.patient_public_id
        data.value.full_name = response.data.full_name
        data.value.contact = response.data.contact
        data.value.dob = response.data.dob
        data.value.height_cm = response.data.height_cm
        data.value.gender = response.data.gender
        data.value.weight_kg = response.data.weight_kg

    } catch (err) {
        appendAlert("Profile data loading failed.", "danger", "bi-exclamation-triangle")
    }
}

onMounted(() => {
    loadPatientDetails()
})


const isProcessing = ref(false)
async function saveChanges(){
    if (isProcessing.value) return

    isProcessing.value = true
    resetInvalidFlags()
    try {
        const response = await axios_instance.patch("/api/dashboard/patient", data.value)
        appendAlert("Profile updated successfully!", "info", "bi-check-circle")
    } catch(error) {
        let msg = error.response?.data?.message || "Profile Update failed."
        if(typeof msg === 'object'){
            if(msg?.patient_public_id){
                msg = "Patient_id " + msg.patient_public_id
            }
            if(msg?.full_name){
                msg = msg.full_name
                data_invalid_flag.value.full_name = true
            }
            if(msg?.contact){
                msg = "In Phone number " + msg.contact.toLowerCase()
                data_invalid_flag.value.contact = true
            }
            if(msg?.gender){
                msg = msg.gender
                data_invalid_flag.value.gender = true
            }
            if(msg?.dob){
                msg = msg.dob
                data_invalid_flag.value.dob = true
            }
            if(msg?.height_cm){
                msg = msg.height_cm
                data_invalid_flag.value.height_cm = true
            }
            if(msg?.weight_kg){
                msg = msg.weight_kg
                data_invalid_flag.value.weight_kg = true
            }
        }
        
        if(error.response?.status === 400 || error.response?.status === 404){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
        } else{
            console.log(error.response?.data)
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
                    <h3 class="h4 fw-bold mb-0" style="color: #220349;">Profile</h3>
                    <p class="text-muted small mb-0">Edit details to save</p>
                </div>
            </div>
            <div class="card border-0 shadow-sm rounded-4 p-4">
                <div class="col-12">
                    <form @submit.prevent="saveChanges">
                        <div class="row g-2">
                            <div class="col-md-12 mb-2 d-flex align-items-end justify-content-center">
                                <img src="@/assets/favicon/icons8-patient.png" alt="Patient" class="img-fluid rounded border shadow-sm" style="max-height: 100px;">
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Patient ID</label>
                                <input :value="currentPatientData?.patient_public_id" type="text" class="form-control custom-input" disabled>
                            </div>
                            
                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Full Name</label>
                                <input v-model="data.full_name" type="text" class="form-control custom-input" 
                                :class="{ 'filled': data.full_name.trim() }, {'unfilled': data_invalid_flag.full_name}"" placeholder="Please Fill Full Name" required>
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Email Address</label>
                                <input :value="currentPatientData?.email" type="text" class="form-control custom-input" disabled>
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Phone Number</label>
                                <input v-model="data.contact" type="tel" class="form-control custom-input"
                                :class="{ 'filled': data.contact.trim() }, {'unfilled': data_invalid_flag.contact}" placeholder="Please Fill Phone Number" required>
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">D.O.B (Y-M-D)</label>
                                <input type="text" class="form-control form-control-lg fs-6 custom-input" 
                                :class="{ 'filled': data.dob.trim() }, {'unfilled': data_invalid_flag.dob}" placeholder="Please Fill D.O.B" onfocus="this.type='date'" onblur="this.type='text'" v-model="data.dob" required></input>
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Gender</label>
                                <VueSelect
                                v-model="data.gender"
                                :options="genders"
                                placeholder="Select Gender" class="custom-select" 
                                :class="{ 'filled': data.gender }, {'unfilled': data_invalid_flag.gender}" required
                                />
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Height (cm.)</label>
                                <input v-model="data.height_cm" type="number" class="form-control custom-input" 
                                :class="{ 'filled': data.height_cm }, {'unfilled': data_invalid_flag.height_cm}" placeholder="Please Fill Height" required>
                            </div>

                            <div class="col-md-3 mb-2">
                                <label class="form-label fw-semibold small highlight-text">Weight (kg.)</label>
                                <input v-model="data.weight_kg" type="number" class="form-control custom-input" 
                                :class="{ 'filled': data.weight_kg }, {'unfilled': data_invalid_flag.weight_kg}" placeholder="Please Fill Weight" required>
                            </div>

                            <div class="col-12 mt-4 d-flex justify-content-center">
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
</style>
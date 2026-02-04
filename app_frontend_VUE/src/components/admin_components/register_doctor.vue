<script setup>
import { onMounted} from "vue";
import { ref, computed } from 'vue';
import axios_instance from "@/axiosSetup";
import router from "@/router";
import VueSelect from "vue3-select-component";
import "vue3-select-component/styles";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
full_name: '',
email: '',
password: '',
gender: '',
license: '',
specialization_id: '',
department_id: '',
experience: '',
contact: '',
description: ''
});

const data_invalid_flag = ref({
full_name: false,
email: false,
password: false,
gender: false,
license: false,
specialization_id: false,
department_id: false,
experience: false,
contact: false,
description: false
});

const confirm_password = ref("")
const passwordMismatch = computed(() => {
return (
    confirm_password.value !== "" &&
    data.value.password !== confirm_password.value
)
})
const passwordMatch = computed(() => {
return (
    confirm_password.value !== "" &&
    data.value.password === confirm_password.value
)
})

function resetInvalidFlags(){
    data_invalid_flag.value = {
        full_name: false,
        email: false,
        password: false,
        gender: false,
        license: false,
        specialization_id: false,
        department_id: false,
        experience: false,
        contact: false,
        description: false
    }
}

const isDataValid = computed(() => {
return (
    data.value.full_name.trim() !== '' &&
    data.value.email.trim() !== '' &&
    data.value.password.trim() !== '' &&
    confirm_password.value !== '' &&
    data.value.password === confirm_password.value &&
    data.value.contact.trim() !== '' &&
    data.value.license.trim() !== '' &&
    data.value.department_id !== '' &&
    data.value.specialization_id !== '' &&
    data.value.experience !== '' &&
    data.value.gender !== '' &&
    data.value.description.trim() !== ''
)
})

function clearData(){
    resetInvalidFlags()
    confirm_password.value = ''
    data.value.full_name = '' 
    data.value.email = ''
    data.value.password = ''
    data.value.contact = ''
    data.value.license = ''
    data.value.department_id = ''
    data.value.specialization_id = '' 
    data.value.experience = ''
    data.value.gender = ''
    data.value.description = ''
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

const existingData = ref({
    departments: [],
    deptCount: 0,
    specializations: [],
    specCount: 0,
})

const departments = ref([])
const specializations = ref([])
const genders = ref([
    { label: 'Male', value: 'male' },
    { label: 'Female', value: 'female' },
    { label: 'Trans', value: 'trans' }
])

async function loadDepartments() {
    try {
        const response = await axios_instance.get("/api/dashboard/admin/departments")
        existingData.value.deptCount = response.data.count
        existingData.value.departments = response.data.departments
        for (const dept of existingData.value.departments) {
            departments.value.push({label:dept.name, value:dept.id})
        }

    } catch (err) {
        appendAlert("Departments loading failed.", "danger", "bi-exclamation-triangle")
    }
}

async function loadSpecializations() {
    try {
        const response = await axios_instance.get("/api/dashboard/admin/specializations")
        existingData.value.specCount = response.data.count
        existingData.value.specializations = response.data.specializations
        for (const spec of existingData.value.specializations) {
            specializations.value.push({label:spec.name, value:spec.id})
        }

    } catch (err) {
        appendAlert("Specializations loading failed.", "danger", "bi-exclamation-triangle")
    }
}

onMounted(() => {
    loadDepartments()
    loadSpecializations()
})


const isProcessing = ref(false)
async function register_doc(){
    if (isProcessing.value) return

    isProcessing.value = true
    resetInvalidFlags()
    try {
        const response = await axios_instance.post("/api/register/doctor", data.value)
        globalTemp.set('DoctorRegStatus', "success")
        router.replace("/dashboard/admin/doctors")
    } catch(error) {
        let msg = error.response?.data?.message || "Doctor registration failed."
        if(typeof msg === 'object'){
            if(msg?.full_name){
                msg = msg.full_name
                // data.value.full_name = ''
                data_invalid_flag.value.full_name = true
            }
            if(msg?.email){
                msg = "In Email Address " + msg.email.toLowerCase()
                // data.value.email = ''
                data_invalid_flag.value.email = true
            }
            if(msg?.password){
                msg = msg.password
                data.value.password = ''
                confirm_password.value = ''
                data_invalid_flag.value.password = true
            }
            if(msg?.contact){
                msg = "In Phone number " + msg.contact.toLowerCase()
                // data.value.contact = ''
                data_invalid_flag.value.contact = true
            }
            if(msg?.gender){
                msg = msg.gender
                // data.value.gender = ''
                data_invalid_flag.value.gender = true
            }
            if(msg?.license){
                msg = msg.license
                // data.value.license = ''
                data_invalid_flag.value.license = true
            }
            if(msg?.department_id){
                msg = msg.department_id
                // data.value.department_id = ''
                data_invalid_flag.value.department_id = true
            }
            if(msg?.specialization_id){
                msg = msg.specialization_id
                // data.value.specialization_id = ''
                data_invalid_flag.value.specialization_id = true
            }
            if(msg?.experience){
                msg = msg.experience
                // data.value.experience = ''
                data_invalid_flag.value.experience = true
            }
            if(msg?.description){
                msg = msg.description
                // data.value.description = ''
                data_invalid_flag.value.description = true
            }
        }
        
        if(error.response?.status === 400 || error.response?.status === 404 || error.response?.status === 409){
            appendAlert(msg, "warning", "bi-exclamation-octagon")
        } else{
            // console.log(error.response?.data)
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
                        <h3 class="h4 fw-bold mb-0" style="color: #220349;">Doctor Registration</h3>
                        <p class="text-muted small mb-0">Fill the doctor's details to register or signup</p>
                    </div>
                </div>
                <div class="card border-0 shadow-sm rounded-4 p-4">
            <div class="col-12">
                <!-- <p>{{ data_invalid_flag }}</p> -->
                <form @submit.prevent="register_doc">
                    <div class="row g-2">
                    <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Full Name</label>
                        <input v-model="data.full_name" type="text" class="form-control custom-input" 
                        :class="{ 'filled': data.full_name.trim() }, {'unfilled': data_invalid_flag.full_name}"" placeholder="e.g. Dr Surya Das" required>
                    </div>

                    <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Email Address</label>
                        <input v-model="data.email" type="email" class="form-control custom-input" 
                        :class="{ 'filled': data.email.trim() }, {'unfilled': data_invalid_flag.email}" placeholder="e.g. name@example.com" required>
                    </div>

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Create Password</label>
                        <input v-model="data.password" type="password" class="form-control custom-input" 
                        :class="{ 'filled' : data.password.trim() }, {'unfilled': data_invalid_flag.password}"  placeholder="e.g. pAss#3489" required>
                    </div>

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Confirm Password</label>
                        <input v-model="confirm_password" type="text" class="form-control custom-input" 
                        :class="{ 'filled' : passwordMatch }, { 'unfilled' : passwordMismatch }, {'unfilled': data_invalid_flag.password}"  placeholder="e.g. pAss#3489" required>
                         <small v-if="passwordMismatch" class="text-danger">
                            Passwords do not match
                        </small>
                    </div>

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Phone Number</label>
                        <input v-model="data.contact" type="tel" class="form-control custom-input"
                        :class="{ 'filled': data.contact.trim() }, {'unfilled': data_invalid_flag.contact}" placeholder="e.g. +91 9XXXXXXXXX" required>
                    </div>
                    
                    <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Department</label>
                        <VueSelect
                        v-model="data.department_id"
                        :options="departments"
                        placeholder="Select Department" class="custom-select" 
                        :class="{ 'filled': data.department_id }, {'unfilled': data_invalid_flag.department_id}" required
                        />
                    </div>
                    
                    <div class="col-md-6 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Specialization</label>
                        <VueSelect
                        v-model="data.specialization_id"
                        :options="specializations"
                        placeholder="Select Specialization" class="custom-select" 
                        :class="{ 'filled': data.specialization_id }, {'unfilled': data_invalid_flag.specialization_id}" required
                        />
                    </div>

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">License Number</label>
                        <input v-model="data.license" type="text" class="form-control custom-input" 
                        :class="{ 'filled': data.license.trim() }, {'unfilled': data_invalid_flag.license}" placeholder="e.g. DOC-123456" required>
                    </div>

                    <!-- <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Gender</label>
                        <select class="form-select custom-input" 
                        :class="{ 'filled': data.gender.trim() }, {'unfilled': data_invalid_flag.gender}" v-model="data.gender" required>
                            <option value="" disabled selected hidden>Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="trans">Trans</option>
                        </select>
                    </div> -->

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Gender</label>
                        <VueSelect
                        v-model="data.gender"
                        :options="genders"
                        placeholder="Select Gender" class="custom-select" 
                        :class="{ 'filled': data.gender }, {'unfilled': data_invalid_flag.gender}" required
                        />
                    </div>

                    <div class="col-md-4 mb-2">
                        <label class="form-label fw-semibold small highlight-text">Years of Experience</label>
                        <input v-model="data.experience" type="number" class="form-control custom-input" 
                        :class="{ 'filled': data.experience }, {'unfilled': data_invalid_flag.experience}" placeholder="e.g. 20" required>
                    </div>

                    <div class="col-12">
                        <label class="form-label fw-semibold small highlight-text">Professional Biography</label>
                        <textarea type="text" v-model="data.description" class="form-control custom-input" 
                         :class="{ 'filled': data.description.trim() }, {'unfilled': data_invalid_flag.description}" rows="3" placeholder="Briefly describe the doctor's background..." required></textarea>
                    </div>

                    <div class="col-12 mt-4 d-flex justify-content-end gap-2 ">
                        <button type="button" class="btn px-4 rounded-pill clear-btn" @click="clearData">Clear</button>
                        <button type="submit" class="btn px-4 text-white rounded-pill shadow-sm submit-btn" v-if="isProcessing" :disabled="isProcessing" id="clicked">
                            <span>Registering...</span>
                        </button>
                        <button type="submit" class="btn px-4 text-white rounded-pill shadow-sm submit-btn" v-else :disabled="!isDataValid">
                            <span>Register Doctor</span>
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
    border: 1px solid #d3e5fa;
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
    border: 1px solid rgb(116, 115, 115);
}
</style>
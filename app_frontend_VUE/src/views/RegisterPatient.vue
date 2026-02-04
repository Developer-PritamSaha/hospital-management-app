<script setup>
    import { onMounted, onUnmounted } from "vue";
    import {ref, computed} from "vue";
    import axios_instance from "@/axiosSetup";
    import router from "@/router";
    

    const getAuthTokens = () => {
      const authTokens = localStorage.getItem('tokens')
      return authTokens ? JSON.parse(authTokens) : null
    }

    async function PingUserToken() {
        try {
            const response = await axios_instance.get("/api/token/user/role-valid")
            if(response?.data['role'] === 'admin'){
            router.replace("/dashboard/admin")
            } 
            if (response?.data['role'] === 'doctor'){
            router.replace("/dashboard/doctor")
            } 
            if (response?.data['role'] === 'patient'){
            router.replace("/dashboard/patient")
            } 

        } catch (error) {
            if(error.response?.status === 401){
            router.replace('/login')
            } else{
            router.replace('/')
            }
            // console.log(error.response?.data)
        }
    }

    onMounted(() => {
        if(getAuthTokens()){
            PingUserToken()
        } else{
            router.replace('/register/patient')
        }
        document.body.style.fontFamily = "Montserrat', Arial, Helvetica, sans-serif"
        document.body.style.height = "100%"
        document.body.style.direction = "column"
        document.body.style.backgroundAttachment = "fixed"
        document.body.style.backgroundImage = "radial-gradient(circle, #bacaf0, #b5c3f0, #b1bcef, #aeb5ee, #adadec, #a19de0, #968cd4, #8c7cc7, #755fad, #5e4494, #49287b, #330962)"
    })

    onUnmounted(() => {
        document.body.style.fontFamily = ""
        document.body.style.height = ""
        document.body.style.direction = ""
        document.body.style.backgroundAttachment = ""
        document.body.style.backgroundImage = ""
    })

    const data = ref({
        email: '',
        password: '',
        full_name: '',
        contact: '',
        dob: '',
        gender: '',
        height_cm: '',
        weight_kg: ''
    })

    const data_invalid_flag = ref({
        full_name: false,
        email: false,
        password: false,
        contact: false,
        gender: false,
        dob: false,
        height_cm: false,
        weight_kg: false
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
            contact: false,
            gender: false,
            dob: false,
            height_cm: false,
            weight_kg: false
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
        data.value.dob.trim() !== '' &&
        data.value.gender.trim() !== '' &&
        data.value.height_cm !== '' &&
        data.value.weight_kg !== ''
    )
    })
    
    const alertPlaceholder = ref(null)
    function appendAlert(message, type, icon) {
        if (!alertPlaceholder.value) return

        alertPlaceholder.value.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show text-center" role="alert">
                <i class="bi ${icon} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `
        // disappear after 5 seconds
        setTimeout(() => {
            if (alertPlaceholder.value) {
            alertPlaceholder.value.innerHTML = ''
            }
        }, 5000)
    }
    
    const isProcessing = ref(false)
    async function register(){
        if (isProcessing.value) return
        isProcessing.value = true
        resetInvalidFlags()
        try {
            const response = await axios_instance.post("/api/register/patient", data.value)
            appendAlert("Registration Successful!", "success", "bi-check-circle-fill")
            router.replace("/login")
        } catch(error) {
            let msg = error.response?.data?.message || "Registration failed"
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
                    msg = msg.contact
                    // data.value.contact = ''
                    data_invalid_flag.value.contact = true
                }
                if(msg?.gender){
                    msg = msg.gender
                    // data.value.gender = ''
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
            
            if(error.response?.status === 400 || error.response?.status === 409){
                appendAlert(msg, "warning", "bi-exclamation-octagon")
            } else{
                appendAlert(msg, "danger", "bi-exclamation-triangle")
            }
            // console.log(error.response?.data)
        } finally {
            isProcessing.value = false
        }
    }
</script>

<template>
    <!-- Main Container -->
     <div class="login-reg-page container d-flex justify-content-center align-items-center min-vh-100">

        <!-- Register Container -->
        <div class="row border border-top-0 rounded-5 shadow-lg p-3 border-secondary panel-area">

            <!-- Left panel -->
             <div class="col-md-6 rounded-4 d-flex justify-content-center align-items-center flex-column left-panel">
                <div class="featured-image mb-2 p-2">
                   <img src="../assets/images/undraw_donut-love_5r3x.svg" class="img-fluid mt-5" style="width: 550px">                 
                </div>
                <router-link to="/" class="navbar-brand d-flex align-items-center brand-logo">
                    <p class="fw-bold fs-2 mt-5"><img src="../assets/favicon/icons8-health-96.png" alt="HMS-App-Logo" width="40" height="40" class="d-inline-block align-text-bottom">
                    PentaFlow</p>
                </router-link>
        
                <small class="mb-5 fs-6 text-white text-center">Your health, Our care, Anytime.</small>
             </div>

             <!-- Right panel -->
             <form @submit.prevent="register" class="col-md-6 rounded-4 d-flex justify-content-center align-items-center p-5 right-panel">
               <div class="row allign-items-center">
                  <div class="header-text mb-3">
                     <h4 class="text">Join Us</h4>
                     <p class="text-secondary">Sign up now for easy doctor appointments</p>
                  </div>
                  <div class="input-group mb-2">
                     <input type="text" class="form-control form-control-lg fs-6 custom-input" 
                        :class="{ 'filled': data.full_name.trim() }, {'unfilled': data_invalid_flag.full_name}" placeholder="Full Name" v-model="data.full_name" required>
                  </div>
                  <div class="input-group mb-2">
                     <input type="email" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.email.trim() }, {'unfilled': data_invalid_flag.email}" placeholder="Email Address" v-model="data.email" required>
                  </div>

                  <div class="input-group mb-1">
                    <small v-if="passwordMismatch" class="text-danger">
                        Passwords do not match
                    </small>
                  </div>
                  <div class="input-group mb-2">
                    <input type="password" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.password.trim() }, {'unfilled': data_invalid_flag.password}" placeholder="Create Password" v-model="data.password" required>

                    <input v-model="confirm_password" type="text" class="form-control form-control-lg fs-6 custom-input" 
                    :class="{ 'filled' : passwordMatch }, { 'unfilled' : passwordMismatch }, {'unfilled': data_invalid_flag.password}"  placeholder="Confirm Password" required>
                  </div>

                  <div class="input-group mb-2">
                    <span class="input-group-text custom-input" :class="{ 'filled': data.contact.trim() }, {'unfilled': data_invalid_flag.contact}">+91</span>
                    <input type="tel" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.contact.trim() }, {'unfilled': data_invalid_flag.contact}" placeholder="Contact No." v-model="data.contact" required>
                  </div>
                  
                  <div class="input-group mb-2">
                     <input type="text" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.dob.trim() }, {'unfilled': data_invalid_flag.dob}" placeholder="D.O.B (Y-M-D)" onfocus="this.type='date'" onblur="this.type='text'" v-model="data.dob" required></input>

                     <select class="form-select fs-6 custom-input" 
                         :class="{ 'filled': data.gender.trim() }, {'unfilled': data_invalid_flag.gender}" 
                         v-model="data.gender" required>
                        <option value="" disabled selected hidden >Gender</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="trans">Trans</option>
                    </select>
                  </div>
                  <div class="input-group mb-4">
                     <input type="number" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.height_cm }, {'unfilled': data_invalid_flag.height_cm}" placeholder="Height (cm)" v-model="data.height_cm" required>
                     <input type="number" class="form-control form-control-lg fs-6 custom-input" 
                         :class="{ 'filled': data.weight_kg }, {'unfilled': data_invalid_flag.weight_kg}" placeholder="Weight (kg)" v-model="data.weight_kg" required>
                  </div>
               
                <button type="submit" class="btn text-white" v-if="isProcessing" :disabled="isProcessing" id="clicked">
                    <span>Registering...</span>
                </button>
                <button type="submit" class="btn text-white" v-else :disabled="!isDataValid">
                    <span>Register</span>
                </button>

                <div class="registered-user">
                    <p>Already signed up? <router-link to="/login" class="login-link">Login</router-link></p>
                </div>

                <div ref="alertPlaceholder"></div>

               </div>
            </form>
        </div>
     </div>
</template>

<style scoped>
    @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap');

    .brand-logo{
        color: #190953;
    }
    .brand-logo:hover{
        color: #1c023f;
        cursor: pointer;
    }
    .panel-area{
        width: 1100px;
        /* background: #250b42; */
        /* background: #755fad; */
        background: white;
    }

    .left-panel{
        /* background: rgb(162, 184, 233); */
        background: #a996d8;
        /* background: #310f59; */
        font-family: 'Lato', 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
    }


    .right-panel button {
        display: block; 
        margin: 0 auto;
        width: 80%;
        padding: 10px;
        align-items: center;
        background: linear-gradient(135deg,#7652b4, #4b2c89, #3b1e79); 
        color: white;
        border: gray;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
    }
    .right-panel button:hover {
        background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
        color:white;
    }

    .custom-input {
        background-color: #f3f6fa;
        border: 1px solid #d1e5fc;
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

    #clicked {
        background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
        color:white;
        cursor:not-allowed;
    }

    .registered-user {
        margin-top: 1rem;
        font-weight: 640;
        text-align: center;
        cursor: pointer;
    }
    .login-link{
      font-weight: 660;
      color: #8151da;
      text-decoration: none;
    }
    .login-link:hover {
        text-decoration: underline;
        color: #5905ae;
    }

    ::placeholder{
        font-size: 15px;
    }

@media only screen and (max-width: 720px){
    .featured-image{
        display: none;
    }
    .panel-area{
        margin: 0 10px;
    }
    .left-panel{
        height: 120px;
        overflow: hidden;
    }
    .right-panel{
        padding: 20px;
    }
}
</style>
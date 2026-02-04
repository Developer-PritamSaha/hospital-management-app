<script setup>
    import { onMounted, onUnmounted } from "vue";
    import {ref} from "vue";
    import axios_instance from "@/axiosSetup";
    import router from "@/router";
    import { useGlobalTemp } from '@/stores/temp_data';

    const globalTemp = useGlobalTemp()
    
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
            router.replace('/login')
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
        rememberMe: ''
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
    async function login(){
        if (isProcessing.value) return
        isProcessing.value = true
        try {
            const response = await axios_instance.post("/api/login", data.value)
            localStorage.setItem("tokens", JSON.stringify(response.data))
            globalTemp.set('LoginStatus', 'success')
            router.push("/")
        } catch(error) {
            let msg = error.response?.data?.message || "Login failed"
            if(msg?.email){
                msg = "In Email " + msg.email.toLowerCase()
            }
            if(msg?.password){
                msg = msg.password
            }
            if(error.response?.status === 400 || error.response?.status === 404){
                appendAlert(msg, "warning", "bi-exclamation-octagon")
            }else{
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

        <!-- Login Container -->
        <div class="row border border-top-0 rounded-5 shadow-lg p-3 border-secondary panel-area">
            
            <!-- Left panel -->
             <div class="col-md-6 rounded-4 d-flex justify-content-center align-items-center flex-column left-panel">
                <div class="featured-image p-2">
                   <img src="../assets/images/undraw_true-love_rap5.svg" class="img-fluid mt-5 mb-2" style="width: 550px">                 
                </div>
                <router-link to="/" class="navbar-brand d-flex align-items-center mt-4 fs-2 fw-bold brand-logo">
                    <p class=" fw-bold fs-2 mt-2"><img src="../assets/favicon/icons8-health-96.png" alt="HMS-App-Logo" width="40" height="40" class="d-inline-block align-text-bottom ">
                    PentaFlow</p>
                </router-link>
                
                <small class="mb-5 fs-6 text-white text-center">Your health, Our care, Anytime.</small>
             </div>

             <!-- Right panel -->
            <form  @submit.prevent="login" class="col-md-6 rounded-4 d-flex justify-content-center align-items-center p-5 right-panel">
                <div class="row allign-items-center">
                    <div class="header-text mb-4">
                        <h4 class="text">Welcome Back</h4>
                        <p class="text-secondary">We're glad to see you again.</p>
                    </div>
                    <div class="input-group mb-3">
                        <input type="email" autocomplete="username" class="form-control form-control-lg fs-6 custom-input" placeholder="Email" v-model="data.email" required>
                    </div>
                    <div class="input-group mb-1">
                        <input type="password" autocomplete="current-password" class="form-control form-control-lg fs-6 custom-input" placeholder="Password" v-model="data.password" required>
                    </div>
                    <div class="input-group my-2 mb-5 d-flex justify-content-between">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="remember" id="rememberMeCheck" v-model="data.rememberMe">
                            <label class="form-check-label text-secondary" for="rememberMeCheck">
                            <small>Remember me</small>
                            </label>
                        </div>
                        <div>
                            <small><router-link to="#" class="forget-password">Forget Password</router-link></small>
                        </div>
                    </div>

                    <button type="submit" v-if="isProcessing" :disabled="isProcessing" id="clicked">
                        <span>Logging in...</span>
                    </button>
                    <button type="submit" v-else>
                        <span>Login</span>
                    </button>

                    <div class="new-user">
                        <p>New User? <router-link to="/register/patient" class="reg-link">SignUp</router-link></p>
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
      width: 930px;
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
   .custom-input {
        background-color: #f3f6fa;
        border: 1px solid #d1e5fc;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        transition: all 0.2s ease;
    }
    .custom-input:focus {
        background-color: #fff;
        border-color: #635bff;
        box-shadow: 0 0 0 4px rgba(99, 91, 255, 0.1);
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
  #clicked{
    background: linear-gradient(135deg,#743fe6, #9b78e2, #ab8ce0);
    color:white;
    cursor:not-allowed;
  }
  .forget-password {
      font-weight: 500;
      color: #6C63FF;
      text-decoration: none;
      cursor: pointer
  }
  .forget-password:hover {
      text-decoration: underline;
      color: #3d0475;
  }

  .new-user {
      margin-top: 1rem;
      font-weight: 640;
      text-align: center;
      cursor: pointer;
  }
  .reg-link{
      font-weight: 660;
      color: #8151da;
      text-decoration: none;
  }
  .reg-link:hover {
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
          overflow:hidden;
      }
      .right-panel{
          padding: 20px;
      }
      .forget-password{
        font-size: small;
      }
  }   
</style>
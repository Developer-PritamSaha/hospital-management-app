<script setup>
  import {onMounted} from "vue";
  import router from "@/router";
  import axios_instance from "@/axiosSetup";

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
        else if (response?.data['role'] === 'doctor'){
          router.replace("/dashboard/doctor")
        } 
        else if (response?.data['role'] === 'patient'){
          router.replace("/dashboard/patient")
        } 
        else{
          router.replace('/login')
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
      router.replace('/')
    }
  })

  function refresh_page(){
    window.location.reload()
  }

</script>

<template>
    <!-- Navigation Bar -->
    <nav class="navbar sticky-top navbar-expand-lg navbar-light bg-light shadow-sm">
        <div class="container d-flex align-items-center">
            <a to='#' @click="refresh_page" class="navbar-brand d-flex align-items-center fs-2 fw-bold brand-logo">
                <img src="../assets/favicon/icons8-health-96.png" alt="PentaFlow-Logo" width="50" height="50" class="d-inline-block  align-text-bottom"> <h3 class="mb-0 ps-1 fw-bold sidebar-text">PentaFlow</h3>
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
              <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarSupportedContent">
              <ul class="navbar-nav ms-auto">
                <li class="nav-item">
                  <router-link to="/login" class="nav-link fs-5" id="nav-login">Login</router-link>
                </li>
                <li class="nav-item">
                  <router-link to="/register/patient" class="nav-link fs-5" id="nav-register">SignUp</router-link>
                </li>
              </ul>
            </div>
          </div>
    </nav>

    <!-- Hero Section -->
    <header class="hero-section py-5 text-center">
        <div class="container py-5">
            <h1 class="display-3 fw-bold mb-3">Healthcare, Simplified for You</h1>
            <p class="fs-5 mb-4 col-lg-8 mx-auto">PentaFlow helps you find the right care, book appointments, and manage your health effortlessly</p>
            <router-link to="/login" class="btn btn-light btn-lg rounded-pill px-4 me-md-2 fw-bold">Get Started</router-link>
        </div>
    </header>
    
    <!-- Features Section -->
    <section id="features" class="py-5 bg-light">
        <div class="container">
            <div class="text-center mb-5">
                <h2 class="display-5 fw-bold mb-3">Why PentaFlow?</h2>
                <p class="fs-5 text-secondary col-lg-8 mx-auto">Designed to make your hospital experience simpler, faster, and stress-free.</p>
            </div>
            <div class="row row-cols-1 row-cols-md-3 g-4">
                <div class="col">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <i class="bi bi-clock-history feature-icon"></i>
                        </div>
                        <h5 class="fw-bold">Save Time</h5>
                        <p class="text-secondary">Skip long queues and unnecessary calls, manage appointments anytime, anywhere.</p>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <i class="bi bi-file-medical feature-icon"></i>
                        </div>
                        <h5 class="fw-bold">All Records in One Place</h5>
                        <p class="text-secondary">Access your appointments, medical history, and updates from a single dashboard.</p>
                    </div>
                </div>
                <div class="col">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <div class="d-flex justify-content-center align-items-center mb-3">
                            <i class="bi bi-database-lock feature-icon"></i>
                        </div>
                        <h5 class="fw-bold">Secure & Hospital-Trusted</h5>
                        <p class="text-secondary">Your data stays safe on a hospital-managed, secure platform.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- SignUp Section -->
    <section id="cta" class="signup-sec py-5 bg-primary text-white text-center">
        <div class="container py-4">
            <h2 class="display-5 fw-bold mb-3">Ready for a hassel free appointment?</h2>
            <p class="fs-5 mb-4 col-lg-8 mx-auto">Sign up now for easy healthcare today!</p>
            <router-link to="/register/patient" class="btn btn-light btn-lg rounded-pill px-5 fw-bold">Sign Up</router-link>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p class="mb-0">&copy; 2026 Pentaflow. All Rights Reserved.</p>
        </div>
    </footer>

</template>


<style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap');

  .brand-logo{
    color: #6150a1;
  }
  .brand-logo:hover{
    color: #330962;
    cursor: pointer;
  }
  .hero-section {
    background: linear-gradient(-20deg, #a8b3e8, #a1a8e3, #9c9cdd, #918cd1, #867bc4, #7c6bb7, #6953a2, #573c8c, #452477, #330962);
    color: white;
  }
  .feature-icon {
    font-size: 2.5rem;
    color: #4e05c3;
  }
  .card {
    border-radius: 1rem;
    transition: transform 0.2s ease-in-out;
  }
  .card:hover {
    transform: translateY(-5px);
  }
  .signup-sec{
    background: linear-gradient(to top, #a8b3e8, #a1a8e3, #9c9cdd, #918cd1, #867bc4, #7c6bb7, #6953a2, #573c8c);
    color: white;
  }
  #nav-login{
    color:#8f59df;
    font-weight: 650;
  }
  #nav-login:hover{
    color: #a378e0;
    text-decoration: underline;
  }
  #nav-register{
    color:#463bdf;
    font-weight: 650;
  }
  #nav-register:hover{
    color: #4e75eb;
    text-decoration: underline;
    transition: transform 0.3s ease-in-out
  }
</style>

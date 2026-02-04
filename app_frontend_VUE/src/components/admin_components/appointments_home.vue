<script setup>
import { ref, onMounted, provide} from "vue";
import axios_instance from "@/axiosSetup";

const data = ref({
appointment_count: 'N/A',
doctor_count: 'N/A',
patien_count: 'N/A'
});

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

async function loadStats() {
    try {
        const response = await axios_instance.get("/api/dashboard/admin/stats")
       
        data.value.appointment_count = response.data?.appointment_count
        data.value.doctor_count = response.data?.doctor_count
        data.value.patien_count = response.data?.patient_count

    } catch (err) {
        appendAlert("Stats loading failed.", "danger", "bi-exclamation-triangle")
    }
}

onMounted(() => {
    loadStats()
})


provide('triggerChildAlert', appendAlert)

</script>

<template>
    
    <div class="container-fluid">
        <div class="row g-4">
            <div class="col-12">
                <div class="row g-2 mb-2">
                    <div class="col-md-4">
                        <div class="card card-stat h-100 shadow-sm border-0">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-blue-soft text-primary">
                                    <i class="bi bi-calendar3"></i>
                                </div>
                                <div class="ms-3">
                                    <h6 class="fw-bold mb-0" style="color: #4b57d1;">Total Appointments</h6>
                                    <span class="h4 fw-bold mb-0 highlight-text">{{ data.appointment_count }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card card-stat h-100 shadow-sm border-0">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-green-soft text-success">
                                    <i class="bi bi-hospital"></i>
                                </div>
                                <div class="ms-3">
                                    <h6 class="fw-bold mb-0" style="color: #157508;">Doctors Registered</h6>
                                    <span class="h4 fw-bold mb-0 highlight-text">{{ data.doctor_count }}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card card-stat h-100 shadow-sm border-0">
                            <div class="card-body d-flex align-items-center">
                                <div class="stat-icon bg-yellow-soft text-danger">
                                    <i class="bi bi-house-heart"></i>
                                </div>
                                <div class="ms-3">
                                    <h6 class="fw-bold mb-0" style="color: #ca890f;">Patients Registered</h6>
                                    <span class="h4 fw-bold mb-0 highlight-text">{{ data.patien_count }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div ref="alertPlaceholder"></div>
                    
                </div>
            </div>
            
            <div class="col-12 d-flex justify-content-center mb-2">
                <div class="nav-slider-container">
                    <router-link to="/dashboard/admin/appointments/upcomming" class="nav-slider-item">
                        Upcoming
                    </router-link>
                    <router-link to="/dashboard/admin/appointments/completed" class="nav-slider-item">
                        Past
                    </router-link>
                </div>
                
            </div>

            <div class="col-12">
                <router-view></router-view>
            </div>
        </div>
    </div>
</template>

<style scoped>

.card-stat {
    transition: transform 0.2s ease;
    border-radius: 12px;
}

.card-stat:hover {
    transform: translateY(-2px);
}

.stat-icon {
    width: 55px;
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 1.5rem;
}

.bg-blue-soft { background-color: rgba(13, 110, 253, 0.1); }
.bg-yellow-soft { background-color: rgba(255, 136, 0, 0.1); }
.bg-green-soft { background-color: rgba(30, 156, 97, 0.1); }

/* Slide Toggle / Segmented Control */
.nav-slider-container {
    display: inline-flex;
    background-color: #ffffff;
    border: 2px solid rgb(207, 199, 238);
    padding: 4px;
    border-radius: 50px;
    position: relative;
    z-index: 1;
}

.nav-slider-item {
    padding: 8px 24px;
    border-radius: 50px;
    text-decoration: none;
    color: #7362a3;
    font-weight: 500;
    font-size: 0.9rem;
    position: relative;
    z-index: 3;
    transition: color 0.3s ease;
}

.router-link-active {
    background-color: #b694f1 !important;
    color: white;
}

.highlight-text{
    color: #341079;
    font-weight: 700;
}
</style>
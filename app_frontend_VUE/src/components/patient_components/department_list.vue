<script setup>
import { ref, onMounted} from "vue";
import router from "@/router";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    departments: [],
    deptCount: 0,
    isLoading: true,
    error: null,
})

async function loadAvailableDepartments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/departments")
        data.value.deptCount = response.data.count
        data.value.departments = response.data.departments
    } catch (err) {
        data.value.deptCount = 0
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Departments data loading failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

async function loadFilteredDepartments() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/patient/departments/search",
        {  
            params: {
                "query": globalTemp.get("searchQuery")
            }
        })
        data.value.deptCount = response.data.count
        data.value.departments = response.data.departments
        globalTemp.reset("searchQuery")
    } catch (err) {
        data.value.deptCount = 0
        data.value.error = err.response?.data?.message || err.message
        if (err.response?.status === 404){
            appendAlert("Searched department not found.", "info", "bi-info-circle")
        }
        else{
            appendAlert("Searched departments data loading failed.", "danger", "bi-exclamation-triangle")
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

// Handle Selected Department
function selectDepartment(dept_name){
    globalTemp.set("department_name", dept_name)
    router.replace('/dashboard/patient/doctor-list')
}


onMounted(() => {

    if(globalTemp.get('searchResource') === 'departments'){
        globalTemp.reset('searchResource')
        loadFilteredDepartments()
    }
    else{
        loadAvailableDepartments()
    }
})

const refreshDepartments = () => {
  loadAvailableDepartments()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-2">
            <div ref="alertPlaceholder"></div>
            
            <div class="d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center">
                   <h2 class="h4 fw-bold" style="color: #220349;">Available Departments</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshDepartments" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                
                <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.deptCount }}</span>
            </div>

            <div class="row row-cols-1 row-cols-md-3 g-4">
                <div v-if="data.isLoading" class="col-12 w-100">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <div class="d-flex justify-content-center align-items-center gap-2 p-4">
                            <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                            <p class="mb-0 fw-medium">Loading Departments...</p>
                        </div>
                    </div>
                </div>

                <div v-else-if="data.error" class="col-12 w-100">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <p class="fw-medium text-danger mt-2 p-4">{{ data.error }}</p>
                    </div>
                </div>

                <div v-else-if="data.deptCount === 0" class="col-12 w-100">
                    <div class="card h-100 p-4 shadow-sm text-center">
                        <p class="fw-medium text-primary mt-2 p-4">No department available yet.</p>
                    </div>
                </div>

                <div v-else class="col" v-for="(dept) in data.departments" :key="dept.id">
                    <div class="card h-100 p-2 shadow-sm text-center">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-center align-items-center mb-2">
                                <i class="bi bi-heart-pulse feature-icon"></i>
                            </div>
                            <h5 class="fw-bold">{{ dept.name }}</h5>
                            <p class="text-secondary">{{ dept.description }}</p>

                            <div class="mt-auto">
                                <button @click="selectDepartment(dept.name)" type="button" title="View Doctors" class="btn px-4 rounded-pill view-btn">
                                    View Doctors
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<style scoped>
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

.count-bg{
  background-color: #9e81ec;
}

.highlight-text{
    color: #341079;
    font-weight: 700;
}

.view-btn{
    background:#eaeafa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(154, 153, 153);
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.view-btn:hover{
    background:#e2e2fa;
    color: rgb(23, 2, 2);
    border: 1px solid rgb(116, 115, 115);
}

</style>
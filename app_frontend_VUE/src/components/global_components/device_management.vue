<script setup>
import { ref, onMounted} from "vue";
import axios_instance from "@/axiosSetup";
import router from "@/router";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    devices: [],
    deviceCount: 0,
    isLoading: true,
    error: null,
})

async function loadDevices() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/devices")
        data.value.deviceCount = response.data.count
        data.value.devices = response.data.devices


    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        data.value.deviceCount = 0
        data.value.devices = []
        appendAlert("LoggedIn Devices Loading Failed.", "danger", "bi-exclamation-triangle")
    } finally {
        data.value.isLoading = false
    }
}

// async function loadFilteredDevices() {
//     data.value.isLoading = true
//     data.value.error = null
//     try {
//         const response = await axios_instance.get("/api/dashboard/admin/devices/search",
//         {  
//             params: {
//                 "query": globalTemp.get("searchQuery")
//             }
//         })
//         data.value.deviceCount = response.data.count
//         data.value.devices = response.data.devices
//         globalTemp.reset("searchQuery")
//     } catch (err) {
//         data.value.error = err.response?.data?.message || err.message
//         if (err.response?.status === 404){
//             appendAlert("Searched device(s) not found.", "info", "bi-info-circle")
//         }
//         else{
//             appendAlert("Devices data loading failed.", "danger", "bi-exclamation-triangle")
//         }
        
//     } finally {
//         data.value.isLoading = false
//     }
// }

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

const deviceToBeLogoutName = ref(null)
const deviceToBeLogoutJti = ref(null)
const selectDevice = (device) => {
    deviceToBeLogoutName.value = device.device_name
    deviceToBeLogoutJti.value = device.token_jti
}

// Handles a single device logout
const isLoggingOut = ref(false)
const loggingOutDeviceJti = ref(null)
async function logoutDevice(jti){
    if (isLoggingOut.value) return
    isLoggingOut.value = true
    loggingOutDeviceJti.value = jti
    try {
        await axios_instance.post("/api/device/logout", 
          {
            "token_jti": jti
          }
        )
        // Refresh the device list
        loadDevices()
        
        appendAlert("The device has been logged out successfully.",'success',"bi-check-circle")
    } catch(error) {
        const msg = error.response?.data?.message || "Device Logout Failed"
        appendAlert(msg, "danger", "bi-exclamation-triangle-fill")
        // console.log(error.response?.data)
    } finally {
        isLoggingOut.value = false
        loggingOutDeviceJti.value = null
        deviceToBeLogoutName.value = null
        deviceToBeLogoutJti.value = null
    }
}

// Handles all device logout
const isLoggingOutAll = ref(false)
async function logoutDeviceAll(){
    if (isLoggingOutAll.value) return
    isLoggingOutAll.value = true
    try {
        await axios_instance.post("/api/logout/all")
        appendAlert("All devices logged out successfully.",'success',"bi-check-circle")
        localStorage.clear();
        router.push("/")

    } catch(error) {
        const msg = error.response?.data?.message || "All Device Logout Failed"
        appendAlert(msg, "danger", "bi-exclamation-triangle-fill")
        // console.log(error.response?.data)
    } finally {
        isLoggingOutAll.value = false
    }
}


onMounted(() => {

    if(globalTemp.get('searchResource') === 'devices'){
        globalTemp.reset('searchResource')
        loadFilteredDevices()
    }
    else{
        loadDevices()
    }

})

const refreshDevices = () => {
  loadDevices()
}

</script>

<template>
    <div class="container-fluid min-vh-100">
        <div class="row g-4">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="d-flex align-items-center">
                   <h2 class="h4 fw-bold" style="color: #220349;">Device Management</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshDevices" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                
                <span class="badge count-bg px-3 py-2 text-white">Count: {{ data.deviceCount }}</span>
            </div>

            <div class="table-container shadow-sm border-1">
                <div class="table-responsive">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Name</th>
                                <th class="text-center">Date (Y-M-D)</th>
                                <th class="text-center">Time (24 HR.)</th>
                                <th class="text-center">Status</th>
                                <th class="text-center">Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-if="data.isLoading">
                                <td colspan="5" class="py-5 text-center text-muted">
                                    <div class="spinner-border spinner-border-sm me-2"></div> Loading...
                                </td>
                            </tr>

                            <tr v-else-if="data.error">
                                <td colspan="5" class="py-5 text-center text-danger fw-medium">
                                    {{ data.error }}
                                </td>
                            </tr>

                            <tr v-else-if="data.deviceCount === 0">
                                <td colspan="5" class="py-5 text-center text-primary fw-medium">No device registered yet.</td>
                            </tr>

                            <tr v-if="!data.isLoading && !data.error" v-for="(device) in data.devices" :key="device.device_name">
                                <td><div class="text-center fw-bold highlight-text">{{ device.device_name }}</div></td>
                                <td><div class="text-center text-primary fw-medium">{{ device.login_date }}</div></td>
                                <td><div class="text-center text-success fw-medium">
                                    {{ device.login_time }}
                                </div></td>

                                <td class="text-center">
                                    <div v-if="device.current_device" class="status-pill completed">
                                        Current Device
                                    </div>
                                    <div v-else class="status-pill booked">
                                        Other Device
                                    </div>
                                </td>

                                <td class="text-center">
                                    <button @click="selectDevice(device)" type="button" class="device-logout-btn px-4 rounded-pill btn" 
                                    title="Logout" data-bs-toggle="modal" data-bs-target="#logoutDeviceModal" v-if="loggingOutDeviceJti !== device.token_jti" :disabled="device.current_device">
                                        <div>
                                            <i class="bi bi-box-arrow-right pe-1 "></i>
                                            Logout
                                        </div>
                                    </button>

                                    <button type="button" class="device-logout-btn px-4 rounded-pill btn" 
                                    title="Logout" data-bs-toggle="modal" data-bs-target="#logoutDeviceModal" v-else disabled>
                                        <div>
                                            <i class="bi bi-box-arrow-right pe-1 "></i>
                                            Logging Out...
                                        </div>
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="col-12 mt-3 mb-2 d-flex justify-content-center" v-if="data.deviceCount > 0">
                    <button type="button" title="Logging Out All" class="btn px-4 text-white rounded-pill shadow-sm logout-all-btn" v-if="isLoggingOutAll" :disabled="isLoggingOutAll" id="clicked">
                        <span>Logging Out...</span>
                    </button>

                    <button type="button" title="Logout Everywhere" class="btn px-4 text-white rounded-pill shadow-sm logout-all-btn" data-bs-toggle="modal" data-bs-target="#logoutAllDeviceModal" v-else>
                        <span>Logout Everywhere</span>
                    </button>
                </div>
            </div>

            <!-- Confirm Device Logout Modal -->
            <div class="modal fade" id="logoutDeviceModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-sm"> 
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-body text-center p-3">
                        <div class="delete-icon-wrapper mb-3">
                            <i class="bi bi-exclamation-circle text-danger"></i>
                        </div>
                        
                        <h5 class="fw-bold mb-2">Confirm Logout</h5>
                        <p class="text-muted mb-0">Are you sure you want to logout</p>
                        <p class="fw-bold text-dark">{{ deviceToBeLogoutName }}?</p>
                        <small class="text-secondary d-block mt-2">*Note: After logging out, the device may remain active for few seconds.</small>
                    </div>
                    
                    <div class="modal-footer border-0 d-flex justify-content-center pb-4">
                        <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm back-btn" data-bs-dismiss="modal">Back</button>
                        <button @click="logoutDevice(deviceToBeLogoutJti)" type="button" class="btn px-4 mx-2 rounded-pill shadow-sm logout-btn" data-bs-dismiss="modal">
                            Logout
                        </button>
                    </div>
                </div>
            </div>
            </div>

            <!-- Confirm All Device Logout Modal -->
            <div class="modal fade" id="logoutAllDeviceModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered modal-sm"> 
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-body text-center p-3">
                        <div class="delete-icon-wrapper mb-3">
                            <i class="bi bi-exclamation-circle text-danger"></i>
                        </div>
                        
                        <h5 class="fw-bold mb-2">Confirm Logout</h5>
                        <p class="text-muted mb-0">Are you sure you want to logout</p>
                        <p class="fw-bold text-dark">All Devices</p>
                        <small class="text-secondary d-block mt-2">*Note: After logging out, the devices may remain active for few seconds.</small>
                    </div>
                    
                    <div class="modal-footer border-0 d-flex justify-content-center pb-4">
                        <button type="button" class="btn px-4 mx-2 rounded-pill shadow-sm back-btn" data-bs-dismiss="modal">Back</button>
                        <button @click="logoutDeviceAll" type="button" class="btn px-4 mx-2 rounded-pill shadow-sm logout-btn" data-bs-dismiss="modal">
                            Logout
                        </button>
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

.device-logout-btn{
    align-items: center;
    background: linear-gradient(135deg,#c87c7c, #bb4e4e, #ab3e3ef4); 
    color: white;
    border: 1px solid rgb(150, 149, 149);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    min-width: 145px;
}
.device-logout-btn:hover{
    background: linear-gradient(135deg,#dd9494fc, #d37070fb, #b16363fb);
    color:white;
    border: 1px solid rgb(131, 130, 130);
}

.device-logout-btn:disabled{
    background: linear-gradient(135deg,#dd9696, #d37070, #b16363);
    color:white;
    border: 1px solid rgb(131, 131, 131);
}

.count-bg{
  background-color: #9e81ec;
}

.highlight-text{
    color: #341079;
    font-weight: 700;
}

.status-pill {
    padding: 4px 8px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-pill.completed {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #15b98b;
}

.status-pill.booked {
    background-color: #faf4c1;
    color: #a3560e;
    border-style: solid;
    border-color: #d4ae2f;
}

.status-pill.canceled {
    background-color: #ffcdcda9;
    color: #9c1b1b;
    border-style: solid;
    border-color: #f8333388;
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
    border: 1px solid rgb(116, 115, 115);
}

.logout-btn {
    align-items: center;
    background: #cc3d33; 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.logout-btn:hover {
    background: #b93030;
    color:white;
}

.logout-all-btn {
    align-items: center;
    background: linear-gradient(135deg,#c45c5c, #9e3636, #9e2d2d); 
    color: white;
    border: 1px solid gray;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}
.logout-all-btn:hover {
    background: linear-gradient(135deg,#8e1e1e, #a54545, #c86b6b);
    color:white;
}
#clicked {
    background: linear-gradient(135deg,#8f1e1e, #b34545, #b65b5b);
    color:white;
    cursor:not-allowed;
}

</style>
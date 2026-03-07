<script setup>
import { ref, onMounted} from "vue";
import axios_instance from "@/axiosSetup";
import { useGlobalTemp } from '@/stores/temp_data';

const globalTemp = useGlobalTemp()

const data = ref({
    availabilities: [],
    availCount: 0,
    week_start_date: '0000-00-00',
    week_end_date: '0000-00-00',
    isLoading: false,
    error: null,
})

async function loadAvailabilities() {
    data.value.isLoading = true
    data.value.error = null
    try {
        const response = await axios_instance.get("/api/dashboard/doctor/availability")
        data.value.availCount = response.data?.count
        data.value.week_start_date = response.data?.week_start_date
        data.value.week_end_date = response.data?.week_end_date
        data.value.availabilities = response.data?.availabilities
    } catch (err) {
        data.value.error = err.response?.data?.message || err.message
        appendAlert("Availability schedule loading failed.", "danger", "bi-exclamation-triangle")
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


async function toggleAvailability(avail_slot) {
    try {
        const response = await axios_instance.patch("/api/dashboard/doctor/availability", 
          {
            "slot_id": avail_slot.slot_id,
            "patient_cap": avail_slot.diagonisis_limit,
            "status": !avail_slot.status
          }
        )
        appendAlert("Availability time changes saved.", "success", "bi-check-circle")
        avail_slot.status = !avail_slot.status
        loadAvailabilities()
    } catch (err) {
        appendAlert("Failed to save availability time.", "danger", "bi-exclamation-triangle")
    }
}

async function savePatientCap(avail_slot) {
    try {
        const response = await axios_instance.patch("/api/dashboard/doctor/availability", 
          {
            "slot_id": avail_slot.slot_id,
            "patient_cap": avail_slot.diagonisis_limit,
            "status": avail_slot.status
          }
        )
        appendAlert(`Maximum patient count changes saved.`, "success", "bi-check-circle")
        loadAvailabilities()
    } catch (err) {
        appendAlert("Failed to save maximum patient count.", "danger", "bi-exclamation-triangle")
    }
}

onMounted(() => {
    loadAvailabilities()
})

const refreshAvailability = () => {
  loadAvailabilities()
}

</script>

<template>
    <div class="container-fluid">
        <div class="row g-3">
            <div ref="alertPlaceholder"></div>
            <div class="d-flex justify-content-between align-items-center mb-1">
                <div class="d-flex align-items-center">
                   <h2 class="h4 fw-bold" style="color: #220349;">Manage Availability</h2> 
                   
                    <button class="btn btn-sm border-0 text-primary" 
                    @click="refreshAvailability" v-if="!data.isLoading" title="Refresh">
                        <i class="bi bi-arrow-clockwise fs-6"></i>
                    </button>
                    <button class="btn btn-sm border-0 text-success" v-else title="Loading" style="cursor: not-allowed;">
                        <i class="bi bi-arrow-repeat fs-6"></i>
                    </button>
                </div>
                    
                <span class="badge week-badge-bg px-3 py-2 text-info">From {{ data.week_start_date }} to {{ data.week_end_date }}</span>
            </div>

            <div class="table-container shadow border-2">
                <div class="table-responsive ">
                    <table class="table-style">
                        <thead>
                            <tr>
                                <th class="text-center">Date (Y-M-D)</th>
                                <th class="text-center">Weekday</th>
                                <th class="text-center">Time Slot 1</th>
                                <th class="text-center">Max Patients 1</th>
                                <th class="text-center">Time Slot 2</th>
                                <th class="text-center">Max Patients 2</th>
                                <th class="text-center">Time Slot 3</th>
                                <th class="text-center">Max Patients 3</th>
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

                            <tr v-else-if="data.availCount !== 7">
                                <td colspan="8" class="py-5 text-center text-primary fw-medium">No availabilities provided yet.</td>
                            </tr>

                            <tr v-else v-for="(avail) in data.availabilities" :key="avail.weekday">
                                <td class="text-center"><div class="date-badge fw-bold">{{ avail.date }}</div></td>
                                <td class="text-center"><span class="fw-bold highlight-text fs-6">{{ avail.weekday }}</span></td>
                                <td class="text-muted text-center">
                                  <button @click="toggleAvailability(avail.slots[0])" 
                                  class="border-0 btn" title="Toggle Availability" :id="avail.slots[0].slot_id">
                                    <div class="time-slot-pill" :class="avail.slots[0].status ? 'active' : 'inactive'">
                                        {{ avail.slots[0].start_time  }} to {{ avail.slots[0].end_time }}
                                    </div>
                                  </button>
                                </td>

                                <td class="align-items-center" style="min-width: 120px;">
                    
                                    <select @change="savePatientCap(avail.slots[0])" 
                                    class="form-select patient-cap fw-medium text-secondary" :id="avail.slots[0].slot_id"
                                    :disabled="!avail.slots[0].status" 
                                    v-model="avail.slots[0].diagonisis_limit" required>
                                        <option value=0 hidden>0</option>
                                        <option value=10 selected>10</option>
                                        <option value=20>20</option>
                                        <option value=30>30</option>
                                    </select>
                                   
                                </td>

                                <td class="text-muted text-center">
                                  <button @click="toggleAvailability(avail.slots[1])" 
                                  class="border-0 btn" title="Toggle Availability" :id="avail.slots[1].slot_id">
                                    <div class="time-slot-pill" :class="avail.slots[1].status ? 'active' : 'inactive'">
                                        {{ avail.slots[1].start_time  }} to {{ avail.slots[1].end_time }}
                                    </div>
                                  </button>
                                </td>

                                <td class="align-items-center"  style="min-width: 120px;">
                                    
                                    <select @change="savePatientCap(avail.slots[1])" 
                                    class="form-select patient-cap fw-medium text-secondary" :id="avail.slots[1].slot_id"
                                    :disabled="!avail.slots[1].status" 
                                    v-model="avail.slots[1].diagonisis_limit" required>
                                        <option value=0 hidden>0</option>
                                        <option value=10 selected>10</option>
                                        <option value=20>20</option>
                                        <option value=30>30</option>
                                    </select>
                                   
                                </td>

                                <td class="text-muted text-center">
                                  <button @click="toggleAvailability(avail.slots[2])" 
                                  class="border-0 btn" title="Toggle Availability" :id="avail.slots[2].slot_id">
                                    <div class="time-slot-pill" :class="avail.slots[2].status ? 'active' : 'inactive'">
                                        {{ avail.slots[2].start_time  }} to {{ avail.slots[2].end_time }}
                                    </div>
                                  </button>
                                </td>

                                <td class="align-items-center" style="min-width: 120px;">
                                    <select @change="savePatientCap(avail.slots[2])" 
                                    class="form-select patient-cap fw-medium text-secondary" :id="avail.slots[2].slot_id"
                                    :disabled="!avail.slots[2].status" 
                                    v-model="avail.slots[2].diagonisis_limit" required>
                                        <option value=0 hidden>0</option>
                                        <option value=10 selected>10</option>
                                        <option value=20>20</option>
                                        <option value=30>30</option>
                                    </select>
                                </td>
                                
                            </tr>
                          
                        </tbody>
                    </table>
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
    background-color: #b4e3f569;
    color: #40576b;
    font-weight: 650;
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
    background-color: #f9faff;
}

.time-slot-pill {
    padding: 6px 12px;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 600;
}

.time-slot-pill.active {
    background-color: #e6fffa;
    color: #047857;
    border-style: solid;
    border-color: #15b98b;
}

.time-slot-pill.inactive {
    background-color: #fef2f2;
    color: #b9681c;
    border-style: solid;
    border-color: #f08e68;
}

.time-slot-pill.deactive {
    background-color: #dad6d6a9;
    color: #4e4e4e;
    border-style: solid;
    border-color: #524f4f88;
}

.date-badge {
    background: #acb0ee96;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #08305ffa;
}

.week-badge-bg{
  background-color: #012c55c2;
}

.highlight-text{
    color: #7845d6;
    font-weight: 600;
}

.patient-cap{
    background-color: #fdfbff;
    border: 1px solid #9473e2;
    border-radius: 12px;
    transition: all 0.2s ease;
    cursor: pointer;
}
.patient-cap:focus {
  background-color: #fff;
  border-color: #635bff;
  box-shadow: 0 0 0 4px rgba(140, 91, 255, 0.226);
}
.patient-cap:disabled {
  background-color: #f3f1f1;
  border-color: #969595;
  cursor: not-allowed;
}
</style>
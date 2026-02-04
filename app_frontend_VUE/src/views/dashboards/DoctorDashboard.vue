<script setup>
    import {ref} from "vue"
    import axios_instance from "../../axiosSetup"
    import router from "../../router"

    axios_instance.get('/api/dashboard')
    .then(response =>{
        console.log(response.data)
        // router.push({name: 'Home'})
        if(response.data.role !== 'doctor'){
            logout()
        }
    })
    .catch(error =>{
        router.push('/')
        console.log(error.response.data)
    })

    const isLoggingOut = ref(false)
    async function logout(){
        if (isLoggingOut.value) return
        isLoggingOut.value = true
        try {
            const response = await axios_instance.post("/api/logout")
            // appendAlert("Login Successful!", "success", "bi-check-circle-fill")
            localStorage.clear();
            router.push("/")
        } catch(error) {
            const msg = error.response?.data?.message || "Logout failed"
            // appendAlert(msg, "danger", "bi-exclamation-triangle-fill")
            console.log(error.response?.data)
        } finally {
            isLoggingOut.value = false
        }
    }
</script>

<template>
    <div class="text-center">
        <h1>Welcome to Doctor dashboard</h1>
        <button @click="logout" class="btn btn-warning fw-bold text-secondary">Logout</button>
    </div>
</template>

<style scoped>

</style>
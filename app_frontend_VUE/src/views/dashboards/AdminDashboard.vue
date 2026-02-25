<script setup>
    import {ref, watch, onMounted, onUnmounted} from "vue";
    import axios_instance from "@/axiosSetup";
    import router from "@/router";
    import { useRoute } from 'vue-router';
    import { useGlobalTemp } from '@/stores/temp_data';

    const globalTemp = useGlobalTemp()
    const currentRoutePath = ref('/dashboard/admin/appointments/upcomming')
    const searchPlaceholder = ref("Search appointments...")
    const routeChangeCounter = ref(0)
    const searchString = ref('')

    // Sidebar toggler for both mobile and desktop 
    const isSidebarOpen = ref(true);
    const route = useRoute();

    const toggleSidebar = () => {
        isSidebarOpen.value = !isSidebarOpen.value;
    }

    // Function to handle automatic closing on window resize
    const handleResize = () => {
        if (window.innerWidth < 992) {
            isSidebarOpen.value = false;
        } else {
            isSidebarOpen.value = true;
        }
    }

    // Watches for route changes
    watch(() => route.path, () => {
        // Change Search resource path
        currentRoutePath.value = route.path
        if(currentRoutePath.value === '/dashboard/admin/patients'){
            searchPlaceholder.value = "Search patients..."
        }
        else if(currentRoutePath.value === '/dashboard/admin/doctors'){
            searchPlaceholder.value = "Search doctors..."
        }
        else if(currentRoutePath.value === '/dashboard/admin/appointments/upcomming' || currentRoutePath.value === '/dashboard/admin/appointments/completed'){
            searchPlaceholder.value = "Search appointments..."
        }
        else{
            searchPlaceholder.value = "Search Unavilable..."
        }


        // If we are on a mobile/tablet screen, close the sidebar on navigation
        if (window.innerWidth < 992) {
            isSidebarOpen.value = false;
        }
    });

    // if the search field becomes clear 
    watch(searchString, (newStr) => {
        if (newStr === '') {
            routeChangeCounter.value++
            router.push(currentRoutePath.value)
        }
    });

    async function get_user_data(){
        try{
            const response = await axios_instance.get('/api/dashboard/admin')
            localStorage.setItem("admin_data", JSON.stringify(response.data))
            if(response.data.role !== 'admin'){
                logout()
            }
            // console.log(response.data)
        } catch (error){
            logout()
        }  
    }

    onMounted(() => {
        // Store the current user common data
        get_user_data()

        // Set initial state based on current screen size
        handleResize();

        if(globalTemp.get('LoginStatus') === 'success'){
            appendAlert("Login Successful!", "success", "bi-check-circle-fill")
            globalTemp.reset('LoginStatus')
        }
    
        // Listen for window resizing
        window.addEventListener('resize', handleResize);

        document.body.style.overflow = "hidden"
        document.body.style.fontFamily = "Montserrat', Arial, Helvetica, sans-serif"
        document.body.style.height = "100%"
        document.body.style.margin = "0"
    })

    onUnmounted(() => {
        // Clean up listener to prevent memory leaks
        window.removeEventListener('resize', handleResize);

        document.body.style.overflow = ""
        document.body.style.fontFamily = ""
        document.body.style.height = ""
        document.body.style.margin = ""
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
        // disappear after 3 seconds
        setTimeout(() => {
            if (alertPlaceholder.value) {
            alertPlaceholder.value.innerHTML = ''
            }
        }, 3000)
    }
    
    const isLoggingOut = ref(false)
    async function logout(){
        if (isLoggingOut.value) return
        isLoggingOut.value = true
        try {
            await axios_instance.post("/api/logout")
            localStorage.clear();
            router.push("/")
        } catch(error) {
            const msg = error.response?.data?.message || "Logout Failed"
            appendAlert(msg, "danger", "bi-exclamation-triangle-fill")
            // console.log(error.response?.data)
        } finally {
            isLoggingOut.value = false
        }
    }

    function refresh_page(){
        window.location.reload()
    }

    
    async function searchQuery(){
        if (searchString.value.trim() === '') return

        if(currentRoutePath.value === '/dashboard/admin/patients'){
            // appendAlert(`Searching for patient '${searchString.value.trim()}' Successful. In ${currentRoutePath.value}`, "success", "bi-check-circle-fill")
            globalTemp.set('searchResource', 'patient')
            globalTemp.set('searchQuery', searchString.value.trim())
            routeChangeCounter.value++
            router.push('/dashboard/admin/patients')
        }
        else if(currentRoutePath.value === '/dashboard/admin/doctors'){
            // appendAlert(`Searching for doctor '${searchString.value.trim()}' Successful. In ${currentRoutePath.value}`, "success", "bi-check-circle-fill")
            globalTemp.set('searchResource', 'doctor')
            globalTemp.set('searchQuery', searchString.value.trim())
            routeChangeCounter.value++
            router.push('/dashboard/admin/doctors')
        }
        else{
            appendAlert("Searching Not Available.", "danger", "bi-exclamation-triangle-fill")
        }
    }

    function clearSearchString(){
        searchString.value = ''
    }
    
</script>

<template>
<div class="dashboard-wrapper">
    <div v-if="isSidebarOpen" class="sidebar-overlay d-lg-none" @click="isSidebarOpen = false"></div>

    <aside class="sidebar py-4" :class="{ 'show': isSidebarOpen, 'collapsed': !isSidebarOpen }">
        <div class="d-lg-none position-absolute top-0 end-0 pt-4 pe-2">
            <button class="btn border-0 text-muted" @click="isSidebarOpen = false">
                <i class="bi bi-x-lg fs-4"></i>
            </button>
        </div>
        <div @click="refresh_page" class="px-4 mb-5 d-flex align-items-center logo-section" style="cursor: pointer;">
            <img src="@/assets/favicon/icons8-health-96.png" alt="PentaFlow-Logo" width="40" height="40" class="d-inline-block  align-text-bottom">
            <h4 class="mb-0 ps-1 fw-bold sidebar-text">PentaFlow</h4>   
        </div>

        <nav class="nav flex-column flex-grow-1 overflow-hidden">
            <small class="px-4 text-uppercase text-muted fw-bold mb-2 sidebar-text" style="font-size: 0.7rem;">Navigation</small>

            <router-link to="/dashboard/admin/appointments" class="nav-link" title="Appointments"><i class="bi bi-calendar2-check me-3"></i><span class="sidebar-text">Appointments</span></router-link>

            <router-link to="/dashboard/admin/patients" class="nav-link" :class="{ 'router-link-active': $route.path.includes('/dashboard/admin/edit-patient') }" title="Patients"><i class="bi bi-people me-3"></i><span class="sidebar-text">Patients</span></router-link>

            <router-link to="/dashboard/admin/doctors" class="nav-link" :class="{ 'router-link-active': $route.path.includes('/dashboard/admin/edit-doctor') }" title="Doctors"><i class="bi bi-heart-pulse me-3"></i><span class="sidebar-text">Doctors</span></router-link>
            
            <router-link to="/dashboard/admin/add-doctor" class="nav-link" title="Add Doctor"><i class="bi bi-plus-square me-3"></i><span class="sidebar-text">Add Doctor</span></router-link>

            <div class="mt-5 px-4 border-top pt-4">
                <a class="nav-link px-0 text-danger" @click="logout" title="Logout"><i class="bi bi-power me-3"></i><span class="sidebar-text">Logout</span></a>
            </div>
        </nav>
    </aside>

    <main class="main-container">
        <div ref="alertPlaceholder"></div>
        <header class="sticky-top ps-1 p-3 d-flex align-items-center justify-content-between bg-white shadow-sm">
            <div class="d-flex align-items-center flex-grow-1">
                <button class="btn me-3 border-0" @click="toggleSidebar">
                    <i class="bi bi-chevron-bar-left fs-5 left-toggle text-secondary" :class="{ 'show': !isSidebarOpen }" title="Close Sidebar"></i>
                    <i class="bi bi-chevron-bar-right fs-5 right-toggle text-secondary" :class="{ 'show': isSidebarOpen }" title="Open Sidebar"></i>
                </button>

                <form @submit.prevent="searchQuery" class="search-bar w-100" style="max-width: 400px;">
                    <div class="input-group" >
                        <button type="submit" class="btn border-0" style="cursor:pointer;" title="Search"><i class="bi bi-search text-primary"></i></button>
                        <input type="text" class="form-control border-0 shadow-none" v-model="searchString"  :placeholder="searchPlaceholder" required>
                        <span class="input-group-text bg-transparent border-0" @click="clearSearchString" style="cursor:pointer;" v-if="searchString !== ''" title="Clear"><i class="bi bi-x-circle text-black"></i></span>
                    </div>
                </form>
            </div>
            
            <div class="d-flex align-items-center">
                <button class="btn border-0 position-relative me-3">
                    <i class="bi bi-bell fs-5"></i>
                    <span class="position-absolute top-25 start-75 translate-middle p-1 bg-danger border border-light rounded-circle"></span>
                </button>
                <div class="d-flex align-items-center border-start ps-3">
                    <div class="text-end me-2 d-none d-md-block">
                        <div class="fw-bold small">Admin</div>
                    </div>
                    <img src="@/assets/favicon/icons8-admin-100.png" class="rounded-circle" width="40" height="40" alt="Avatar">
                </div>
            </div>
        </header>
        
        <div class="content-body">
            <router-view :key="routeChangeCounter"></router-view>
        </div>
    </main>
</div>
</template>

<style scoped>
    .dashboard-wrapper {
        --sidebar-width: 260px;
        --sidebar-collapsed-width: 85px;
        --sidebar-bg: #ffffff;
        --main-bg: #f9f6ff;
        --primary-purple: #7f5bff;
        
        display: flex;
        height: 100vh;
        width: 100vw;
        background-color: var(--main-bg);
        overflow: hidden;
    }

    .sidebar {
        width: var(--sidebar-width);
        min-width: var(--sidebar-width);
        height: 100%;
        background: var(--sidebar-bg);
        border-right: 1px solid #e9ecef;
        display: flex;
        flex-direction: column;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        z-index: 1050;
    }


    /* Desktop Collapse (Hides text, keeps icons) */
    @media (min-width: 992px) {
        .sidebar.collapsed {
            width: var(--sidebar-collapsed-width);
            min-width: var(--sidebar-collapsed-width);
        }
        .sidebar.collapsed .sidebar-text {
            display: none;
        }
        .sidebar.collapsed .nav-link {
            text-align: center;
            margin: 0.2rem 0.5rem;
        }
        .sidebar.collapsed .nav-link i {
            margin-right: 0 !important;
            font-size: 1.3rem;
        }
    }

    /* Mobile Transitions */
    @media (max-width: 991px) {
        .sidebar {
            position: fixed;
            left: calc(var(--sidebar-width) * -1);
        }
        .sidebar.show {
            left: 0;
        }
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.3);
            z-index: 1040;
        }
    }

    .main-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        min-width: 0;
        height: 100%;
    }
    
    .content-body {
        flex-grow: 1;
        overflow-y: auto;
        padding: 1.5rem;
    }

    .nav-link {
        color: #6c757d;
        font-weight: 500;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        margin: 0.2rem 1rem;
        white-space: nowrap;
        cursor: pointer;
    }

    .router-link-active {
        background-color: #eee6fc !important;
        color: var(--primary-purple) !important;
    }
   
    .search-bar {
        background: #fff;
        border-radius: 50px;
        border: 1px solid #cac9c9;
        padding: 0.4rem 1rem;
    }

    .left-toggle.show{
        display: none;
    }
    .right-toggle.show{
        display: none;
    }
</style>
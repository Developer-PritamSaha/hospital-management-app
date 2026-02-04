import { createMemoryHistory, createRouter } from 'vue-router'

import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import PatientRegister from '@/views/RegisterPatient.vue'
import AdminDashboard from '@/views/dashboards/AdminDashboard.vue'
import DoctorDashboard from '@/views/dashboards/DoctorDashboard.vue'
import PatientDashboard from '@/views/dashboards/PatientDashboard.vue'

import ADappointments from '@/components/admin_components/appointments_home.vue'
import ADupcommingAp from '@/components/admin_components/upcomming_appointments.vue'
import ADcompletedAp from '@/components/admin_components/completed_appointments.vue'
import ADpatients from "@/components/admin_components/patients.vue"
import ADdoctors from "@/components/admin_components/doctors.vue"
import ADeditDoc from "@/components/admin_components/edit_doctor.vue"
import ADeditPat from "@/components/admin_components/edit_patient.vue"
import ADregDoc from "@/components/admin_components/register_doctor.vue"

const routes = [
  { 
    path: '/', 
    name: "Home",
    component: Home 
  },
  { 
    path: '/login', 
    name: "Login",
    component: Login 
  },
  { 
    path: '/register/patient', 
    name: "Register_Patient",
    component: PatientRegister 
  },
  {
    path: '/dashboard/admin', 
    name: "Admin_Dashboard",
    meta: { requiresAuth: true, role: 'admin' },
    component: AdminDashboard,
    children: [
      {
        path: "",
        name: "Admin_dashboard_home",
        redirect: "/dashboard/admin/appointments"
      },
      {
        path: "appointments",
        name: "Appointments_Dashboard",
        component: ADappointments,
        children:[
          {
            path: "",
            name: "Appointments_home",
            redirect: "/dashboard/admin/appointments/upcomming"
          },
          {
            path: "upcomming",
            name: "AdminUpcommingAppointments",
            component: ADupcommingAp,
          },
          {
            path: "completed",
            name: "AdminCompletedAppointments",
            component: ADcompletedAp,
          }
        ]
      },
      {
        path: "patients",
        name: "AdminPatients",
        component: ADpatients,
      },
      {
        path: "doctors",
        name: "AdminDoctors",
        component: ADdoctors,
      },
      {
        path: "add-doctor",
        name: "AdminDoctReg",
        component: ADregDoc,
      },
      {
        path: "edit-doctor",
        name: "AdminDoctEdit",
        component: ADeditDoc,
      },
      {
        path: "edit-patient",
        name: "AdminPatientEdit",
        component: ADeditPat,
      },
      // {
      //   path: "",
      //   name: "",
      //   component: ,
      // },
      
    ]
  },
  {
    path: '/dashboard/patient', 
    name: "Patient_Dashboard",
    meta: { requiresAuth: true, role: 'patient' },
    component: PatientDashboard
  },
  {
    path: '/dashboard/doctor', 
    name: "Doctor_Dashboard",
    meta: { requiresAuth: true, role: 'doctor' },
    component: DoctorDashboard
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'Not_Found',
    component: Home
  }
]

const router = createRouter({
  history: createMemoryHistory(),
  routes,
})

// Check Auth tokens for protected routes
const getAuthTokens = () => {
    const authTokens = localStorage.getItem('tokens')
    return authTokens ? JSON.parse(authTokens) : null
}
router.beforeEach((to, from, next) => {
  const isAuth = getAuthTokens();

  // Check if the route requires auth
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuth) {
      next({ name: 'Login' });
    } else {
      next(); // continue to protected route
    }
  } else {
    next(); // continue to public route
  }
});

export default router
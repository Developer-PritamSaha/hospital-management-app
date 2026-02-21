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

import DRappointments from '@/components/doctor_components/appointments_home.vue'
import DRupcomingAp from '@/components/doctor_components/upcoming.vue'
import DRavailability from '@/components/doctor_components/availability.vue'
import DRpatients from "@/components/doctor_components/assigned_patients.vue"
import DRpatientTreatment from "@/components/doctor_components/update_patient_history.vue"
import DRpatientTreatmentHist from "@/components/doctor_components/patient_history.vue"

import PAdoctors from '@/components/patient_components/doctors_list.vue'
import PAappointments from '@/components/patient_components/book_appointments.vue'

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
        name: "AdminAppointments",
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
    component: PatientDashboard,
    children: [
      {
        path: "",
        name: "Patient_dashboard_home",
        redirect: "/dashboard/patient/doctor-list"
      },
      {
        path: "doctor-list",
        name: "PatientCheckDoctors",
        component: PAdoctors
      },
      {
        path: "book-appointment",
        name: "PatientBookAppointments",
        component: PAappointments
      }

    ]
  },
  {
    path: '/dashboard/doctor', 
    name: "Doctor_Dashboard",
    meta: { requiresAuth: true, role: 'doctor' },
    component: DoctorDashboard,
    children:[
      {
        path: "",
        name: "Doctor_dashboard_home",
        redirect: "/dashboard/doctor/appointments"
      },
      {
        path: "appointments",
        name: "DoctorAppointments",
        component: DRappointments,
        children:[
          {
            path: "",
            name: "DrAppointmentsHome",
            redirect: "/dashboard/doctor/appointments/upcoming"
          },
          {
            path: "upcoming",
            name: "DoctorUpcommingAppointments",
            component: DRupcomingAp,
          },
          // {
          //   path: "patient-treatment",
          //   name: "DoctorPatientTreatment",
          //   component: DRpatientTreatment,
          // }
        ]
      },
      {
        path: "patient-treatment",
        name: "DoctorPatientTreatment",
        component: DRpatientTreatment,
      },
      {
        path: "assigned-patients",
        name: "DoctorAssignedPatiets",
        component: DRpatients,
      },
      {
        path: "patient-history",
        name: "DoctorAssignedPatietHistory",
        component: DRpatientTreatmentHist,
      },
      {
        path: "availability",
        name: "DoctorAvailability",
        component: DRavailability,
      },
    ]
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
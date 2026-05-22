import { createMemoryHistory, createRouter } from 'vue-router'

import Home from '@/views/Home.vue'
import Login from '@/views/Login.vue'
import PatientRegister from '@/views/RegisterPatient.vue'

import AdminDashboard from '@/views/dashboards/AdminDashboard.vue'
import DoctorDashboard from '@/views/dashboards/DoctorDashboard.vue'
import PatientDashboard from '@/views/dashboards/PatientDashboard.vue'

import DeviceMng from '@/components/global_components/device_management.vue'

import ADappointments from '@/components/admin_components/appointments_home.vue'
import ADupcommingAp from '@/components/admin_components/upcomming_appointments.vue'
import ADpreviousAp from '@/components/admin_components/previous_appointments.vue'
import ADpatientHistory from '@/components/admin_components/patient_medical_history.vue'
import ADpatients from "@/components/admin_components/patients.vue"
import ADdoctors from "@/components/admin_components/doctors.vue"
import ADeditDoc from "@/components/admin_components/edit_doctor.vue"
import ADeditPat from "@/components/admin_components/edit_patient.vue"
import ADregDoc from "@/components/admin_components/register_doctor.vue"

import DRappointments from '@/components/doctor_components/appointments_home.vue'
import DRupcomingAp from '@/components/doctor_components/upcoming_appointments.vue'
import DRhistoryAp from '@/components/doctor_components/appointment_history.vue'
import DRavailability from '@/components/doctor_components/availability.vue'
import DRpatients from "@/components/doctor_components/assigned_patients.vue"
import DRpatientTreatment from "@/components/doctor_components/update_patient_history.vue"
import DRpatientTreatmentHist from "@/components/doctor_components/patient_history.vue"

import PAdoctors from '@/components/patient_components/doctors_list.vue'
import PAbookAppointments from '@/components/patient_components/book_appointments.vue'
import PAupcomingappointments from '@/components/patient_components/upcoming_appointments.vue'
import PAdepartments from '@/components/patient_components/department_list.vue'
import PAhistoryData from '@/components/patient_components/treatment_history.vue'
import PAprofile from '@/components/patient_components/profile.vue'

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
            redirect: "/dashboard/admin/appointments/upcoming"
          },
          {
            path: "upcoming",
            name: "AdminUpcommingAppointments",
            component: ADupcommingAp,
          },
          {
            path: "previous",
            name: "AdminAllAppointments",
            component: ADpreviousAp,
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
      {
        path: "patient-records",
        name: "AdminPatientHistory",
        component: ADpatientHistory
      },
      {
        path: "devices",
        name: "AdminDeviceMng",
        component: DeviceMng
      }
      
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
        redirect: "/dashboard/patient/appointments"
      },
      {
        path: "doctor-list",
        name: "PatientCheckDoctors",
        component: PAdoctors
      },
      {
        path: "book-appointment",
        name: "PatientBookAppointments",
        component: PAbookAppointments
      },
      {
        path: "appointments",
        name: "PatientUpcomingAppointments",
        component: PAupcomingappointments
      },
      {
        path: "department-list",
        name: "PatientDepartmentList",
        component: PAdepartments
      },
      {
        path: "history",
        name: "PatientMedicalHistory",
        component: PAhistoryData
      },
      {
        path: "profile",
        name: "PatientProfile",
        component: PAprofile
      },
      {
        path: "devices",
        name: "PatientDeviceMng",
        component: DeviceMng
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
          {
            path: "history",
            name: "DoctorAppointmentHistory",
            component: DRhistoryAp,
          }
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
      {
        path: "devices",
        name: "DoctorDeviceMng",
        component: DeviceMng
      }
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
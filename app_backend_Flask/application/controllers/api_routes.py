from flask import current_app as app
from app_backend_Flask.application.api import *

### Adding API resorces to their respective routes
## Login Registration APIs
app.extensions["api"].add_resource(PatientRegistration, "/api/register/patient")
app.extensions["api"].add_resource(DoctorRegistration, "/api/register/doctor")
app.extensions["api"].add_resource(UserLogin, "/api/login")
app.extensions["api"].add_resource(TokenRefresher, "/api/token/refresh")
app.extensions["api"].add_resource(UserTokenRole, "/api/token/user/role-valid")
app.extensions["api"].add_resource(UserLogout, "/api/logout")
app.extensions["api"].add_resource(UserLogoutEverywhere, "/api/logout/all")

## Search APIs
app.extensions["api"].add_resource(AdminSearchAppointments, "/api/dashboard/admin/appointments/search")
app.extensions["api"].add_resource(AdminSearchPatientsData, "/api/dashboard/admin/patients/search")
app.extensions["api"].add_resource(AdminSearchDoctorsData, "/api/dashboard/admin/doctors/search")

app.extensions["api"].add_resource(DoctorSearchAssignedPatientsData, "/api/dashboard/doctor/assigned-patients/search")
app.extensions["api"].add_resource(DoctorSearchAppointments, "/api/dashboard/doctor/appointments/search")

app.extensions["api"].add_resource(PatientSearchUpcomingAppointments, "/api/dashboard/patient/upcoming-appointments/search")
app.extensions["api"].add_resource(PatientSearchDepartments, "/api/dashboard/patient/departments/search")
app.extensions["api"].add_resource(PatientSearchDepartmentDoctors, "/api/dashboard/patient/doctor-list/search")
app.extensions["api"].add_resource(PatientSearchAppointmentHistory, "/api/dashboard/patient/appointment-history/search")

## Admin APIs
app.extensions["api"].add_resource(AdminDashboard, "/api/dashboard/admin")
app.extensions["api"].add_resource(AdminAppointments, "/api/dashboard/admin/appointments")
app.extensions["api"].add_resource(AdminPatientsData, "/api/dashboard/admin/patients")
app.extensions["api"].add_resource(AdminPatientAppointmentHistory, "/api/dashboard/admin/patient-appointments")
app.extensions["api"].add_resource(AdminPatientTreatmentData, "/api/dashboard/admin/patient-treatment")
app.extensions["api"].add_resource(AdminDoctorsData, "/api/dashboard/admin/doctors")
app.extensions["api"].add_resource(StatsCount, "/api/dashboard/admin/stats")
app.extensions["api"].add_resource(DepartmentList, "/api/dashboard/admin/departments")
app.extensions["api"].add_resource(SpecializationList, "/api/dashboard/admin/specializations")
app.extensions["api"].add_resource(AdminManageDoctor, "/api/dashboard/admin/doctor")
app.extensions["api"].add_resource(AdminManagePatient, "/api/dashboard/admin/patient")

## Doctor APIs
app.extensions["api"].add_resource(DoctorDashboard, "/api/dashboard/doctor")
app.extensions["api"].add_resource(DocStatsCount, "/api/dashboard/doctor/week-stats")
app.extensions["api"].add_resource(DoctorManageAvailability, "/api/dashboard/doctor/availability")
app.extensions["api"].add_resource(DoctorManageAppointments, "/api/dashboard/doctor/appointments")
app.extensions["api"].add_resource(DoctorAssignedPatient, "/api/dashboard/doctor/assigned-patients")
app.extensions["api"].add_resource(DoctorPatientTreatmentHistory, "/api/dashboard/doctor/patient-history")
app.extensions["api"].add_resource(DoctorPatientAppointmentTreatmentData, "/api/dashboard/doctor/treatment-data")

## Patient APIs
app.extensions["api"].add_resource(PatientDashboard, "/api/dashboard/patient")
app.extensions["api"].add_resource(PatientAvailableDoctors, "/api/dashboard/patient/doctor-list")
app.extensions["api"].add_resource(PatientUpcomingAppointments, "/api/dashboard/patient/upcoming-appointments")
app.extensions["api"].add_resource(PatientBookAppointment, "/api/dashboard/patient/book-appointment")
app.extensions["api"].add_resource(PatientDepartmentList, "/api/dashboard/patient/departments")
app.extensions["api"].add_resource(PatientAppointmentHistory, "/api/dashboard/patient/appointment-history")
app.extensions["api"].add_resource(PatientTreatmentData, "/api/dashboard/patient/appointment-treatment")

## Celery job API
app.extensions["api"].add_resource(ExportCsvReport,"/api/dashboard/patient/export-csv")
app.extensions["api"].add_resource(DownloadCSV,"/api/dashboard/patient/download-csv")

## Notifications APIs
app.extensions["api"].add_resource(AdminNotifications,"/api/dashboard/admin/notifications")
app.extensions["api"].add_resource(DoctorNotifications,"/api/dashboard/doctor/notifications")
app.extensions["api"].add_resource(PatientNotifications,"/api/dashboard/patient/notifications")
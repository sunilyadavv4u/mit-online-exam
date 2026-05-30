import apiClient from './client';

export const authApi = {
  login: (email, password) => apiClient.post('/auth/login/', { email, password }),
  register: (payload) => apiClient.post('/auth/register/', payload),
  logout: (refresh) => apiClient.post('/auth/logout/', { refresh }),
  forgotPassword: (email) => apiClient.post('/auth/forgot-password/', { email }),
  resetPassword: (token, new_password) =>
    apiClient.post('/auth/reset-password/', { token, new_password }),
  verifyEmail: (token) => apiClient.get(`/auth/verify-email/${token}/`),
  me: () => apiClient.get('/users/users/me/'),
  updateMe: (payload) => apiClient.patch('/users/users/me/', payload),
  changePassword: (oldPwd, newPwd) =>
    apiClient.post('/users/users/change-password/', {
      old_password: oldPwd,
      new_password: newPwd,
    }),
};

export const usersApi = {
  list: (params) => apiClient.get('/users/users/', { params }),
  get: (id) => apiClient.get(`/users/users/${id}/`),
  create: (payload) => apiClient.post('/users/users/', payload),
  update: (id, payload) => apiClient.patch(`/users/users/${id}/`, payload),
  remove: (id) => apiClient.delete(`/users/users/${id}/`),
  studentProfile: () => apiClient.get('/users/students/me/'),
  updateStudentProfile: (payload) => apiClient.patch('/users/students/me/', payload),
  teacherProfile: () => apiClient.get('/users/teachers/me/'),
  updateTeacherProfile: (payload) => apiClient.patch('/users/teachers/me/', payload),
};

export const subjectsApi = {
  list: (params) => apiClient.get('/exams/subjects/', { params }),
  create: (payload) => apiClient.post('/exams/subjects/', payload),
  update: (id, payload) => apiClient.patch(`/exams/subjects/${id}/`, payload),
  remove: (id) => apiClient.delete(`/exams/subjects/${id}/`),
};

export const examsApi = {
  list: (params) => apiClient.get('/exams/', { params }),
  get: (slug) => apiClient.get(`/exams/${slug}/`),
  create: (payload) => apiClient.post('/exams/', payload),
  update: (slug, payload) => apiClient.patch(`/exams/${slug}/`, payload),
  remove: (slug) => apiClient.delete(`/exams/${slug}/`),
  publish: (slug, status) => apiClient.post(`/exams/${slug}/publish/`, { status }),
  enroll: (slug, studentIds) =>
    apiClient.post(`/exams/${slug}/enroll/`, { student_ids: studentIds }),
  enrollAll: (slug) => apiClient.post(`/exams/${slug}/enroll-all/`),
  enrollments: (slug) => apiClient.get(`/exams/${slug}/enrollments/`),
  myUpcoming: () => apiClient.get('/exams/my-upcoming/'),
};

export const questionsApi = {
  list: (params) => apiClient.get('/questions/', { params }),
  get: (id) => apiClient.get(`/questions/${id}/`),
  create: (payload) => apiClient.post('/questions/', payload),
  update: (id, payload) => apiClient.patch(`/questions/${id}/`, payload),
  remove: (id) => apiClient.delete(`/questions/${id}/`),
};

export const attemptsApi = {
  list: (params) => apiClient.get('/submissions/attempts/', { params }),
  get: (id) => apiClient.get(`/submissions/attempts/${id}/`),
  start: (examId) => apiClient.post('/submissions/attempts/start/', { exam_id: examId }),
  saveAnswer: (attemptId, payload) =>
    apiClient.post(`/submissions/attempts/${attemptId}/answer/`, payload),
  submit: (attemptId, autoSubmit = false) =>
    apiClient.post(`/submissions/attempts/${attemptId}/submit/`, { auto: autoSubmit }),
  proctorEvent: (attemptId, eventType, metadata = {}) =>
    apiClient.post(`/submissions/attempts/${attemptId}/proctor-event/`, {
      event_type: eventType,
      metadata,
    }),
  runCode: (attemptId, payload) =>
    apiClient.post(`/submissions/attempts/${attemptId}/run-code/`, payload),
  myAttempts: () => apiClient.get('/submissions/attempts/my-attempts/'),
  pendingEvaluation: () => apiClient.get('/submissions/attempts/pending-evaluation/'),
};

export const evaluationsApi = {
  list: (params) => apiClient.get('/evaluations/', { params }),
  get: (id) => apiClient.get(`/evaluations/${id}/`),
  fromAttempt: (attemptId) =>
    apiClient.post('/evaluations/from-attempt/', { attempt_id: attemptId }),
  gradeAnswer: (id, payload) =>
    apiClient.post(`/evaluations/${id}/grade-answer/`, payload),
  publish: (id, publish = true) =>
    apiClient.post(`/evaluations/${id}/publish/`, { publish }),
  myResults: () => apiClient.get('/evaluations/me/'),
};

export const analyticsApi = {
  teacherDashboard: () => apiClient.get('/analytics/teacher-dashboard/'),
  studentDashboard: () => apiClient.get('/analytics/student-dashboard/'),
  superAdminDashboard: () => apiClient.get('/analytics/super-admin-dashboard/'),
  leaderboard: (params) => apiClient.get('/analytics/leaderboard/', { params }),
  attemptsCsv: (params) =>
    apiClient.get('/analytics/reports/attempts-csv/', { params, responseType: 'blob' }),
  attemptsXlsx: (params) =>
    apiClient.get('/analytics/reports/attempts-xlsx/', { params, responseType: 'blob' }),
  attemptPdf: (attemptId) =>
    apiClient.get(`/analytics/reports/attempt-pdf/${attemptId}/`, { responseType: 'blob' }),
};

export const notificationsApi = {
  list: () => apiClient.get('/notifications/'),
  unreadCount: () => apiClient.get('/notifications/unread-count/'),
  markRead: (id) => apiClient.post(`/notifications/${id}/mark-read/`),
  markAllRead: () => apiClient.post('/notifications/mark-all-read/'),
};

export const aiApi = {
  sqlToSparkSql: (code) =>
    apiClient.post('/ai/assistant/convert/sql-to-spark-sql/', { code }),
  sqlToPySpark: (code) =>
    apiClient.post('/ai/assistant/convert/sql-to-pyspark/', { code }),
  pythonToPySpark: (code) =>
    apiClient.post('/ai/assistant/convert/python-to-pyspark/', { code }),
  explain: (code, language = 'python') =>
    apiClient.post('/ai/assistant/explain/', { code, language }),
  chat: (messages) => apiClient.post('/ai/assistant/chat/', { messages }),
  history: () => apiClient.get('/ai/history/'),
  generateQuestionPaper: (payload) =>
    apiClient.post('/ai/question-paper/generate/', payload),
  importToExam: (payload) =>
    apiClient.post('/ai/question-paper/import-to-exam/', payload),
  extractNotesFile: (file) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.post('/ai/question-paper/extract-notes/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
    });
  },
};

export const auditApi = {
  list: (params) => apiClient.get('/audit/logs/', { params }),
};

/** ChatGPT-style MIT AI Chat (Llama-4) — separate from code-assistant aiApi */
export const mitChatApi = {
  send: (messages) => apiClient.post('/ai/mit-chat/send/', { messages }, { timeout: 120000 }),
};

/** MIT Code Studio playground — Python / SQL / PySpark / Java editor */
export const codeStudioApi = {
  run: (payload) => {
    const lang = payload?.language;
    const timeout = lang === 'pyspark' ? 180000 : 60000;
    return apiClient.post('/submissions/code-studio/run/', payload, { timeout });
  },
};

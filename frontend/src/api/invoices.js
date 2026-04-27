import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

export const profileApi = {
  get: () => api.get("/profile/"),
  update: (data) =>
    api.patch("/profile/", data, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export const clientsApi = {
  list: () => api.get("/clients/"),
  create: (data) => api.post("/clients/", data),
  update: (id, data) => api.put(`/clients/${id}/`, data),
  delete: (id) => api.delete(`/clients/${id}/`),
};

export const invoicesApi = {
  list: () => api.get("/invoices/"),
  get: (id) => api.get(`/invoices/${id}/`),
  create: (data) => api.post("/invoices/", data),
  update: (id, data) => api.put(`/invoices/${id}/`, data),
  delete: (id) => api.delete(`/invoices/${id}/`),
  nextNumber: () => api.get("/invoices/next_number/"),
  duplicate: (id) => api.post(`/invoices/${id}/duplicate/`),
  uploadLogo: (id, file) => {
    const fd = new FormData();
    fd.append("logo", file);
    return api.post(`/invoices/${id}/upload_logo/`, fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  downloadPdf: (id) =>
    api.get(`/invoices/${id}/pdf/`, { responseType: "blob" }),
};

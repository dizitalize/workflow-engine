import api from "./api";

export const workflowApi = {
  getWorkflows: async () => {
    const response = await api.get("/workflows");
    return response.data;
  },

  getWorkflow: async (id: string) => {
    const response = await api.get(`/workflows/${id}`);
    return response.data;
  },

  createWorkflow: async (data: { name: string; description?: string }) => {
    const response = await api.post("/workflows", data);
    return response.data;
  },

  updateWorkflow: async (id: string, data: { name?: string; description?: string }) => {
    const response = await api.put(`/workflows/${id}`, data);
    return response.data;
  },

  deleteWorkflow: async (id: string) => {
    await api.delete(`/workflows/${id}`);
  },

  validateWorkflow: async (id: string, definition: any) => {
    const response = await api.post(`/workflows/${id}/validate`, definition);
    return response.data;
  },

  createVersion: async (workflowId: string, definition: any) => {
    const response = await api.post(`/workflows/${workflowId}/versions`, { definition });
    return response.data;
  },

  getActiveVersion: async (workflowId: string) => {
    const response = await api.get(`/workflows/${workflowId}/versions/active`);
    return response.data;
  },

  activateVersion: async (workflowId: string, versionId: string) => {
    const response = await api.put(`/workflows/${workflowId}/versions/${versionId}/activate`);
    return response.data;
  },
};

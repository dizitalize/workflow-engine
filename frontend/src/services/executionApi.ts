import api from "./api";

export const executionApi = {
  getExecutions: async (workflowId?: string) => {
    const params = workflowId ? { workflowId } : {};
    const response = await api.get("/executions", { params });
    return response.data;
  },

  getExecution: async (id: string) => {
    const response = await api.get(`/executions/${id}`);
    return response.data;
  },

  executeWorkflow: async (workflowId: string, input: any = {}) => {
    const response = await api.post(`/executions/workflows/${workflowId}/execute`, { input });
    return response.data;
  },

  cancelExecution: async (id: string) => {
    const response = await api.post(`/executions/${id}/cancel`);
    return response.data;
  },
};

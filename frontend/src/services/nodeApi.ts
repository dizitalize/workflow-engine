import api from "./api";

export const nodeApi = {
  getNodes: async () => {
    const response = await api.get("/nodes");
    return response.data;
  },
};

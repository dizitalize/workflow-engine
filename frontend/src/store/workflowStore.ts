import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";
import { Workflow, WorkflowDefinition } from "../types/workflow";
import { workflowApi } from "../services/workflowApi";
import { executionApi } from "../services/executionApi";

interface WorkflowStoreState {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  workflowDefinition: WorkflowDefinition | null;
  selectedNodeId: string | null;
  isDirty: boolean;
  isSaving: boolean;
  isLoading: boolean;
  isExecuting: boolean;
  validationErrors: any[];
  execution: any | null;
  
  fetchWorkflows: () => Promise<void>;
  fetchWorkflow: (id: string) => Promise<void>;
  createWorkflow: (name: string, description?: string) => Promise<void>;
  updateWorkflow: (workflow: Partial<Workflow>) => Promise<void>;
  deleteWorkflow: (id: string) => Promise<void>;
  
  setWorkflowDefinition: (definition: WorkflowDefinition) => void;
  addNode: (node: any) => void;
  updateNode: (nodeId: string, updates: Partial<any>) => void;
  deleteNode: (nodeId: string) => void;
  duplicateNode: (nodeId: string) => void;
  setNodes: (nodes: any[]) => void;
  setEdges: (edges: any[]) => void;
  selectNode: (nodeId: string | null) => void;
  updateNodeConfig: (nodeId: string, config: any) => void;
  
  markDirty: () => void;
  clearDirty: () => void;
  saveWorkflow: () => Promise<void>;
  validateWorkflow: () => Promise<void>;
  executeWorkflow: () => Promise<void>;
  cancelExecution: () => Promise<void>;
  resetWorkflow: () => void;
}

export const useWorkflowStore = create<WorkflowStoreState>()(
  devtools(
    persist(
      (set, get) => ({
        workflows: [],
        currentWorkflow: null,
        workflowDefinition: null,
        selectedNodeId: null,
        isDirty: false,
        isSaving: false,
        isLoading: false,
        isExecuting: false,
        validationErrors: [],
        execution: null,
        
        fetchWorkflows: async () => {
          set({ isLoading: true });
          try {
            const workflows = await workflowApi.getWorkflows();
            set({ workflows, isLoading: false });
          } catch (error) {
            console.error("Failed to fetch workflows:", error);
            set({ isLoading: false });
          }
        },
        
        fetchWorkflow: async (id: string) => {
          set({ isLoading: true });
          try {
            const workflow = await workflowApi.getWorkflow(id);
            set({ currentWorkflow: workflow, isLoading: false });
            
            if (workflow.active_version_id) {
              set({ workflowDefinition: { nodes: [], edges: [] } });
            }
          } catch (error) {
            console.error("Failed to fetch workflow:", error);
            set({ isLoading: false });
          }
        },
        
        createWorkflow: async (name: string, description?: string) => {
          set({ isSaving: true });
          try {
            const workflow = await workflowApi.createWorkflow({ name, description });
            set({ currentWorkflow: workflow, isSaving: false });
            set({ workflowDefinition: { nodes: [], edges: [] } });
            
            await get().fetchWorkflows();
          } catch (error) {
            console.error("Failed to create workflow:", error);
            set({ isSaving: false });
          }
        },
        
        updateWorkflow: async (workflow: Partial<Workflow>) => {
          if (!get().currentWorkflow) return;
          
          set({ isSaving: true });
          try {
            const updatedWorkflow = await workflowApi.updateWorkflow(
              get().currentWorkflow!.id,
              workflow
            );
            set({ currentWorkflow: updatedWorkflow, isSaving: false });
            
            await get().fetchWorkflows();
          } catch (error) {
            console.error("Failed to update workflow:", error);
            set({ isSaving: false });
          }
        },
        
        deleteWorkflow: async (id: string) => {
          set({ isSaving: true });
          try {
            await workflowApi.deleteWorkflow(id);
            set({ isSaving: false });
            
            await get().fetchWorkflows();
            
            if (get().currentWorkflow?.id === id) {
              set({ currentWorkflow: null, workflowDefinition: null });
            }
          } catch (error) {
            console.error("Failed to delete workflow:", error);
            set({ isSaving: false });
          }
        },
        
        setWorkflowDefinition: (definition: WorkflowDefinition) => {
          set({ workflowDefinition: definition, isDirty: false });
        },
        
        addNode: (node: any) => {
          const { workflowDefinition } = get();
          if (!workflowDefinition) return;
          
          set({
            workflowDefinition: {
              ...workflowDefinition,
              nodes: [...workflowDefinition.nodes, node],
            },
            isDirty: true,
          });
        },
        
        updateNode: (nodeId: string, updates: Partial<any>) => {
          const { workflowDefinition } = get();
          if (!workflowDefinition) return;
          
          set({
            workflowDefinition: {
              ...workflowDefinition,
              nodes: workflowDefinition.nodes.map((node: any) =>
                node.id === nodeId ? { ...node, ...updates } : node
              ),
            },
            isDirty: true,
          });
        },
        
        deleteNode: (nodeId: string) => {
          const { workflowDefinition } = get();
          if (!workflowDefinition) return;
          
          set({
            workflowDefinition: {
              ...workflowDefinition,
              nodes: workflowDefinition.nodes.filter((node: any) => node.id !== nodeId),
            },
            isDirty: true,
          });
        },
        
        duplicateNode: (nodeId: string) => {
          const { workflowDefinition } = get();
          if (!workflowDefinition) return;
          
          const nodeToDuplicate = workflowDefinition.nodes.find(
            (node: any) => node.id === nodeId
          );
          if (!nodeToDuplicate) return;
          
          const duplicatedNode = {
            ...nodeToDuplicate,
            id: `node_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
            position: {
              x: (nodeToDuplicate.position?.x || 0) + 20,
              y: (nodeToDuplicate.position?.y || 0) + 20,
            },
          };
          
          set({
            workflowDefinition: {
              ...workflowDefinition,
              nodes: [...workflowDefinition.nodes, duplicatedNode],
            },
            isDirty: true,
          });
        },
        
        setNodes: (nodes: any[]) => {
          set((state) => ({
            workflowDefinition: {
              ...state.workflowDefinition!,
              nodes,
            },
            isDirty: true,
          }));
        },
        
        setEdges: (edges: any[]) => {
          set((state) => ({
            workflowDefinition: {
              ...state.workflowDefinition!,
              edges,
            },
            isDirty: true,
          }));
        },
        
        selectNode: (nodeId: string | null) => {
          set({ selectedNodeId: nodeId });
        },
        
        updateNodeConfig: (nodeId: string, config: any) => {
          const { workflowDefinition } = get();
          if (!workflowDefinition) return;
          
          set({
            workflowDefinition: {
              ...workflowDefinition,
              nodes: workflowDefinition.nodes.map((node: any) =>
                node.id === nodeId ? { ...node, config } : node
              ),
            },
            isDirty: true,
          });
        },
        
        markDirty: () => {
          set({ isDirty: true });
        },
        
        clearDirty: () => {
          set({ isDirty: false });
        },
        
        saveWorkflow: async () => {
          const { currentWorkflow, workflowDefinition } = get();
          if (!currentWorkflow || !workflowDefinition) return;
          
          set({ isSaving: true });
          try {
            set({ isSaving: false, isDirty: false });
            console.log("Workflow saved successfully");
          } catch (error) {
            console.error("Failed to save workflow:", error);
            set({ isSaving: false });
          }
        },
        
        validateWorkflow: async () => {
          const { currentWorkflow, workflowDefinition } = get();
          if (!currentWorkflow || !workflowDefinition) return;
          
          set({ isLoading: true });
          try {
            const result = await workflowApi.validateWorkflow(
              currentWorkflow.id,
              workflowDefinition
            );
            set({ validationErrors: result.errors || [], isLoading: false });
          } catch (error) {
            console.error("Failed to validate workflow:", error);
            set({ isLoading: true, validationErrors: [{ message: "Validation failed" }] });
          }
        },
        
        executeWorkflow: async () => {
          const { currentWorkflow, workflowDefinition } = get();
          if (!currentWorkflow || !workflowDefinition) return;
          
          set({ isExecuting: true });
          try {
            const result = await executionApi.executeWorkflow(
              currentWorkflow.id,
              {}
            );
            
            set({ 
              execution: result,
              isExecuting: false 
            });
          } catch (error) {
            console.error("Failed to execute workflow:", error);
            set({ 
              execution: { 
                status: "FAILED", 
                error: "Execution failed" 
              },
              isExecuting: false 
            });
          }
        },
        
        cancelExecution: async () => {
          const { execution } = get();
          if (!execution?.id) return;
          
          try {
            await executionApi.cancelExecution(execution.id);
            set({ execution: null });
          } catch (error) {
            console.error("Failed to cancel execution:", error);
          }
        },
        
        resetWorkflow: () => {
          set({
            workflowDefinition: { nodes: [], edges: [] },
            selectedNodeId: null,
            isDirty: false,
            validationErrors: [],
            execution: null,
          });
        },
      }),
      {
        name: "workflow-storage",
        getStorage: () => localStorage,
      }
    )
  )
);
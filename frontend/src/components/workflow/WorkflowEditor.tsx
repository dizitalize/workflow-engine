"use client";

import React, { useEffect } from "react";
import { useWorkflowStore } from "../../store/workflowStore";
import WorkflowToolbar from "./WorkflowToolbar";
import WorkflowCanvas from "./WorkflowCanvas";
import NodeLibrary from "./NodeLibrary";
import NodeInspector from "./NodeInspector";
import EmptyWorkflow from "./EmptyWorkflow";
import "./WorkflowEditor.css";

const WorkflowEditor = () => {
  const {
    currentWorkflow,
    isLoading,
    workflows,
    fetchWorkflows,
  } = useWorkflowStore();

  // Load workflows when component mounts
  useEffect(() => {
    if (workflows.length === 0) {
      fetchWorkflows();
    }
  }, [fetchWorkflows, workflows.length]);

  if (isLoading && workflows.length === 0) {
    return (
      <div className="workflow-editor-loading">
        <p>Loading workflows...</p>
      </div>
    );
  }

  // If no workflows exist, show a message to create one
  if (workflows.length === 0) {
    return (
      <div className="workflow-editor-empty">
        <h2>No workflows found</h2>
        <p>Create your first workflow to get started.</p>
        {/* In a real implementation, we would have a button to create a new workflow */}
      </div>
    );
  }

  // If we have a current workflow, show the editor
  if (currentWorkflow) {
    return (
      <div className="workflow-editor">
        <WorkflowToolbar />
        <div className="workflow-editor-body">
          <div className="workflow-editor-sidebar">
            <NodeLibrary />
          </div>
          <div className="workflow-editor-main">
            <WorkflowCanvas />
            <NodeInspector />
          </div>
        </div>
      </div>
    );
  }

  // Fallback - show workflow list
  return (
    <div className="workflow-editor">
      <WorkflowToolbar />
      <div className="workflow-editor-body">
        <div className="workflow-editor-sidebar">
          <NodeLibrary />
        </div>
        <div className="workflow-editor-main">
          <h2>Select a workflow to edit</h2>
          <p>Choose a workflow from the list above to begin editing.</p>
        </div>
      </div>
    </div>
  );
};

export default WorkflowEditor;
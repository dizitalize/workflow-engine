"use client";

import React from "react";
import { useWorkflowStore } from "@/store/workflowStore";
import { Link } from "next/link";

const WorkflowToolbar = () => {
  const {
    currentWorkflow,
    execution,
    isSaving,
    isLoading,
    isExecuting,
    validationErrors,
    fetchWorkflows,
    validateWorkflow,
    executeWorkflow,
    resetWorkflow,
  } = useWorkflowStore();

  const handleValidate = async () => {
    await validateWorkflow();
    // In a real implementation, we would show a toast or notification
    if (validationErrors.length === 0) {
      console.log("Workflow is valid");
    } else {
      console.log("Workflow has validation errors");
    }
  };

  const handleExecute = async () => {
    await executeWorkflow();
  };

  const handleReset = async () => {
    await resetWorkflow();
    await fetchWorkflows(); // Refresh workflow list
  };

  return (
    <div className="workflow-toolbar">
      <div className="toolbar-left">
        <Link href="/workflows">
          <a>← Workflows</a>
        </Link>
      </div>
      <div className="toolbar-center">
        {currentWorkflow && (
          <div className="workflow-title">
            <h2>{currentWorkflow.name}</h2>
            {currentWorkflow.description && (
              <p className="workflow-description">{currentWorkflow.description}</p>
            )}
          </div>
        )}
      </div>
      <div className="toolbar-right">
        <div className="toolbar-actions">
          {!isLoading && !isSaving && !isExecuting && (
            <button onClick={handleValidate} disabled={isLoading}>
              Validate
            </button>
          )}
          {!isLoading && !isSaving && !isExecuting && (
            <button onClick={handleExecute} disabled={isExecuting}>
              Test
            </button>
          )}
          {!isSaving && (
            <button onClick={() => {/* Save logic would go here */}} disabled={isSaving}>
              Save
            </button>
          )}
          {!isLoading && (
            <button onClick={handleReset} disabled={isLoading}>
              Reset
            </button>
          )}
        </div>
        
        {/* Status indicators */}
        {isSaving && <span className="status-indicator saving">Saving...</span>}
        {isLoading && <span className="status-indicator loading">Loading...</span>}
        {isExecuting && <span className="status-indicator running">Running...</span>}
        {!isExecuting && execution && execution.status === "SUCCESS" && (
          <span className="status-indicator success">Success</span>
        )}
        {!isExecuting && execution && execution.status === "FAILED" && (
          <span className="status-indicator error">Error</span>
        )}
      </div>
    </div>
  );
};

export default WorkflowToolbar;
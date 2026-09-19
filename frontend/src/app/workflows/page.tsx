"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useWorkflowStore } from "@/store/workflowStore";

const WorkflowsPage = () => {
  const { workflows, fetchWorkflows, deleteWorkflow, createWorkflow } = useWorkflowStore();
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState("");
  const [newWorkflowDescription, setNewWorkflowDescription] = useState("");

  useEffect(() => {
    fetchWorkflows().then(() => setIsLoading(false));
  }, [fetchWorkflows]);

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this workflow?")) {
      setDeletingId(id);
      await deleteWorkflow(id);
      setDeletingId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWorkflowName.trim()) return;
    
    await createWorkflow(newWorkflowName.trim(), newWorkflowDescription.trim());
    setShowCreateModal(false);
    setNewWorkflowName("");
    setNewWorkflowDescription("");
  };

  if (isLoading) {
    return (
      <div className="workflows-page">
        <div className="workflows-header">
          <h1>Workflows</h1>
        </div>
        <div className="workflows-loading">Loading workflows...</div>
      </div>
    );
  }

  return (
    <div className="workflows-page">
      <div className="workflows-header">
        <h1>Workflows</h1>
        <div className="workflows-new-workflow">
          <button
            onClick={() => setShowCreateModal(true)}
            className="workflow-btn create"
          >
            + New Workflow
          </button>
        </div>
      </div>

      {workflows.length === 0 ? (
        <div className="workflows-empty">
          <h2>No workflows yet</h2>
          <p>Create your first workflow to start building automations.</p>
          <button onClick={() => setShowCreateModal(true)} className="workflow-btn create">
            + Create Workflow
          </button>
        </div>
      ) : (
        <div className="workflows-list">
          {workflows.map((workflow: any) => (
            <div key={workflow.id} className="workflow-card">
              <div className="workflow-card-content">
                <div className="workflow-card-title">
                  <Link href={`/workflow/${workflow.id}`}>
                    <a>{workflow.name}</a>
                  </Link>
                  {workflow.description && (
                    <p className="workflow-card-description">{workflow.description}</p>
                  )}
                </div>
                <div className="workflow-card-meta">
                  <span className="workflow-card-status">{workflow.status}</span>
                  <span className="workflow-card-updated">
                    Updated {new Date(workflow.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="workflow-card-actions">
                  <Link href={`/workflow/${workflow.id}`}>
                    <button className="workflow-btn view">Edit</button>
                  </Link>
                  <button
                    className={`workflow-btn delete ${deletingId === workflow.id ? "delete-confirm" : ""}`}
                    onClick={() => handleDelete(workflow.id)}
                    disabled={deletingId !== null && deletingId !== workflow.id}
                  >
                    {deletingId === workflow.id ? "Confirm?" : "Delete"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Workflow</h2>
            <form onSubmit={handleCreate}>
              <div className="modal-field">
                <label htmlFor="name">Name *</label>
                <input
                  id="name"
                  type="text"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  placeholder="My Workflow"
                  required
                  autoFocus
                />
              </div>
              <div className="modal-field">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  value={newWorkflowDescription}
                  onChange={(e) => setNewWorkflowDescription(e.target.value)}
                  placeholder="What does this workflow do?"
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="workflow-btn" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="workflow-btn create">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowsPage;
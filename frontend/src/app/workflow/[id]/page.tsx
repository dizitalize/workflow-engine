"use client";

import { useEffect } from "react";
import { useWorkflowStore } from "@/store/workflowStore";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";

interface WorkflowDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function WorkflowDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = await params;
  const { fetchWorkflow, currentWorkflow } = useWorkflowStore();

  useEffect(() => {
    if (resolvedParams.id) {
      fetchWorkflow(resolvedParams.id);
    }
  }, [fetchWorkflow, resolvedParams.id]);

  if (currentWorkflow) {
    return (
      <div className="workflow-detail-page">
        <WorkflowEditor />
      </div>
    );
  }

  return (
    <div className="workflow-detail-page">
      <div className="workflow-detail-loading">
        <p>Loading workflow...</p>
      </div>
    </div>
  );
}
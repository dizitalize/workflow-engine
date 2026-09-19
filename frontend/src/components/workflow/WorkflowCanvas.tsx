"use client";

import ReactFlow, { Background, Controls, MiniMap, Node, Edge, Position } from "reactflow";
import { useWorkflowStore } from "../../store/workflowStore";
import { WorkflowNodeDefinition, WorkflowEdgeDefinition } from "@/types/workflow";

const WorkflowCanvas = () => {
  const { workflowDefinition } = useWorkflowStore();

  // Transform workflow nodes to React Flow nodes
  const reactFlowNodes: Node[] = (workflowDefinition?.nodes || []).map((node: WorkflowNodeDefinition) => ({
    id: node.id,
    type: "custom",
    position: node.position || { x: 0, y: 0 },
    data: {
      label: node.label || node.name || node.type,
      type: node.type,
      status: node.config?.status,
    },
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
  }));

  // Transform workflow edges to React Flow edges
  const reactFlowEdges: Edge[] = (workflowDefinition?.edges || []).map((edge: WorkflowEdgeDefinition) => ({
    id: `${edge.source}-${edge.target}`,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.source_handle,
    targetHandle: edge.target_handle,
    type: "smoothstep",
    animated: false,
  }));

  return (
    <div className="workflow-canvas">
      <ReactFlow
        nodes={reactFlowNodes}
        edges={reactFlowEdges}
        nodeTypes={{
          custom: ({ data }) => (
            <div className="workflow-node">
              <div className="workflow-node-header">
                <div className="workflow-node-type">{data.type}</div>
                <div className="workflow-node-connector"></div>
              </div>
              <div className="workflow-node-content">
                <div className="workflow-node-label">{data.label}</div>
                {data.status && (
                  <div className={`workflow-node-status ${data.status.toLowerCase()}`}>
                    {data.status}
                  </div>
                )}
              </div>
              <div className="workflow-node-footer">
                <div className="workflow-node-connector"></div>
              </div>
            </div>
          ),
        }}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
};

export default WorkflowCanvas;
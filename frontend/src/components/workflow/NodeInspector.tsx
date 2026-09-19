"use client";

import React from "react";
import { useWorkflowStore } from "../../store/workflowStore";

const NodeInspector = () => {
  const { selectedNodeId, workflowDefinition, updateNodeConfig } = useWorkflowStore();

  if (!selectedNodeId || !workflowDefinition) {
    return (
      <div className="node-inspector">
        <h3>Node Inspector</h3>
        <p>Select a node to configure it</p>
      </div>
    );
  }

  const node = workflowDefinition.nodes.find((n: any) => n.id === selectedNodeId);
  if (!node) {
    return (
      <div className="node-inspector">
        <h3>Node Inspector</h3>
        <p>Node not found</p>
      </div>
    );
  }

  const handleConfigChange = (key: string, value: any) => {
    updateNodeConfig(selectedNodeId, {
      ...node.config,
      [key]: value,
    });
  };

  return (
    <div className="node-inspector">
      <h3>Node Inspector</h3>
      <div className="node-inspector-header">
        <h4>{node.name}</h4>
        <p className="node-inspector-type">{node.type}</p>
      </div>
      <div className="node-inspector-content">
        <div className="node-config-section">
          <h4>Configuration</h4>
          <pre>{JSON.stringify(node.config, null, 2)}</pre>
          <div className="node-config-actions">
            <button onClick={() => handleConfigChange("test", "updated value")}>
              Update Config
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeInspector;


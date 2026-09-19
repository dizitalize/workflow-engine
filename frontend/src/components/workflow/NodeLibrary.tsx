"use client";

import React, { useEffect, useState } from "react";
import { useWorkflowStore } from "@/store/workflowStore";
import { nodeApi } from "@/services/nodeApi";
import "./NodeLibrary.css";

const NodeLibrary = () => {
  const { addNode } = useWorkflowStore();
  const [nodes, setNodes] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>("");

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        setLoading(true);
        const nodeData = await nodeApi.getNodes();
        setNodes(nodeData);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch nodes:", error);
        setLoading(false);
        // Fallback nodes
        setNodes([
          { id: "trigger.manual", name: "Manual Trigger", type: "trigger.manual", category: "Triggers" },
          { id: "transform.set", name: "Set", type: "transform.set", category: "Transform" },
          { id: "utility.log", name: "Log", type: "utility.log", category: "Utility" },
          { id: "logic.if", name: "IF", type: "logic.if", category: "Logic" },
          { id: "utility.http_request", name: "HTTP Request", type: "utility.http_request", category: "Utility" },
        ]);
      }
    };

    fetchNodes();
  }, [addNode]);

  const filteredNodes = nodes.filter((node: any) =>
    node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddNode = (nodeType: string) => {
    const position = {
      x: 100 + Math.floor(Math.random() * 300),
      y: 100 + Math.floor(Math.random() * 200),
    };

    addNode({
      id: `node_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      type: nodeType,
      version: 1,
      position,
      config: {},
    });
  };

  if (loading) {
    return (
      <div className="node-library">
        <div className="node-library-header">
          <h3>Node Library</h3>
          <input
            type="text"
            placeholder="Search nodes..."
            className="node-search-input"
            disabled
          />
        </div>
        <div className="node-library-loading">Loading nodes...</div>
      </div>
    );
  }

  // Group nodes by category
  const groupedNodes = filteredNodes.reduce((acc: Record<string, any[]>, node: any) => {
    if (!acc[node.category]) {
      acc[node.category] = [];
    }
    acc[node.category].push(node);
    return acc;
  }, {});

  if (filteredNodes.length === 0) {
    return (
      <div className="node-library">
        <div className="node-library-header">
          <h3>Node Library</h3>
          <input
            type="text"
            placeholder="Search nodes..."
            className="node-search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="node-library-empty">
          <p>No nodes found matching "{searchTerm}"</p>
        </div>
      </div>
    );
  }

  return (
    <div className="node-library">
      <div className="node-library-header">
        <h3>Node Library</h3>
        <input
          type="text"
          placeholder="Search nodes..."
          className="node-search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      {Object.entries(groupedNodes).map(([category, nodes]) => (
        <div key={category} className="node-category">
          <h4>{category}</h4>
          <div className="node-list">
            {nodes.map((node: any) => (
              <div
                key={node.id}
                className="node-item"
                onClick={() => handleAddNode(node.type)}
              >
                <div className="node-item-icon">
                  <span className="node-type-tag">{node.type.split(".").pop()}</span>
                </div>
                <div className="node-item-info">
                  <div className="node-item-name">{node.name}</div>
                  <div className="node-item-type">{node.type}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default NodeLibrary;


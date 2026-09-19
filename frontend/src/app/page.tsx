import Link from "next/link";

export default function Home() {
  return (
    <div style={{ 
      minHeight: "100vh", 
      display: "flex", 
      flexDirection: "column", 
      alignItems: "center", 
      justifyContent: "center",
      background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
      padding: "2rem"
    }}>
      <div style={{
        maxWidth: "800px",
        textAlign: "center",
        background: "white",
        padding: "3rem",
        borderRadius: "16px",
        boxShadow: "0 10px 40px rgba(0,0,0,0.1)"
      }}>
        <h1 style={{
          fontSize: "3rem",
          fontWeight: 700,
          color: "#1976d2",
          marginBottom: "1rem"
        }}>
          Workflow Engine
        </h1>
        <p style={{
          fontSize: "1.25rem",
          color: "#666",
          marginBottom: "2rem",
          lineHeight: 1.6
        }}>
          A visual workflow automation engine for building and executing automated workflows.
        </p>
        <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
          <Link href="/workflows" style={{
            display: "inline-block",
            padding: "0.875rem 2rem",
            backgroundColor: "#1976d2",
            color: "white",
            textDecoration: "none",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "1rem",
            transition: "background-color 0.2s"
          }}>
            View Workflows
          </Link>
          <Link href="/workflows" style={{
            display: "inline-block",
            padding: "0.875rem 2rem",
            backgroundColor: "transparent",
            color: "#1976d2",
            textDecoration: "none",
            border: "2px solid #1976d2",
            borderRadius: "8px",
            fontWeight: 600,
            fontSize: "1rem",
            transition: "background-color 0.2s"
          }}>
            Create Workflow
          </Link>
        </div>
        <div style={{ marginTop: "3rem", paddingTop: "2rem", borderTop: "1px solid #eee" }}>
          <h3 style={{ marginBottom: "1.5rem", color: "#333" }}>Features</h3>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1.5rem",
            textAlign: "left"
          }}>
            <div style={{ padding: "1rem" }}>
              <h4 style={{ color: "#1976d2", marginBottom: "0.5rem" }}>Visual Editor</h4>
              <p style={{ color: "#666", fontSize: "0.9rem" }}>Drag-and-drop workflow builder with React Flow</p>
            </div>
            <div style={{ padding: "1rem" }}>
              <h4 style={{ color: "#1976d2", marginBottom: "0.5rem" }}>Node Library</h4>
              <p style={{ color: "#666", fontSize: "0.9rem" }}>Extensible node system with categories</p>
            </div>
            <div style={{ padding: "1rem" }}>
              <h4 style={{ color: "#1976d2", marginBottom: "0.5rem" }}>Execution Engine</h4>
              <p style={{ color: "#666", fontSize: "0.9rem" }}>Run and monitor workflow executions</p>
            </div>
            <div style={{ padding: "1rem" }}>
              <h4 style={{ color: "#1976d2", marginBottom: "0.5rem" }}>TypeScript</h4>
              <p style={{ color: "#666", fontSize: "0.9rem" }}>Full type safety across the stack</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
import { useState, useEffect } from 'react'
import './App.css'

interface AuditLog {
  id: number
  agent_id: number
  action: string
  tool_name: string
  status: string
  reason: string | null
  cost: number
  created_at: string
}

interface ApprovalRequest {
  id: number
  agent_id: number
  action: string
  tool_name: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameters: any
  status: string
  created_at: string
}

interface WorkflowCheckpoint {
  id: number
  agent_id: number
  tool_name: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  parameters: any
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  agent_state: any
  created_at: string
}

interface Agent {
  id: number
  name: string
  description: string
  trust_score: number
  is_active: boolean
}

const API_BASE = "http://127.0.0.1:8000"

function App() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([])
  const [agents, setAgents] = useState<Agent[]>([])

  const [workflows, setWorkflows] = useState<string[]>([])
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null)
  const [checkpoints, setCheckpoints] = useState<WorkflowCheckpoint[]>([])

  const fetchData = async () => {
    try {
      const logsRes = await fetch(`${API_BASE}/v1/dashboard/logs`)
      const logsData = await logsRes.json()
      setLogs(logsData)

      const approvalsRes = await fetch(`${API_BASE}/v1/dashboard/approvals`)
      const approvalsData = await approvalsRes.json()
      setApprovals(approvalsData)
      
      const agentsRes = await fetch(`${API_BASE}/v1/dashboard/agents`)
      const agentsData = await agentsRes.json()
      setAgents(agentsData)

      const workflowsRes = await fetch(`${API_BASE}/v1/proxy/workflows`)
      const workflowsData = await workflowsRes.json()
      setWorkflows(workflowsData)
    } catch (e) {
      console.error("Failed to fetch dashboard data", e)
    }
  }

  const fetchCheckpoints = async (workflowId: string) => {
    try {
      const res = await fetch(`${API_BASE}/v1/proxy/workflows/${workflowId}/checkpoints`)
      const data = await res.json()
      setCheckpoints(data)
      setSelectedWorkflow(workflowId)
    } catch (e) {
      console.error("Failed to fetch checkpoints", e)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchData()
    // Poll every 3 seconds for updates
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [])

  const handleApproval = async (id: number, status: 'approved' | 'rejected') => {
    try {
      await fetch(`${API_BASE}/v1/proxy/approval/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      fetchData() // refresh immediately
    } catch (e) {
      console.error(`Failed to ${status} request`, e)
    }
  }

  return (
    <div className="dashboard-container">
      <header>
        <h1>🦀 CrabsHold Governance Dashboard</h1>
        <p>Identity-Aware Agent Gateway & Execution Proxy</p>
      </header>
      
      <main>
        <section className="agents-section">
          <h2>Active Agents & Trust Scores</h2>
          <div className="cards-container">
            {agents.map(agent => (
              <div key={agent.id} className={`agent-card ${agent.trust_score < 50 ? 'strict-mode' : ''}`}>
                <div className="agent-header">
                  <strong>#{agent.id} {agent.name}</strong>
                  {agent.trust_score < 50 && <span className="strict-badge">STRICT MODE</span>}
                </div>
                <div className="agent-body">
                  <p>{agent.description}</p>
                  <div className="trust-meter">
                    <div className="trust-fill" style={{ 
                      width: `${agent.trust_score}%`,
                      backgroundColor: agent.trust_score < 50 ? '#e74c3c' : (agent.trust_score < 80 ? '#f39c12' : '#2ecc71')
                    }}></div>
                  </div>
                  <p className="trust-text">Trust Score: <strong>{agent.trust_score}</strong> / 100</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {approvals.length > 0 && (
          <section className="approvals-section">
            <h2>⚠️ Pending Human Approvals ({approvals.length})</h2>
            <div className="cards-container">
              {approvals.map(req => (
                <div key={req.id} className="approval-card">
                  <div className="card-header">
                    <strong>Agent #{req.agent_id}</strong> requested <code>{req.action}</code>
                  </div>
                  <div className="card-body">
                    <p><strong>Tool:</strong> {req.tool_name}</p>
                    <p><strong>Params:</strong> {JSON.stringify(req.parameters)}</p>
                    <p><strong>Time:</strong> {new Date(req.created_at).toLocaleTimeString()}</p>
                  </div>
                  <div className="card-actions">
                    <button className="btn approve" onClick={() => handleApproval(req.id, 'approved')}>Approve</button>
                    <button className="btn reject" onClick={() => handleApproval(req.id, 'rejected')}>Reject</button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="time-travel-section">
          <h2>⏳ Workflow Time Travel (Checkpoints)</h2>
          <div className="workflow-controls" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
            {workflows.map(wf => (
              <button 
                key={wf} 
                className={`btn ${selectedWorkflow === wf ? 'approve' : ''}`}
                onClick={() => fetchCheckpoints(wf)}
              >
                Run {wf.substring(0, 8)}...
              </button>
            ))}
            {workflows.length === 0 && <p>No workflows run yet.</p>}
          </div>

          {selectedWorkflow && (
            <div className="checkpoints-timeline">
              <h3>Checkpoints for Run {selectedWorkflow.substring(0, 8)}...</h3>
              <div className="timeline-container">
                {checkpoints.map((cp, idx) => (
                  <div key={cp.id} className="checkpoint-card" style={{ background: '#f8f9fa', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', borderLeft: '4px solid #3498db' }}>
                    <div className="checkpoint-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <strong>Step {idx + 1}: {cp.tool_name}</strong>
                      <span style={{ fontSize: '0.85rem', color: '#7f8c8d' }}>{new Date(cp.created_at).toLocaleTimeString()}</span>
                    </div>
                    <div className="checkpoint-body">
                      <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem' }}><strong>Parameters:</strong> <code>{JSON.stringify(cp.parameters)}</code></p>
                      <details>
                        <summary style={{ cursor: 'pointer', color: '#2980b9', fontWeight: 600 }}>View Agent Brain State</summary>
                        <pre className="brain-state" style={{ background: '#2c3e50', color: '#ecf0f1', padding: '1rem', borderRadius: '4px', overflowX: 'auto', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                          {JSON.stringify(cp.agent_state, null, 2)}
                        </pre>
                      </details>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="logs-section">
          <h2>Recent Audit Logs</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Agent</th>
                  <th>Action</th>
                  <th>Tool</th>
                  <th>Status</th>
                  <th>Reason</th>
                  <th>Cost</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id} className={`status-${log.status}`}>
                    <td>{log.id}</td>
                    <td>Agent #{log.agent_id}</td>
                    <td><code>{log.action}</code></td>
                    <td><code>{log.tool_name}</code></td>
                    <td>
                      <span className={`badge ${log.status}`}>
                        {log.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{log.reason || "-"}</td>
                    <td>{log.cost}</td>
                    <td>{new Date(log.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={8} style={{textAlign: 'center', padding: '2rem'}}>No logs yet. Run an agent!</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App

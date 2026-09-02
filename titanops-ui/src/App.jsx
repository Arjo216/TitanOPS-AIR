import React, { useState, useEffect, useRef } from 'react';
import { Crosshair, ShieldAlert, Cpu, Flame, Power, Radio, Target, Activity } from 'lucide-react';
import './App.css';

function App() {
  const [systemStatus, setSystemStatus] = useState("AWAITING UPLINK");
  const [threatCount, setThreatCount] = useState(0);
  const [logs, setLogs] = useState([]);
  const [videoFrame, setVideoFrame] = useState(null);
  const [mapFrame, setMapFrame] = useState(null);
  
  // Tactical State Controls (Decoupled)
  const [autoPilot, setAutoPilot] = useState(false);
  const [isStriking, setIsStriking] = useState(false);
  
  const ws = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    const addLog = (msg, type = 'normal') => {
      setLogs(prev => [...prev.slice(-20), { time: new Date().toLocaleTimeString(), msg, type }]);
    };
    addLog("TITAN_OPS AIR WEAPONIZED C2 INITIALIZED.");

    const currentHost = window.location.hostname;
    const wsUrl = currentHost === 'localhost' ? "ws://localhost:8765" : `wss://${currentHost.replace('5173', '8765')}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => addLog("✅ BIDIRECTIONAL UPLINK SECURED.", "strike");
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "TELEMETRY") {
        setSystemStatus(data.status);
        setThreatCount(data.threats);
        if (data.video_frame) setVideoFrame(data.video_frame);
        if (data.map_frame) setMapFrame(data.map_frame);
        
        let logType = 'normal';
        if (data.status === "TARGET_LOCK") logType = 'threat';
        if (data.status === "STRIKE_EXECUTED") { logType = 'strike'; setIsStriking(false); }
        
        addLog(data.log_msg, logType);
      }
    };
    return () => ws.current.close();
  }, []);

  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  // --- DECOUPLED COMMAND PROTOCOLS ---
  const sendCommand = (cmd) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ command: cmd }));
    }
  };

  const engageAutopilot = () => {
    setAutoPilot(true);
    sendCommand("ENGAGE_AUTOPILOT");
  };

  const engageManualOverride = () => {
    setAutoPilot(false);
    sendCommand("MANUAL_OVERRIDE");
  };

  const executeManualStrike = () => {
    setIsStriking(true);
    sendCommand("FIRE_SWARM");
  };

  return (
    <div className="dashboard-container">
      
      {/* HEADER: Master Autopilot Control */}
      <div className="header panel">
        <div className="title-box">
          <h1 style={{color: autoPilot ? 'var(--neon-green)' : 'var(--neon-yellow)'}}>TITAN_OPS AIR</h1>
          <span style={{color: '#888', fontSize: '0.85rem'}}>OVERWATCH NEXUS ARCHITECTURE</span>
        </div>
        
        <div style={{display: 'flex', alignItems: 'center', gap: '20px'}}>
          <div style={{textAlign: 'right'}}>
             <div style={{color: 'var(--neon-purple)', fontWeight: 'bold'}}>NETWORK STATUS: {systemStatus}</div>
          </div>
          {/* THE MASTER AI TOGGLE */}
          <button 
            onClick={engageAutopilot} 
            className={`master-mode-btn ${autoPilot ? 'active' : ''}`}
          >
            <Cpu size={16} style={{verticalAlign:'middle', marginRight:'5px'}}/>
            AI AUTOPILOT {autoPilot ? 'ENGAGED' : 'STANDBY'}
          </button>
        </div>
      </div>

      {/* LEFT PANEL: Swarm Assets & Weapons Bay */}
      <div className="panel">
        <h3 style={{marginTop: 0, borderBottom: '1px solid #333', paddingBottom: '10px', color: 'var(--neon-cyan)'}}>
          <Radio size={18} style={{verticalAlign:'middle', marginRight:'5px'}}/> SWARM ASSETS
        </h3>
        
        <div style={{margin: '10px 0'}}>
          <div style={{color: '#fff', fontWeight: 'bold'}}>SENTINEL_UAV_01 (OVERWATCH)</div>
          <div style={{fontSize: '0.8rem', color: 'var(--neon-cyan)'}}>RADAR: YOLO11 GPU LINKED</div>
        </div>
        <div style={{margin: '10px 0'}}>
          <div style={{color: '#fff', fontWeight: 'bold'}}>INTERCEPTOR_SWARM (PAYLOAD)</div>
          <div style={{fontSize: '0.8rem', color: 'var(--neon-cyan)'}}>STATUS: ARMED & READY</div>
        </div>
        
        <h3 style={{color: threatCount > 0 ? 'var(--neon-red)' : 'var(--neon-cyan)', margin: '20px 0 10px 0'}}>
          <ShieldAlert size={18} style={{verticalAlign:'middle', marginRight:'5px'}}/> THREATS LOGGED: {threatCount}
        </h3>

        {/* 🚀 DECOUPLED WEAPONS CONTROL DECK */}
        <div className="weapons-bay">
          <div style={{fontSize: '0.8rem', color: '#888', marginBottom: '10px', textAlign: 'center'}}>TACTICAL WEAPONS CONTROL</div>
          
          <button 
            onClick={engageManualOverride} 
            className={`override-btn ${!autoPilot ? 'active' : ''}`}
          >
            <Power size={14} style={{verticalAlign:'middle', marginRight:'5px'}}/> 
            {!autoPilot ? "MANUAL OVERRIDE ACTIVE" : "REQUEST MANUAL CONTROL"}
          </button>

          <button 
            onClick={executeManualStrike} 
            className="fire-btn" 
            disabled={autoPilot || threatCount === 0 || isStriking}
          >
            <Flame size={18} style={{verticalAlign:'middle', marginRight:'5px'}}/> NEUTRALIZE TARGET
          </button>
        </div>
      </div>

      {/* CENTER PANEL: Optical Targeting */}
      <div className={`panel center-feed ${systemStatus === "TARGET_LOCK" || systemStatus === "STRIKE_EXECUTED" ? 'engaged' : ''}`}>
        <div style={{position: 'absolute', top: '10px', left: '10px', fontSize: '0.8rem', background: 'rgba(0,0,0,0.8)', padding: '6px', zIndex: 10, border: '1px solid #555', color: 'var(--neon-cyan)'}}>
          <Target size={14} style={{verticalAlign: 'middle', marginRight: '5px', color: 'red'}}/> AERIAL OPTICAL UPLINK
        </div>
        {videoFrame ? (
            /* 🚀 SILVER BULLET FIX: Position Absolute stops grid stretching */
            <img src={`data:image/jpeg;base64,${videoFrame}`} alt="YOLO Feed" style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'cover', zIndex: 0}} />
        ) : (
            <div style={{opacity: 0.3, textAlign: 'center', margin: 'auto', zIndex: 1}}>
                <Activity size={48} className="animate-pulse" style={{margin: '0 auto 10px auto', display: 'block'}} />
                <p>INITIALIZING CAMERA SENSOR...</p>
            </div>
        )}
      </div>

      {/* RIGHT PANEL: Tactical Map */}
      <div className="panel" style={{padding: 0, overflow: 'hidden'}}>
        <div style={{position: 'absolute', top: '10px', left: '10px', fontSize: '0.8rem', background: 'rgba(0,0,0,0.8)', padding: '5px', zIndex: 10, color: 'var(--neon-cyan)'}}>TACTICAL MAP</div>
        <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: '#000'}}>
            {mapFrame ? (
                /* 🚀 SILVER BULLET FIX: Position Absolute applied to map too */
                <img src={`data:image/png;base64,${mapFrame}`} alt="Map" style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain'}} />
            ) : null}
        </div>
      </div>

      {/* BOTTOM PANEL: Telemetry Logs */}
      <div className="panel telemetry-log">
        {logs.map((log, i) => (
          <div key={i} className={`log-entry ${log.type === 'threat' ? 'log-threat' : log.type === 'strike' ? 'log-strike' : ''}`}>
            <span className="log-time">[{log.time}]</span> {log.msg}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>

    </div>
  );
}

export default App;
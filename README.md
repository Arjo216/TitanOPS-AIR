# TitanOPS-AIR
A distributed Air-Ground Collaborative Swarm Intelligence platform. Utilizes Graph Neural Networks (GNNs) and Heterogeneous Multi-Agent Reinforcement Learning (MARL) for dynamic threat routing and autonomous logistics.

# 🛡️ TitanOPS AIR: Overwatch Nexus Architecture

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-Vite-61DAFB.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-YOLO11-EE4C2C.svg)
![NetworkX](https://img.shields.io/badge/NetworkX-A*-green.svg)

> **A distributed, hardware-decoupled Command & Control (C2) architecture for autonomous drone swarm interception, integrating Deep Learning Vision pipelines with real-time heuristic pathfinding and Human-On-The-Loop (HOTL) autonomy.**

## 📖 Executive Summary

TitanOPS AIR is a highly scalable, autonomous targeting and routing simulator built on a first-principles systems engineering mindset. Designed to bridge the gap between heavy neural inference and lightweight edge execution, the architecture offloads raw visual data via WebSocket tunneling to a dedicated cloud GPU, returning deterministic geospatial coordinates to a local React-based command dashboard. 

This project demonstrates production-grade robotic control loops, dynamic spatial graphing, and strictly decoupled ML-to-UI microservices.

## 🏗️ System Architecture & Data Flow

The platform relies on a tripartite distributed architecture, ensuring that heavy tensor operations never block the event loop of the tactical UI.

```mermaid
graph TD;
    subgraph Edge Control Node [Local / GitHub Codespace]
        UI[React/Vite C2 Dashboard] <==> |WebSocket: Telemetry & Commands| WE[Python World Engine];
    end
    
    subgraph Cloud Neural Node [Google Colab T4 GPU]
        WE <==> |Ngrok Tunnel: Base64 Vision Frames| API[FastAPI / PyTorch];
        API --> YOLO[YOLO11 Object Detection];
        YOLO --> |Bounding Box Coordinates| API;
    end
    
    WE --> NX[NetworkX Spatial Graph];
    NX --> |A* Heuristic Search| UI;

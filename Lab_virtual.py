"""
LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA
Práctica: Determinación de Hierro en Sal de Mohr
Curso: QU-0301 Análisis Cuantitativo
Universidad de Costa Rica

Profesor: Douglas Venegas González
douglas.venegas@ucr.ac.cr

INSTALACIÓN:
pip install streamlit

EJECUCIÓN:
streamlit run Lab_virtual.py
"""

import streamlit as st
import webbrowser
import os
import tempfile
import time

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Lab Virtual - Sal de Mohr",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# HTML DEL SIMULADOR
# ============================================================================

SIMULADOR_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador de Pesado - Sal de Mohr</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        const PlayIcon = () => (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
        );
        
        const PauseIcon = () => (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
            </svg>
        );
        
        const RotateIcon = () => (
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
                <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
                <path d="M8 16H3v5"/>
            </svg>
        );

        const SaltWeighingSimulator = () => {
          const canvasRef = useRef(null);
          const [watchGlassPos, setWatchGlassPos] = useState({ x: 100, y: 200 });
          const [spatulaPos, setSpatulaPos] = useState({ x: 200, y: 150 });
          const [isDraggingGlass, setIsDraggingGlass] = useState(false);
          const [isDraggingSpatula, setIsDraggingSpatula] = useState(false);
          const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
          const [mass, setMass] = useState(0);
          const [isAdding, setIsAdding] = useState(false);
          const [particles, setParticles] = useState([]);
          const [isComplete, setIsComplete] = useState(false);
          const targetMass = 0.4903;
          const animationRef = useRef(null);

          const scalePos = { x: 450, y: 420 };
          const scaleSize = { width: 200, height: 18 };
          const watchGlassSize = { width: 70, height: 35 };
          const spatulaSize = { width: 80, height: 15 };
          const bottlePos = { x: 700, y: 150 };

          const isWatchGlassOnScale = () => {
            const glassBottom = watchGlassPos.y + watchGlassSize.height;
            const glassCenterX = watchGlassPos.x + watchGlassSize.width / 2;
            return (
              glassBottom >= scalePos.y - 30 &&
              glassBottom <= scalePos.y + 30 &&
              glassCenterX >= scalePos.x + 20 &&
              glassCenterX <= scalePos.x + scaleSize.width - 20
            );
          };

          const isSpatulaOverGlass = () => {
            const spatulaTipX = spatulaPos.x;
            const spatulaTipY = spatulaPos.y + spatulaSize.height / 2;
            return (
              spatulaTipX >= watchGlassPos.x &&
              spatulaTipX <= watchGlassPos.x + watchGlassSize.width &&
              spatulaTipY >= watchGlassPos.y &&
              spatulaTipY <= watchGlassPos.y + watchGlassSize.height
            );
          };

          const isSpatulaInBottle = () => {
            const spatulaTipX = spatulaPos.x;
            const spatulaTipY = spatulaPos.y;
            return (
              spatulaTipX >= bottlePos.x + 20 &&
              spatulaTipX <= bottlePos.x + 60 &&
              spatulaTipY >= bottlePos.y + 30 &&
              spatulaTipY <= bottlePos.y + 100
            );
          };

          const generateParticles = () => {
            if (!isAdding || mass >= targetMass || !isSpatulaOverGlass() || !isWatchGlassOnScale()) return;
            const newParticles = [];
            for (let i = 0; i < 2; i++) {
              newParticles.push({
                id: Date.now() + Math.random(),
                x: spatulaPos.x + (Math.random() - 0.5) * 20,
                y: spatulaPos.y + spatulaSize.height,
                vx: (Math.random() - 0.5) * 2,
                vy: Math.random() * 2 + 2,
                size: Math.random() * 3 + 2,
                opacity: 1,
                rotation: Math.random() * Math.PI * 2
              });
            }
            setParticles(prev => [...prev, ...newParticles]);
          };

          const updateParticles = () => {
            setParticles(prev => {
              const updated = prev.map(p => ({
                ...p,
                x: p.x + p.vx,
                y: p.y + p.vy,
                vy: p.vy + 0.3,
                rotation: p.rotation + 0.1,
                opacity: p.opacity - 0.015
              }))
              .filter(p => {
                if (p.y >= watchGlassPos.y + 10 && 
                    p.x >= watchGlassPos.x + 10 && 
                    p.x <= watchGlassPos.x + watchGlassSize.width - 10 &&
                    p.opacity > 0) {
                  setMass(m => {
                    const newMass = Math.min(m + 0.001, targetMass);
                    if (newMass >= targetMass) {
                      setIsComplete(true);
                      setIsAdding(false);
                    }
                    return newMass;
                  });
                  return false;
                }
                return p.y < watchGlassPos.y + 100 && p.opacity > 0;
              });
              return updated;
            });
          };

          useEffect(() => {
            const animate = () => {
              if (isAdding && isSpatulaOverGlass() && isWatchGlassOnScale() && mass < targetMass) {
                generateParticles();
              }
              updateParticles();
              animationRef.current = requestAnimationFrame(animate);
            };
            animationRef.current = requestAnimationFrame(animate);
            return () => {
              if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
              }
            };
          }, [isAdding, watchGlassPos, spatulaPos, mass]);

          useEffect(() => {
            const canvas = canvasRef.current;
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Fondo
            const bgGradient = ctx.createLinearGradient(0, 0, 0, 600);
            bgGradient.addColorStop(0, '#f0f4f8');
            bgGradient.addColorStop(1, '#d9e2ec');
            ctx.fillStyle = bgGradient;
            ctx.fillRect(0, 0, 900, 600);

            ctx.fillStyle = '#e8f0f7';
            ctx.fillRect(0, 0, 900, 380);

            ctx.strokeStyle = '#c5d4e0';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 380);
            ctx.lineTo(900, 380);
            ctx.stroke();

            const tableGradient = ctx.createLinearGradient(0, 380, 0, 600);
            tableGradient.addColorStop(0, '#9b7e5c');
            tableGradient.addColorStop(0.5, '#8b6f4f');
            tableGradient.addColorStop(1, '#7a5f42');
            ctx.fillStyle = tableGradient;
            ctx.fillRect(0, 380, 900, 220);

            // FRASCO
            const bottleWidth = 80;
            const bottleHeight = 120;
            
            const bottleShadowGradient = ctx.createRadialGradient(
              bottlePos.x + bottleWidth / 2, bottlePos.y + bottleHeight + 3, 5,
              bottlePos.x + bottleWidth / 2, bottlePos.y + bottleHeight + 3, 40
            );
            bottleShadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.3)');
            bottleShadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = bottleShadowGradient;
            ctx.beginPath();
            ctx.ellipse(bottlePos.x + bottleWidth / 2, bottlePos.y + bottleHeight + 3, 35, 8, 0, 0, Math.PI * 2);
            ctx.fill();

            const bottleGradient = ctx.createLinearGradient(
              bottlePos.x, bottlePos.y + 30,
              bottlePos.x + bottleWidth, bottlePos.y + 30
            );
            bottleGradient.addColorStop(0, 'rgba(180, 100, 30, 0.4)');
            bottleGradient.addColorStop(0.5, 'rgba(200, 120, 40, 0.6)');
            bottleGradient.addColorStop(1, 'rgba(180, 100, 30, 0.4)');
            ctx.fillStyle = bottleGradient;
            ctx.beginPath();
            ctx.roundRect(bottlePos.x + 10, bottlePos.y + 30, bottleWidth - 20, bottleHeight - 30, 5);
            ctx.fill();

            ctx.strokeStyle = '#8b5a00';
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.fillStyle = 'rgba(120, 80, 60, 0.7)';
            ctx.beginPath();
            ctx.roundRect(bottlePos.x + 15, bottlePos.y + 70, bottleWidth - 30, 45, 3);
            ctx.fill();

            ctx.fillStyle = '#2d3748';
            ctx.beginPath();
            ctx.roundRect(bottlePos.x + 15, bottlePos.y + 10, bottleWidth - 30, 25, 3);
            ctx.fill();

            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.beginPath();
            ctx.roundRect(bottlePos.x + 15, bottlePos.y + 40, bottleWidth - 30, 25, 2);
            ctx.fill();

            ctx.fillStyle = '#1e293b';
            ctx.font = 'bold 10px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Sal de Mohr', bottlePos.x + bottleWidth / 2, bottlePos.y + 50);
            ctx.font = '8px Arial';
            ctx.fillText('(NH₄)₂Fe(SO₄)₂', bottlePos.x + bottleWidth / 2, bottlePos.y + 60);

            if (isSpatulaInBottle()) {
              ctx.strokeStyle = '#3b82f6';
              ctx.lineWidth = 3;
              ctx.shadowColor = '#3b82f6';
              ctx.shadowBlur = 15;
              ctx.setLineDash([5, 5]);
              ctx.strokeRect(bottlePos.x + 5, bottlePos.y + 5, bottleWidth - 10, bottleHeight - 10);
              ctx.setLineDash([]);
              ctx.shadowBlur = 0;
            }

            // BALANZA (código completo del canvas anterior)
            const shadowGradient = ctx.createRadialGradient(
              scalePos.x + scaleSize.width / 2, scalePos.y + 100, 20,
              scalePos.x + scaleSize.width / 2, scalePos.y + 100, 120
            );
            shadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.15)');
            shadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = shadowGradient;
            ctx.beginPath();
            ctx.ellipse(scalePos.x + scaleSize.width / 2, scalePos.y + 100, 110, 20, 0, 0, Math.PI * 2);
            ctx.fill();

            const bodyGradient = ctx.createLinearGradient(
              scalePos.x, scalePos.y + 30,
              scalePos.x, scalePos.y + 90
            );
            bodyGradient.addColorStop(0, '#525d6b');
            bodyGradient.addColorStop(0.5, '#3d4654');
            bodyGradient.addColorStop(1, '#2d3542');
            ctx.fillStyle = bodyGradient;
            ctx.beginPath();
            ctx.roundRect(scalePos.x + 35, scalePos.y + 30, scaleSize.width - 70, 60, 8);
            ctx.fill();

            const platformGradient = ctx.createLinearGradient(
              scalePos.x, scalePos.y - 8,
              scalePos.x, scalePos.y + scaleSize.height + 5
            );
            platformGradient.addColorStop(0, '#f1f5f9');
            platformGradient.addColorStop(0.3, '#e2e8f0');
            platformGradient.addColorStop(0.7, '#cbd5e0');
            platformGradient.addColorStop(1, '#94a3b8');
            ctx.fillStyle = platformGradient;
            ctx.beginPath();
            ctx.roundRect(scalePos.x, scalePos.y - 5, scaleSize.width, scaleSize.height + 10, 4);
            ctx.fill();
            ctx.strokeStyle = '#64748b';
            ctx.lineWidth = 3;
            ctx.stroke();

            // Display
            const displayX = scalePos.x + 20;
            const displayY = scalePos.y + 38;
            const displayWidth = 160;
            const displayHeight = 45;

            ctx.fillStyle = '#1a1a1a';
            ctx.beginPath();
            ctx.roundRect(displayX, displayY, displayWidth, displayHeight, 6);
            ctx.fill();

            const lcdGradient = ctx.createLinearGradient(displayX, displayY, displayX, displayY + displayHeight);
            lcdGradient.addColorStop(0, '#0f1419');
            lcdGradient.addColorStop(1, '#1a2027');
            ctx.fillStyle = lcdGradient;
            ctx.beginPath();
            ctx.roundRect(displayX + 4, displayY + 4, displayWidth - 8, displayHeight - 8, 4);
            ctx.fill();

            ctx.font = 'bold 28px "Courier New", monospace';
            ctx.fillStyle = '#00ff88';
            ctx.shadowColor = '#00ff88';
            ctx.shadowBlur = 10;
            ctx.textAlign = 'right';
            ctx.fillText(`${mass.toFixed(4)}`, displayX + displayWidth - 35, displayY + 30);
            ctx.font = 'bold 16px Arial';
            ctx.fillText('g', displayX + displayWidth - 12, displayY + 30);
            ctx.shadowBlur = 0;

            const ledColor = isAdding ? '#00ff88' : '#ff6b6b';
            ctx.fillStyle = ledColor;
            ctx.shadowColor = ledColor;
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(displayX + 12, displayY + 12, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            // VIDRIO DE RELOJ
            const glassShadowGradient = ctx.createRadialGradient(
              watchGlassPos.x + watchGlassSize.width / 2, 
              watchGlassPos.y + watchGlassSize.height + 2, 5,
              watchGlassPos.x + watchGlassSize.width / 2, 
              watchGlassPos.y + watchGlassSize.height + 2, 35
            );
            glassShadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.3)');
            glassShadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = glassShadowGradient;
            ctx.beginPath();
            ctx.ellipse(
              watchGlassPos.x + watchGlassSize.width / 2, 
              watchGlassPos.y + watchGlassSize.height + 2, 
              watchGlassSize.width / 2, 8, 0, 0, Math.PI * 2
            );
            ctx.fill();

            const glassGradient = ctx.createRadialGradient(
              watchGlassPos.x + watchGlassSize.width / 2,
              watchGlassPos.y + watchGlassSize.height / 2, 0,
              watchGlassPos.x + watchGlassSize.width / 2,
              watchGlassPos.y + watchGlassSize.height / 2,
              watchGlassSize.width / 2
            );
            glassGradient.addColorStop(0, 'rgba(200, 230, 255, 0.3)');
            glassGradient.addColorStop(0.7, 'rgba(220, 240, 255, 0.5)');
            glassGradient.addColorStop(1, 'rgba(180, 220, 255, 0.4)');
            
            ctx.fillStyle = glassGradient;
            ctx.beginPath();
            ctx.ellipse(
              watchGlassPos.x + watchGlassSize.width / 2,
              watchGlassPos.y + watchGlassSize.height / 2,
              watchGlassSize.width / 2,
              watchGlassSize.height / 2, 0, 0, Math.PI * 2
            );
            ctx.fill();

            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // ESPÁTULA
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.beginPath();
            ctx.ellipse(spatulaPos.x + 40, spatulaPos.y + spatulaSize.height + 3, 35, 5, 0, 0, Math.PI * 2);
            ctx.fill();

            const handleGradient = ctx.createLinearGradient(
              spatulaPos.x + 40, spatulaPos.y,
              spatulaPos.x + 40, spatulaPos.y + spatulaSize.height
            );
            handleGradient.addColorStop(0, '#8b7355');
            handleGradient.addColorStop(1, '#6b5644');
            ctx.fillStyle = handleGradient;
            ctx.beginPath();
            ctx.roundRect(spatulaPos.x + 35, spatulaPos.y, 45, spatulaSize.height, 3);
            ctx.fill();

            const bladeGradient = ctx.createLinearGradient(
              spatulaPos.x, spatulaPos.y,
              spatulaPos.x, spatulaPos.y + spatulaSize.height
            );
            bladeGradient.addColorStop(0, '#e2e8f0');
            bladeGradient.addColorStop(0.5, '#cbd5e0');
            bladeGradient.addColorStop(1, '#94a3b8');
            ctx.fillStyle = bladeGradient;
            ctx.beginPath();
            ctx.moveTo(spatulaPos.x, spatulaPos.y + spatulaSize.height / 2);
            ctx.lineTo(spatulaPos.x + 35, spatulaPos.y + 2);
            ctx.lineTo(spatulaPos.x + 40, spatulaPos.y + 2);
            ctx.lineTo(spatulaPos.x + 40, spatulaPos.y + spatulaSize.height - 2);
            ctx.lineTo(spatulaPos.x + 35, spatulaPos.y + spatulaSize.height - 2);
            ctx.closePath();
            ctx.fill();

            ctx.strokeStyle = '#64748b';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            if (isSpatulaInBottle() && isAdding) {
              ctx.fillStyle = 'rgba(139, 92, 54, 0.8)';
              ctx.beginPath();
              ctx.ellipse(spatulaPos.x + 15, spatulaPos.y + spatulaSize.height / 2, 12, 5, 0, 0, Math.PI * 2);
              ctx.fill();
            }

            // Partículas
            particles.forEach(p => {
              ctx.save();
              ctx.translate(p.x, p.y);
              ctx.rotate(p.rotation);

              const particleGradient = ctx.createRadialGradient(-p.size/4, -p.size/4, 0, 0, 0, p.size);
              particleGradient.addColorStop(0, `rgba(230, 170, 120, ${p.opacity})`);
              particleGradient.addColorStop(0.5, `rgba(200, 140, 90, ${p.opacity})`);
              particleGradient.addColorStop(1, `rgba(139, 92, 54, ${p.opacity * 0.8})`);
              
              ctx.fillStyle = particleGradient;
              ctx.beginPath();
              ctx.arc(0, 0, p.size, 0, Math.PI * 2);
              ctx.fill();

              ctx.restore();
            });

            // Indicadores
            if (isWatchGlassOnScale()) {
              ctx.strokeStyle = '#10b981';
              ctx.lineWidth = 6;
              ctx.shadowColor = '#10b981';
              ctx.shadowBlur = 20;
              ctx.setLineDash([10, 10]);
              ctx.strokeRect(
                scalePos.x - 15, scalePos.y - 15,
                scaleSize.width + 30, scaleSize.height + 30
              );
              ctx.setLineDash([]);
              ctx.shadowBlur = 0;
            }

            ctx.textAlign = 'left';
          }, [watchGlassPos, spatulaPos, particles, mass, isAdding]);

          const handleMouseDown = (e) => {
            const rect = canvasRef.current.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const distToGlass = Math.sqrt(
              Math.pow(mouseX - (watchGlassPos.x + watchGlassSize.width / 2), 2) +
              Math.pow(mouseY - (watchGlassPos.y + watchGlassSize.height / 2), 2)
            );
            
            if (distToGlass < watchGlassSize.width / 2) {
              setIsDraggingGlass(true);
              setDragOffset({ x: mouseX - watchGlassPos.x, y: mouseY - watchGlassPos.y });
              return;
            }

            if (mouseX >= spatulaPos.x && mouseX <= spatulaPos.x + spatulaSize.width &&
                mouseY >= spatulaPos.y && mouseY <= spatulaPos.y + spatulaSize.height) {
              setIsDraggingSpatula(true);
              setDragOffset({ x: mouseX - spatulaPos.x, y: mouseY - spatulaPos.y });
            }
          };

          const handleMouseMove = (e) => {
            if (!isDraggingGlass && !isDraggingSpatula) return;
            const rect = canvasRef.current.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (isDraggingGlass) {
              setWatchGlassPos({
                x: Math.max(0, Math.min(mouseX - dragOffset.x, 900 - watchGlassSize.width)),
                y: Math.max(0, Math.min(mouseY - dragOffset.y, 550 - watchGlassSize.height))
              });
            }

            if (isDraggingSpatula) {
              setSpatulaPos({
                x: Math.max(0, Math.min(mouseX - dragOffset.x, 900 - spatulaSize.width)),
                y: Math.max(0, Math.min(mouseY - dragOffset.y, 550 - spatulaSize.height))
              });
            }
          };

          const handleMouseUp = () => {
            setIsDraggingGlass(false);
            setIsDraggingSpatula(false);
          };

          const toggleAdding = () => {
            if (isWatchGlassOnScale() && mass < targetMass && isSpatulaInBottle()) {
              setIsAdding(!isAdding);
            }
          };

          const reset = () => {
            setMass(0);
            setIsAdding(false);
            setParticles([]);
            setIsComplete(false);
            setWatchGlassPos({ x: 100, y: 200 });
            setSpatulaPos({ x: 200, y: 150 });
          };

          const percentComplete = (mass / targetMass) * 100;
          const canStartAdding = isWatchGlassOnScale() && isSpatulaInBottle();

          return (
            <div className="w-full h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 p-6 flex flex-col items-center">
              <div className="mb-4 text-center">
                <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-2xl">
                  🧪 Simulador de Pesado - Sal de Mohr
                </h1>
                <p className="text-indigo-200 text-sm">
                  Usa la espátula para transferir sal del frasco al vidrio de reloj
                </p>
              </div>

              <div className="relative">
                <canvas
                  ref={canvasRef}
                  width={900}
                  height={600}
                  className="rounded-2xl shadow-2xl cursor-grab active:cursor-grabbing border-4 border-indigo-400/30"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                />

                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-slate-800/90 backdrop-blur-md px-6 py-3 rounded-full shadow-2xl border-2 border-indigo-400/30">
                  <div className="flex items-center gap-3">
                    <span className="text-white font-semibold text-sm">Progreso:</span>
                    <div className="w-48 bg-slate-700 rounded-full h-3 overflow-hidden shadow-inner">
                      <div 
                        className="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 transition-all duration-300"
                        style={{ width: `${Math.min(percentComplete, 100)}%` }}
                      />
                    </div>
                    <span className="text-cyan-300 font-bold text-sm min-w-[50px]">
                      {percentComplete.toFixed(0)}%
                    </span>
                  </div>
                </div>

                {isComplete && (
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-green-400 to-emerald-500 text-white px-10 py-5 rounded-2xl shadow-2xl font-bold text-3xl animate-bounce border-4 border-white">
                    ✓ Pesado Completo
                  </div>
                )}

                {!isWatchGlassOnScale() && !isComplete && (
                  <div className="absolute bottom-4 left-4 bg-gradient-to-r from-amber-400 to-orange-500 text-slate-900 px-6 py-3 rounded-xl shadow-2xl font-bold text-sm border-2 border-amber-200">
                    📍 Paso 1: Coloca el vidrio de reloj sobre la balanza
                  </div>
                )}

                {isWatchGlassOnScale() && !isSpatulaInBottle() && !isComplete && (
                  <div className="absolute bottom-4 left-4 bg-gradient-to-r from-blue-400 to-cyan-500 text-white px-6 py-3 rounded-xl shadow-2xl font-bold text-sm border-2 border-blue-200">
                    🥄 Paso 2: Lleva la espátula al frasco de Sal de Mohr
                  </div>
                )}

                {canStartAdding && !isAdding && !isComplete && (
                  <div className="absolute bottom-4 left-4 bg-gradient-to-r from-green-400 to-emerald-500 text-white px-6 py-3 rounded-xl shadow-2xl font-bold text-sm border-2 border-green-200 animate-pulse">
                    ✓ Listo! Presiona "Agregar Sal"
                  </div>
                )}
              </div>

              <div className="mt-4 flex gap-4">
                <button
                  onClick={toggleAdding}
                  disabled={!canStartAdding || isComplete}
                  className={`flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-105 ${
                    canStartAdding && !isComplete
                      ? 'bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white shadow-xl'
                      : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  {isAdding ? (<><PauseIcon /> Detener</>) : (<><PlayIcon /> Agregar Sal</>)}
                </button>

                <button onClick={reset} className="flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl font-bold text-lg transition-all shadow-xl transform hover:scale-105">
                  <RotateIcon /> Reiniciar
                </button>
              </div>

              <div className="mt-4 bg-slate-800/80 backdrop-blur-md p-4 rounded-xl max-w-3xl text-slate-200 text-sm shadow-xl border border-indigo-400/30">
                <h3 className="font-bold text-white mb-2">📋 Instrucciones:</h3>
                <ol className="list-decimal list-inside space-y-1 text-xs">
                  <li>Arrastra el <span className="text-cyan-400 font-semibold">vidrio de reloj</span> sobre la balanza</li>
                  <li>Lleva la <span className="text-amber-400 font-semibold">espátula</span> al frasco</li>
                  <li>Presiona "Agregar Sal" y mueve sobre el vidrio</li>
                </ol>
              </div>
            </div>
          );
        };

        ReactDOM.render(<SaltWeighingSimulator />, document.getElementById('root'));
    </script>
</body>
</html>
"""

# ============================================================================
# FUNCIONES DE LA APLICACIÓN
# ============================================================================

def guardar_simulador():
    """Guarda el simulador en un archivo temporal y lo retorna"""
    try:
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', 
                                        encoding='utf-8') as f:
            f.write(SIMULADOR_HTML)
            return f.name
    except Exception as e:
        st.error(f"Error al crear el simulador: {e}")
        return None

def abrir_simulador_navegador():
    """Abre el simulador en una nueva pestaña del navegador"""
    temp_file = guardar_simulador()
    if temp_file:
        webbrowser.open('file://' + os.path.abspath(temp_file))
        return temp_file
    return None

# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    # Estilos CSS personalizados
    st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .section-box {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            margin-bottom: 1rem;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

    # Header principal
    st.markdown("""
        <div class="main-header">
            <h1>🧪 LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA</h1>
            <h3>Determinación de Hierro en Sal de Mohr por Permanganimetría</h3>
            <p>QU-0301 Análisis Cuantitativo | Universidad de Costa Rica</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Escudo_UCR.svg/1200px-Escudo_UCR.svg.png", width=150)
        st.markdown("### 👨‍🏫 Información del Curso")
        st.info("""
        **Profesor:**  
        Douglas Venegas González  
        douglas.venegas@ucr.ac.cr
        
        **Curso:**  
        QU-0301 Análisis Cuantitativo
        """)
        
        st.markdown("### 📚 Navegación")
        pagina = st.radio(
            "Seleccione una parte:",
            ["🏠 Inicio", "1️⃣ Preparación", "2️⃣ Pesado (Simulador)", "3️⃣ Valoración", "4️⃣ Cálculos"],
            key="navegacion"
        )

    # Contenido según la página seleccionada
    if pagina == "🏠 Inicio":
        mostrar_inicio()
    elif pagina == "1️⃣ Preparación":
        mostrar_preparacion()
    elif pagina == "2️⃣ Pesado (Simulador)":
        mostrar_pesado()
    elif pagina == "3️⃣ Valoración":
        mostrar_valoracion()
    elif pagina == "4️⃣ Cálculos":
        mostrar_calculos()

# ============================================================================
# PÁGINAS DE CONTENIDO
# ============================================================================

def mostrar_inicio():
    st.markdown("## 🎯 Objetivo de la Práctica")
    st.markdown("""
    <div class="section-box">
    Determinar el contenido de hierro (Fe²⁺) en una muestra de Sal de Mohr 
    [sulfato ferroso amónico hexahidratado: (NH₄)₂Fe(SO₄)₂·6H₂O] mediante 
    valoración con permanganato de potasio (KMnO₄).
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔬 Fundamento Teórico")
        st.markdown("""
        La **permanganimetría** es un método volumétrico de oxidación-reducción 
        basado en la reacción entre el ion permanganato (MnO₄⁻) y el ion ferroso (Fe²⁺).
        
        **Reacción principal:**
        ```
        MnO₄⁻ + 5Fe²⁺ + 8H⁺ → Mn²⁺ + 5Fe³⁺ + 4H₂O
        ```
        
        El punto final se detecta por el **viraje rosa persistente** debido al 
        exceso de permanganato.
        """)
    
    with col2:
        st.markdown("### 📋 Material y Reactivos")
        st.markdown("""
        **Material:**
        - Balanza analítica
        - Vidrio de reloj
        - Espátula
        - Erlenmeyer 250 mL
        - Bureta 50 mL
        
        **Reactivos:**
        - Sal de Mohr
        - KMnO₄ 0.02 M
        - H₂SO₄ 2 M
        - Agua destilada
        """)

    st.markdown("### 📝 Procedimiento General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("**Paso 1**\n\nPreparación de soluciones")
    with col2:
        st.success("**Paso 2**\n\nPesado de Sal de Mohr")
    with col3:
        st.warning("**Paso 3**\n\nValoración con KMnO₄")
    with col4:
        st.error("**Paso 4**\n\nCálculos y resultados")

def mostrar_preparacion():
    st.markdown("## 1️⃣ Preparación de Soluciones")
    
    tab1, tab2 = st.tabs(["💧 H₂SO₄ 2M", "🟣 KMnO₄ 0.02M"])
    
    with tab1:
        st.markdown("### Preparación de H₂SO₄ 2M (100 mL)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Datos")
            st.markdown("""
            - **Concentración deseada:** 2 M
            - **Volumen:** 100 mL
            - **H₂SO₄ concentrado:** 18 M
            """)
        
        with col2:
            st.markdown("#### 🧮 Cálculos")
            st.latex(r"M_1V_1 = M_2V_2")
            st.latex(r"V_1 = \frac{M_2 \times V_2}{M_1}")
            st.latex(r"V_1 = \frac{2\,M \times 100\,mL}{18\,M} = 11.11\,mL")
        
        st.success("✅ Se requieren **11.11 mL** de H₂SO₄ concentrado + agua hasta 100 mL")
        
        st.warning("⚠️ **PRECAUCIÓN:** Siempre agregar el ácido al agua, **NUNCA** al revés.")
    
    with tab2:
        st.markdown("### Preparación de KMnO₄ 0.02M (250 mL)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Datos")
            st.markdown("""
            - **Concentración deseada:** 0.02 M
            - **Volumen:** 250 mL = 0.25 L
            - **Masa molar KMnO₄:** 158.04 g/mol
            """)
        
        with col2:
            st.markdown("#### 🧮 Cálculos")
            st.latex(r"masa = M \times V \times MM")
            st.latex(r"masa = 0.02 \times 0.25 \times 158.04")
            masa = 0.02 * 0.25 * 158.04
            st.latex(f"masa = {masa:.4f}\,g")
        
        st.success(f"✅ Pesar **{masa:.4f} g** de KMnO₄ + agua hasta 250 mL")
        
        st.info("💡 Esta solución debe ser estandarizada antes de usar")

def mostrar_pesado():
    st.markdown("## 2️⃣ Pesado de Sal de Mohr")
    
    st.markdown("""
    <div class="section-box">
    <h3>🎯 Objetivo: Pesar 0.4903 g de Sal de Mohr</h3>
    <p>En esta sección utilizaremos un simulador interactivo para realizar el pesado 
    de la Sal de Mohr [(NH₄)₂Fe(SO₄)₂·6H₂O] utilizando vidrio de reloj y espátula.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Opción 1: Mostrar simulador embebido (iframe)
    st.markdown("### 🖥️ Opción 1: Simulador Embebido")
    st.info("El simulador se mostrará directamente aquí abajo:")
    
    # Guardar simulador y crear iframe
    temp_file = guardar_simulador()
    if temp_file:
        # Mostrar en iframe
        with open(temp_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        st.success("✅ Simulador cargado correctamente")
    
    st.markdown("---")
    
    # Opción 2: Botón para abrir en navegador
    st.markdown("### 🌐 Opción 2: Abrir en Nueva Ventana")
    st.info("Si el simulador no funciona correctamente arriba, ábrelo en una nueva pestaña:")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Abrir Simulador en Nueva Ventana", key="abrir_simulador"):
            temp_file = abrir_simulador_navegador()
            if temp_file:
                st.success("✅ Simulador abierto en el navegador")
                st.balloons()
            else:
                st.error("❌ Error al abrir el simulador")
    
    st.markdown("---")
    
    # Instrucciones
    st.markdown("### 📋 Instrucciones del Simulador")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Pasos a seguir:**
        1. 🔵 Arrastra el **vidrio de reloj** (círculo azul) hasta la balanza
        2. 🥄 Lleva la **espátula** al frasco de Sal de Mohr (frasco ámbar)
        3. ▶️ Presiona **"Agregar Sal"** cuando ambos estén en posición
        4. ↔️ Mueve la espátula sobre el vidrio de reloj
        5. 📊 Observa cómo aumenta la masa hasta **0.4903 g**
        """)
    
    with col2:
        st.markdown("""
        **Tips:**
        - 🖱️ Los objetos se arrastran con el mouse
        - ✅ La balanza mostrará la masa en tiempo real
        - 🟢 Indicadores verdes muestran posición correcta
        - 🔄 Usa "Reiniciar" si necesitas comenzar de nuevo
        - 📈 La barra de progreso muestra el avance
        """)
    
    # Datos para registro
    st.markdown("### 📝 Registro de Datos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        masa_registrada = st.number_input(
            "Masa pesada (g):", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.4903,
            step=0.0001,
            format="%.4f"
        )
    
    with col2:
        st.metric("Masa objetivo", "0.4903 g")
    
    with col3:
        diferencia = abs(masa_registrada - 0.4903)
        st.metric("Diferencia", f"{diferencia:.4f} g")
    
    if abs(diferencia) < 0.0005:
        st.success("✅ ¡Excelente! La masa está dentro del rango aceptable")
    elif abs(diferencia) < 0.001:
        st.warning("⚠️ La masa es aceptable pero podría mejorar")
    else:
        st.error("❌ La diferencia es demasiado grande. Intenta de nuevo")

def mostrar_valoracion():
    st.markdown("## 3️⃣ Valoración con KMnO₄")
    
    st.markdown("""
    <div class="section-box">
    <h3>⚗️ Procedimiento de Valoración</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Procedimiento paso a paso
    with st.expander("📋 Ver procedimiento completo", expanded=True):
        st.markdown("""
        1. Transferir la Sal de Mohr pesada a un erlenmeyer de 250 mL
        2. Disolver con **50 mL de H₂SO₄ 2M**
        3. Agregar agua destilada hasta ~100 mL
        4. Llenar la bureta con **KMnO₄ 0.02M**
        5. Valorar gota a gota hasta **viraje rosa persistente**
        """)
    
    st.markdown("### 🧪 Simulación de Valoración")
    
    if st.button("▶️ Iniciar Valoración", key="iniciar_valoracion"):
        progreso = st.progress(0)
        estado = st.empty()
        
        volumenes = [0, 5, 10, 15, 20, 23, 24, 24.5, 24.8]
        observaciones = [
            "Solución incolora",
            "Solución incolora",
            "Solución incolora",
            "Solución incolora", 
            "Solución incolora",
            "Ligero tinte rosa que desaparece",
            "Tinte rosa más persistente",
            "Rosa claro",
            "¡Viraje rosa persistente! ✅"
        ]
        
        for i, (v, obs) in enumerate(zip(volumenes, observaciones)):
            progreso.progress((i + 1) / len(volumenes))
            estado.info(f"**Volumen agregado:** {v:.1f} mL | **Observación:** {obs}")
            time.sleep(0.8)
        
        st.success("✅ **Valoración completada!** Volumen gastado: 24.8 mL")
        st.balloons()
    
    # Registro de datos
    st.markdown("### 📊 Registro de Datos Experimentales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vol_kmno4 = st.number_input(
            "Volumen KMnO₄ (mL):",
            min_value=0.0,
            max_value=50.0,
            value=24.8,
            step=0.1
        )
    
    with col2:
        conc_kmno4 = st.number_input(
            "Concentración KMnO₄ (M):",
            min_value=0.0,
            max_value=0.1,
            value=0.02,
            step=0.001,
            format="%.3f"
        )
    
    with col3:
        masa_sal = st.number_input(
            "Masa Sal de Mohr (g):",
            min_value=0.0,
            max_value=1.0,
            value=0.4903,
            step=0.0001,
            format="%.4f"
        )
    
    # Guardar en session state
    if 'datos_experimento' not in st.session_state:
        st.session_state.datos_experimento = {}
    
    st.session_state.datos_experimento = {
        'vol_kmno4': vol_kmno4,
        'conc_kmno4': conc_kmno4,
        'masa_sal': masa_sal
    }
    
    st.info(f"📝 Datos guardados para cálculos")

def mostrar_calculos():
    st.markdown("## 4️⃣ Cálculos y Resultados")
    
    # Obtener datos guardados
    if 'datos_experimento' in st.session_state:
        datos = st.session_state.datos_experimento
        vol_kmno4 = datos.get('vol_kmno4', 24.8)
        conc_kmno4 = datos.get('conc_kmno4', 0.02)
        masa_sal = datos.get('masa_sal', 0.4903)
    else:
        vol_kmno4 = 24.8
        conc_kmno4 = 0.02
        masa_sal = 0.4903
    
    st.markdown("### 📊 Datos del Experimento")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Masa Sal de Mohr", f"{masa_sal} g")
    col2.metric("Volumen KMnO₄", f"{vol_kmno4} mL")
    col3.metric("Conc. KMnO₄", f"{conc_kmno4} M")
    
    st.markdown("---")
    
    # Cálculos
    st.markdown("### 🧮 Cálculos Paso a Paso")
    
    # Paso 1
    with st.expander("📐 PASO 1: Moles de KMnO₄", expanded=True):
        st.latex(r"n(KMnO_4) = M \times V(L)")
        moles_kmno4 = conc_kmno4 * (vol_kmno4 / 1000)
        st.latex(f"n(KMnO_4) = {conc_kmno4} \\times {vol_kmno4/1000:.4f} = {moles_kmno4:.6f}\,mol")
        st.success(f"**Resultado:** {moles_kmno4:.6f} mol de KMnO₄")
    
    # Paso 2
    with st.expander("📐 PASO 2: Moles de Fe²⁺", expanded=True):
        st.markdown("**Reacción:**")
        st.latex(r"MnO_4^- + 5Fe^{2+} + 8H^+ \rightarrow Mn^{2+} + 5Fe^{3+} + 4H_2O")
        st.markdown("**Relación estequiométrica:** 1 mol MnO₄⁻ : 5 mol Fe²⁺")
        moles_fe = moles_kmno4 * 5
        st.latex(f"n(Fe^{{2+}}) = {moles_kmno4:.6f} \\times 5 = {moles_fe:.6f}\,mol")
        st.success(f"**Resultado:** {moles_fe:.6f} mol de Fe²⁺")
    
    # Paso 3
    with st.expander("📐 PASO 3: Porcentaje de Fe en la sal", expanded=True):
        mm_fe = 55.845
        masa_fe = moles_fe * mm_fe
        st.latex(f"masa(Fe) = {moles_fe:.6f} \\times {mm_fe} = {masa_fe:.4f}\,g")
        porcentaje_fe = (masa_fe / masa_sal) * 100
        st.latex(f"\\% Fe = \\frac{{{masa_fe:.4f}}}{{{masa_sal}}} \\times 100 = {porcentaje_fe:.2f}\\%")
        st.success(f"**Resultado:** {porcentaje_fe:.2f}% de Fe en la muestra")
    
    # Paso 4
    with st.expander("📐 PASO 4: Porcentaje Teórico y Error", expanded=True):
        mm_sal = 392.14
        porcentaje_teorico = (mm_fe / mm_sal) * 100
        st.markdown(f"**Porcentaje teórico de Fe en (NH₄)₂Fe(SO₄)₂·6H₂O:**")
        st.latex(f"\\% Fe_{{\,teorico}} = \\frac{{{mm_fe}}}{{{mm_sal}}} \\times 100 = {porcentaje_teorico:.2f}\\%")
        
        error_relativo = abs((porcentaje_fe - porcentaje_teorico) / porcentaje_teorico) * 100
        st.latex(f"Error = \\frac{{|{porcentaje_fe:.2f} - {porcentaje_teorico:.2f}|}}{{{porcentaje_teorico:.2f}}} \\times 100 = {error_relativo:.2f}\\%")
        
        if error_relativo < 5:
            st.success(f"✅ **Error relativo:** {error_relativo:.2f}% (Excelente)")
        elif error_relativo < 10:
            st.warning(f"⚠️ **Error relativo:** {error_relativo:.2f}% (Aceptable)")
        else:
            st.error(f"❌ **Error relativo:** {error_relativo:.2f}% (Alto)")
    
    st.markdown("---")
    
    # Resumen final
    st.markdown("### 📋 Resumen de Resultados")
    
    resultados_df = {
        "Parámetro": [
            "Moles de KMnO₄",
            "Moles de Fe²⁺",
            "Masa de Fe",
            "% Fe experimental",
            "% Fe teórico",
            "Error relativo"
        ],
        "Valor": [
            f"{moles_kmno4:.6f} mol",
            f"{moles_fe:.6f} mol",
            f"{masa_fe:.4f} g",
            f"{porcentaje_fe:.2f}%",
            f"{porcentaje_teorico:.2f}%",
            f"{error_relativo:.2f}%"
        ]
    }
    
    st.table(resultados_df)
    
    # Botón de descarga
    import pandas as pd
    df = pd.DataFrame(resultados_df)
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Descargar Resultados (CSV)",
        data=csv,
        file_name="resultados_sal_mohr.csv",
        mime="text/csv"
    )

# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()

def mostrar_patron_madre():
    st.markdown("## 1️⃣ Preparación de Solución Patrón Madre de Fe")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar una solución patrón madre de Fe a partir de Sal de Mohr 
    [(NH₄)₂Fe(SO₄)₂·6H₂O] para posteriormente preparar los patrones de la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⚖️ Paso 1: Pesado de Sal de Mohr")
    
    # Botón para abrir simulador
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🎮 Abrir Simulador de Pesado", type="primary", use_container_width=True):
            # Crear archivo temporal con el simulador
            SIMULADOR_PESADO = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador de Pesado - Sal de Mohr</title>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        const PlayIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
        );
        
        const PauseIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
            </svg>
        );
        
        const RotateIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
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
          const targetMass = 5.0;
          const minMass = 0.2;
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
                    const newMass = Math.min(m + 0.002, targetMass);
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

            // [TODO EL CÓDIGO DE DIBUJO DEL CANVAS - IGUAL QUE ANTES]
            // Fondo
            const bgGradient = ctx.createLinearGradient(0, 0, 0, 600);
            bgGradient.addColorStop(0, '#f0f4f8');
            bgGradient.addColorStop(1, '#d9e2ec');
            ctx.fillStyle = bgGradient;
            ctx.fillRect(0, 0, 900, 600);

            ctx.fillStyle = '#e8f0f7';
            ctx.fillRect(0, 0, 900, 380);

            const tableGradient = ctx.createLinearGradient(0, 380, 0, 600);
            tableGradient.addColorStop(0, '#9b7e5c');
            tableGradient.addColorStop(0.5, '#8b6f4f');
            tableGradient.addColorStop(1, '#7a5f42');
            ctx.fillStyle = tableGradient;
            ctx.fillRect(0, 380, 900, 220);

            // FRASCO (simplificado por espacio)
            const bottleWidth = 80;
            const bottleHeight = 120;
            
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

            // BALANZA
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

            // VIDRIO DE RELOJ
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

          const canStartAdding = isWatchGlassOnScale() && isSpatulaInBottle();

          return (
            <div className="w-full h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 p-6 flex flex-col items-center">
              <div className="mb-4 text-center">
                <h1 className="text-3xl font-bold text-white mb-2">
                  ⚖️ Simulador de Pesado - Sal de Mohr
                </h1>
                <p className="text-indigo-200 text-sm">
                  Rango: 0.2 - 5.0 g | Usa el mouse para arrastrar
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
                    <span className="text-white font-semibold">Masa Pesada:</span>
                    <span className="text-cyan-300 font-bold text-2xl">{mass.toFixed(4)} g</span>
                  </div>
                </div>

                {!isWatchGlassOnScale() && (
                  <div className="absolute bottom-4 left-4 bg-amber-400 text-slate-900 px-6 py-3 rounded-xl shadow-2xl font-bold text-sm">
                    📍 Coloca el vidrio de reloj sobre la balanza
                  </div>
                )}

                {isWatchGlassOnScale() && !isSpatulaInBottle() && (
                  <div className="absolute bottom-4 left-4 bg-blue-400 text-white px-6 py-3 rounded-xl shadow-2xl font-bold text-sm">
                    🥄 Lleva la espátula al frasco
                  </div>
                )}

                {canStartAdding && !isAdding && mass < minMass && (
                  <div className="absolute bottom-4 left-4 bg-green-400 text-white px-6 py-3 rounded-xl shadow-2xl font-bold text-sm animate-pulse">
                    ✓ Presiona "Agregar Sal"
                  </div>
                )}

                {mass >= minMass && (
                  <div className="absolute bottom-4 left-4 bg-green-500 text-white px-6 py-3 rounded-xl shadow-2xl font-bold text-sm">
                    ✅ Masa válida para continuar
                  </div>
                )}
              </div>

              <div className="mt-6 flex gap-4">
                <button
                  onClick={toggleAdding}
                  disabled={!canStartAdding || mass >= targetMass}
                  className={`flex items-center gap-2 px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                    canStartAdding && mass < targetMass
                      ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-xl'
                      : 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  {isAdding ? (<><PauseIcon /> Detener</>) : (<><PlayIcon /> Agregar Sal</>)}
                </button>

                <button
                  onClick={reset}
                  className="flex items-center gap-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold text-lg transition-all shadow-xl"
                >
                  <RotateIcon /> Reiniciar
                </button>
              </div>

              <div className="mt-6 bg-slate-800/80 backdrop-blur-md p-4 rounded-xl max-w-2xl text-slate-200 text-sm">
                <p className="font-semibold text-white mb-2">📋 Instrucciones:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Arrastra el <span className="text-cyan-400">vidrio de reloj</span> sobre la balanza</li>
                  <li>Lleva la <span className="text-amber-400">espátula</span> al frasco</li>
                  <li>Presiona "Agregar Sal" y mueve la espátula sobre el vidrio</li>
                  <li>Pesa entre 0.2 y 5.0 g según tu criterio</li>
                  <li>Cierra esta ventana y registra la masa en Streamlit</li>
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
            
            import webbrowser
            import tempfile
            import os
            
            try:
                with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', 
                                                encoding='utf-8') as f:
                    f.write(SIMULADOR_PESADO)
                    temp_path = f.name
                
                webbrowser.open('file://' + os.path.abspath(temp_path))
                st.success("✅ Simulador abierto en nueva ventana del navegador")
                st.info("💡 Después de pesar, registra la masa abajo")
                st.balloons()
            except Exception as e:
                st.error(f"Error al abrir simulador: {e}")
    
    st.markdown("---")
    
    # Registro de masa pesada
    st.markdown("### 📝 Registro de Masa Pesada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        masa_pesada = st.number_input(
            "Masa pesada en el simulador (g):",
            min_value=0.20,
            max_value=5.00,
            value=st.session_state.masa_sal_mohr if st.session_state.masa_sal_mohr else None,
            step=0.0001,
            format="%.4f",
            help="Ingresa exactamente la masa que obtuviste en el simulador"
        )
        
        if masa_pesada:
            st.session_state.masa_sal_mohr = masa_pesada
            st.success(f"✅ Masa registrada: {masa_pesada:.4f} g")
    
    with col2:
        if st.session_state.masa_sal_mohr:
            st.metric(
                "Masa Confirmada",
                f"{st.session_state.masa_sal_mohr:.4f} g",
                help="Esta masa se usará para los cálculos"
            )
            
            # Validación
            if st.session_state.masa_sal_mohr < 0.2:
                st.warning("⚠️ Masa muy baja (< 0.2 g)")
            elif st.session_state.masa_sal_mohr > 5.0:
                st.error("❌ Masa excede el máximo (> 5.0 g)")
            else:
                st.success("✅ Masa en rango válido")
    
    # Sección de aforo
    if st.session_state.masa_sal_mohr:
        st.markdown("---")
        st.markdown("### 🧪 Paso 2: Aforo del Patrón Madre")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Transferencia al Balón Aforado")
            st.info("Transfiere cuantitativamente la Sal de Mohr pesada a un balón aforado")
            
            volumen_balon = st.selectbox(
                "Selecciona el volumen del balón aforado (mL):",
                [None, 50, 100, 250, 500, 1000],
                format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
            )
            
            if volumen_balon:
                st.session_state.volumen_aforo_patron = volumen_balon
                st.success(f"✅ Balón de {volumen_balon} mL seleccionado")
        
        with col2:
            if st.session_state.volumen_aforo_patron:
                st.markdown("#### Aforar hasta la marca")
                st.info("Completa con agua destilada hasta la marca de aforo, usando una piseta")
                
                # Imagen ilustrativa (emoji)
                st.markdown("""
                <div style="text-align: center; font-size: 80px;">
                    🧪 💧
                </div>
                """, unsafe_allow_html=True)
    
    # Cálculos
    if st.session_state.masa_sal_mohr and st.session_state.volumen_aforo_patron:
        st.markdown("---")
        st.markdown("### 🧮 Cálculos Automáticos")
        
        conc_patron_madre = calcular_concentracion_patron_madre(
            st.session_state.masa_sal_mohr,
            st.session_state.volumen_aforo_patron
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Masa Sal de Mohr", f"{st.session_state.masa_sal_mohr:.4f} g")
        
        with col2:
            st.metric("Volumen Aforo", f"{st.session_state.volumen_aforo_patron} mL")
        
        with col3:
            st.metric(
                "Concentración Patrón Madre",
                f"{conc_patron_madre:.2f} mg/L",
                help="Concentración de Fe en la solución patrón madre"
            )
        
        # Mostrar cálculos detallados
        with st.expander("📐 Ver cálculos detallados"):
            mm_sal = 392.14
            mm_fe = 55.845
            moles_sal = st.session_state.masa_sal_mohr / mm_sal
            masa_fe_mg = moles_sal * mm_fe * 1000
            
            st.markdown(f"""
            **Paso 1: Cálculo de moles de Sal de Mohr**
            
            MM (NH₄)₂Fe(SO₄)₂·6H₂O = 392.14 g/mol
            
            n(Sal) = {st.session_state.masa_sal_mohr:.4f} g ÷ 392.14 g/mol = **{moles_sal:.6f} mol**
            
            ---
            
            **Paso 2: Moles de Fe (relación 1:1)**
            
            n(Fe) = **{moles_sal:.6f} mol**
            
            ---
            
            **Paso 3: Masa de Fe**
            
            MM Fe = 55.845 g/mol
            
            masa(Fe) = {moles_sal:.6f} mol × 55.845 g/mol = {moles_sal * mm_fe:.6f} g
            
            masa(Fe) = **{masa_fe_mg:.4f} mg**
            
            ---
            
            **Paso 4: Concentración en mg/L**
            
            C = masa(Fe) / Volumen(L)
            
            C = {masa_fe_mg:.4f} mg ÷ {st.session_state.volumen_aforo_patron/1000:.3f} L
            
            C = **{conc_patron_madre:.2f} mg/L**
            """)
        
        # Verificar si es adecuado para hacer patrones
        st.markdown("### 📊 Evaluación de la Concentración")
        
        if conc_patron_madre < 50:
            st.warning("""
            ⚠️ **La concentración del patrón madre es BAJA (< 50 mg/L)**
            
            - Será **difícil** preparar patrones en el rango 1-5 mg/L
            - Necesitarás tomar alícuotas muy grandes
            - Puede haber mayor error en las diluciones
            
            💡 **Recomendación:** 
            - Pesar más Sal de Mohr, o
            - Usar un balón de menor volumen
            """)
        elif conc_patron_madre > 500:
            st.info("""
            💡 **La concentración del patrón madre es ALTA (> 500 mg/L)**
            
            - Necesitarás tomar alícuotas muy pequeñas (< 1 mL)
            - Debes usar **micropipetas** o pipetas de precisión
            - El error relativo puede aumentar con volúmenes muy pequeños
            
            ✅ **Esto es aceptable** si tienes el equipo adecuado
            """)
        else:
            st.success("""
            ✅ **Concentración del patrón madre ÓPTIMA (50-500 mg/L)**
            
            - Podrás preparar fácilmente patrones en el rango 1-5 mg/L
            - Las alícuotas serán de tamaño manejable
            - Menor error en las diluciones
            
            🎯 Puedes continuar con la preparación de la curva de calibración
            """)
        
        st.session_state.conc_patron_madre = conc_patron_madre
        
        # Botón para continuar
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("➡️ Continuar a Curva de Calibración", type="primary", use_container_width=True):
                st.success("✅ Patrón madre preparado correctamente")
                st.info("👉 Ve a la **Etapa 2: Curva de Calibración** en el menú lateral")
                st.balloons()def mostrar_patron_madre()
    st.markdown("## 1️⃣ Preparación de Solución Patrón Madre de Fe")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar una solución patrón madre de Fe a partir de Sal de Mohr 
    [(NH₄)₂Fe(SO₄)₂·6H₂O] para posteriormente preparar los patrones de la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎮 Simulador Interactivo de Pesado")
    
    # Simulador embebido
    SIMULADOR_PESADO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { useState, useEffect, useRef } = React;
        
        const PlayIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
            </svg>
        );
        
        const PauseIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
            </svg>
        );
        
        const RotateIcon = () => (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
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
          const targetMass = 5.0; // Máximo 5g
          const minMass = 0.2; // Mínimo 0.2g
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
                    const newMass = Math.min(m + 0.002, targetMass);
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

            // BALANZA
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

          const confirmMass = () => {
            if (mass >= minMass && mass <= targetMass) {
              setIsComplete(true);
              setIsAdding(false);
              window.parent.postMessage({type: 'masa_pesada', value: mass}, '*');
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
            <div className="w-full bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900 p-4" style={{minHeight: '700px'}}>
              <div className="mb-3 text-center">
                <h2 className="text-2xl font-bold text-white mb-1">
                  ⚖️ Simulador de Pesado - Sal de Mohr
                </h2>
                <p className="text-indigo-200 text-sm">
                  Rango: 0.2 - 5.0 g
                </p>
              </div>

              <div className="relative">
                <canvas
                  ref={canvasRef}
                  width={900}
                  height={600}
                  className="rounded-xl shadow-2xl cursor-grab active:cursor-grabbing border-2 border-indigo-400/30 mx-auto"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                />

                <div className="absolute top-3 left-1/2 transform -translate-x-1/2 bg-slate-800/90 backdrop-blur-md px-4 py-2 rounded-full shadow-xl border border-indigo-400/30">
                  <div className="flex items-center gap-3">
                    <span className="text-white font-semibold text-sm">Masa:</span>
                    <span className="text-cyan-300 font-bold text-lg">{mass.toFixed(4)} g</span>
                  </div>
                </div>

                {!isWatchGlassOnScale() && !isComplete && (
                  <div className="absolute bottom-3 left-3 bg-amber-400 text-slate-900 px-4 py-2 rounded-lg shadow-xl font-bold text-xs">
                    📍 Coloca el vidrio de reloj sobre la balanza
                  </div>
                )}

                {isWatchGlassOnScale() && !isSpatulaInBottle() && !isComplete && (
                  <div className="absolute bottom-3 left-3 bg-blue-400 text-white px-4 py-2 rounded-lg shadow-xl font-bold text-xs">
                    🥄 Lleva la espátula al frasco
                  </div>
                )}

                {canStartAdding && !isAdding && !isComplete && mass < minMass && (
                  <div className="absolute bottom-3 left-3 bg-green-400 text-white px-4 py-2 rounded-lg shadow-xl font-bold text-xs animate-pulse">
                    ✓ Presiona "Agregar Sal"
                  </div>
                )}

                {mass >= minMass && mass < targetMass && !isComplete && (
                  <div className="absolute bottom-3 left-3 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-xl font-bold text-xs animate-pulse">
                    ✓ Masa válida - Presiona "Confirmar"
                  </div>
                )}

                {isComplete && (
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-green-500 text-white px-8 py-4 rounded-xl shadow-2xl font-bold text-xl animate-bounce border-4 border-white">
                    ✓ Masa Confirmada: {mass.toFixed(4)} g
                  </div>
                )}
              </div>

              <div className="mt-3 flex gap-3 justify-center">
                <button
                  onClick={toggleAdding}
                  disabled={!canStartAdding || isComplete || mass >= targetMass}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold text-sm transition-all ${
                    canStartAdding && !isComplete && mass < targetMass
                      ? 'bg-blue-500 hover:bg-blue-600 text-white shadow-lg'
                      : 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  {isAdding ? (<><PauseIcon /> Detener</>) : (<><PlayIcon /> Agregar Sal</>)}
                </button>

                <button
                  onClick={confirmMass}
                  disabled={mass < minMass || mass > targetMass || isComplete}
                  className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold text-sm transition-all ${
                    mass >= minMass && mass <= targetMass && !isComplete
                      ? 'bg-green-500 hover:bg-green-600 text-white shadow-lg animate-pulse'
                      : 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  ✓ Confirmar Masa
                </button>

                <button
                  onClick={reset}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold text-sm transition-all shadow-lg"
                >
                  <RotateIcon /> Reiniciar
                </button>
              </div>

              <div className="mt-3 bg-slate-800/80 backdrop-blur-md p-3 rounded-lg text-slate-200 text-xs">
                <p className="font-semibold text-white mb-1">📋 Instrucciones:</p>
                <ol className="list-decimal list-inside space-y-0.5">
                  <li>Arrastra el <span className="text-cyan-400">vidrio de reloj</span> sobre la balanza</li>
                  <li>Lleva la <span className="text-amber-400">espátula</span> al frasco de Sal de Mohr</li>
                  <li>Presiona "Agregar Sal" y mueve la espátula sobre el vidrio</li>
                  <li>Cuando tengas entre 0.2 y 5.0 g, presiona <span className="text-green-400">"Confirmar"</span></li>
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
    
    # Mostrar simulador embebido
    st.components.v1.html(SIMULADOR_PESADO, height=750, scrolling=False)
    
    # Escuchar mensaje del simulador
    st.markdown("""
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'masa_pesada') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: event.data.value
            }, '*');
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sección de aforo
    st.markdown("### 🧪 Aforo del Patrón Madre")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Transferir al Balón Aforado")
        st.info("Una vez pesada la Sal de Mohr, transfiérela cuantitativamente a un balón aforado")
        
        masa_pesada = st.number_input(
            "Confirma la masa pesada (g):",
            min_value=0.20,
            max_value=5.00,
            value=st.session_state.masa_sal_mohr if st.session_state.masa_sal_mohr else None,
            step=0.0001,
            format="%.4f",
            help="Ingresa la masa del simulador"
        )
        
        if masa_pesada and masa_pesada != st.session_state.masa_sal_mohr:
            st.session_state.masa_sal_mohr = masa_pesada
            st.success(f"✅ Masa registrada: {masa_pesada:.4f} g")
    
    with col2:
        st.markdown("#### Selección del Balón Aforado")
        volumen_balon = st.selectbox(
            "Volumen del balón aforado (mL):",
            [None, 50, 100, 250, 500, 1000],
            format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
        )
        
        if volumen_balon:
            st.success(f"✅ Volumen seleccionado: {volumen_balon} mL")
            st.session_state.volumen_aforo_patron = volumen_balon
    
    # Cálculos
    if st.session_state.masa_sal_mohr and st.session_state.volumen_aforo_patron:
        st.markdown("---")
        st.markdown("### 🧮 Cálculos Automáticos")
        
        conc_patron_madre = calcular_concentracion_patron_madre(
            st.session_state.masa_sal_mohr,
            st.session_state.volumen_aforo_patron
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Masa Sal de Mohr", f"{st.session_state.masa_sal_mohr:.4f} g")
        
        with col2:
            st.metric("Volumen Aforo", f"{st.session_state.volumen_aforo_patron} mL")
        
        with col3:
            st.metric(
                "Concentración Patrón Madre",
                f"{conc_patron_madre:.2f} mg/L",
                help="Concentración de Fe en la solución patrón madre"
            )
        
        # Mostrar cálculos detallados
        with st.expander("📐 Ver cálculos detallados"):
            st.markdown(f"""
            **Paso 1: Cálculo de moles de Sal de Mohr**
            
            Masa molar (NH₄)₂Fe(SO₄)₂·6H₂O = 392.14 g/mol
            
            n(Sal) = {st.session_state.masa_sal_mohr:.4f} g / 392.14 g/mol = {st.session_state.masa_sal_mohr/392.14:.6f} mol
            
            **Paso 2: Moles de Fe (relación 1:1)**
            
            n(Fe) = {st.session_state.masa_sal_mohr/392.14:.6f} mol
            
            **Paso 3: Masa de Fe**
            
            Masa molar Fe = 55.845 g/mol
            
            masa(Fe) = {st.session_state.masa_sal_mohr/392.14:.6f} mol × 55.845 g/mol = {(st.session_state.masa_sal_mohr/392.14)*55.845:.6f} g
            
            masa(Fe) = {((st.session_state.masa_sal_mohr/392.14)*55.845)*1000:.4f} mg
            
            **Paso 4: Concentración en mg/L**
            
            C = masa(Fe) / Volumen(L)
            
            C = {((st.session_state.masa_sal_mohr/392.14)*55.845)*1000:.4f} mg / {st.session_state.volumen_aforo_patron/1000:.3f} L
            
            C = {conc_patron_madre:.2f} mg/L
            """)
        
        # Verificar si es adecuado para hacer patrones
        if conc_patron_madre < 50:
            st.warning("⚠️ La concentración del patrón madre es baja. Será difícil preparar patrones en el rango 1-5 mg/L")
            st.info("💡 **Recomendación:** Considera pesar más Sal de Mohr o usar un balón de menor volumen")
        elif conc_patron_madre > 500:
            st.info("💡 La concentración del patrón madre es alta. Necesitarás alícuotas pequeñas para los patrones")
            st.success("✅ Esto es aceptable, pero asegúrate de tener pipetas precisas para alícuotas pequeñas")
        else:
            st.success("✅ Concentración del patrón madre adecuada para preparar la curva de calibración")
        
        st.session_state.conc_patron_madre = conc_patron_madre
        
        # Botón para continuar
        if st.button("➡️ Continuar a Curva de Calibración", type="primary"):
            st.success("✅ Patrón madre preparado correctamente. Ve a la siguiente etapa en el menú lateral.")
            st.balloons()"""
LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA
Práctica: Determinación de Hierro en Vinos por Absorción Atómica
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
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Lab Virtual - Fe en Vinos",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DATOS DE LOS VINOS (con concentraciones reales de Fe)
# ============================================================================

VINOS_DATABASE = {
    "Vino Tinto Reserva": {
        "imagen": "🍷",
        "color": "#8B0000",
        "concentracion_fe": 8.5,  # mg/L real en el vino
        "descripcion": "Vino tinto con cuerpo, crianza en barrica",
        "fd_sugerido": 2
    },
    "Vino Blanco Seco": {
        "imagen": "🥂",
        "color": "#FFD700",
        "concentracion_fe": 2.8,  # mg/L
        "descripcion": "Vino blanco ligero, afrutado",
        "fd_sugerido": 1
    },
    "Vino Rosado": {
        "imagen": "🌸",
        "color": "#FF69B4",
        "concentracion_fe": 4.2,  # mg/L
        "descripcion": "Vino rosado fresco y aromático",
        "fd_sugerido": 1
    },
    "Vino Tinto Joven": {
        "imagen": "🍇",
        "color": "#DC143C",
        "concentracion_fe": 12.3,  # mg/L
        "descripcion": "Vino tinto joven, intenso",
        "fd_sugerido": 3
    }
}

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if 'masa_sal_mohr' not in st.session_state:
    st.session_state.masa_sal_mohr = None

if 'volumen_aforo_patron' not in st.session_state:
    st.session_state.volumen_aforo_patron = None

if 'patrones_preparados' not in st.session_state:
    st.session_state.patrones_preparados = []

if 'vino_seleccionado' not in st.session_state:
    st.session_state.vino_seleccionado = None

if 'alicuota_vino' not in st.session_state:
    st.session_state.alicuota_vino = None

if 'volumen_aforo_muestra' not in st.session_state:
    st.session_state.volumen_aforo_muestra = None

if 'mediciones_aa' not in st.session_state:
    st.session_state.mediciones_aa = {}

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def calcular_concentracion_patron_madre(masa_sal, volumen_aforo):
    """
    Calcula la concentración de Fe en la solución patrón madre
    Sal de Mohr: (NH4)2Fe(SO4)2·6H2O
    MM = 392.14 g/mol
    MM Fe = 55.845 g/mol
    """
    if masa_sal is None or volumen_aforo is None:
        return None
    
    mm_sal = 392.14  # g/mol
    mm_fe = 55.845   # g/mol
    
    # Moles de sal
    moles_sal = masa_sal / mm_sal
    
    # Moles de Fe (1:1)
    moles_fe = moles_sal
    
    # Masa de Fe
    masa_fe = moles_fe * mm_fe  # g
    masa_fe_mg = masa_fe * 1000  # mg
    
    # Concentración en mg/L
    conc_mg_L = masa_fe_mg / (volumen_aforo / 1000)
    
    return conc_mg_L

def calcular_concentracion_patron(conc_madre, alicuota, volumen_aforo):
    """Calcula la concentración de un patrón por dilución"""
    if conc_madre is None:
        return None
    return (conc_madre * alicuota) / volumen_aforo

def generar_absorbancia(concentracion, curva_lineal=True):
    """
    Genera absorbancia basada en Ley de Beer
    Si curva_lineal=False, añade desviaciones
    """
    # Coeficiente de absorción típico para Fe a 248.3 nm
    k = 0.082  # L/(mg·cm)
    
    if curva_lineal:
        # Ley de Beer perfecta con pequeño ruido
        abs_teorica = k * concentracion
        ruido = np.random.normal(0, 0.002)
        return abs_teorica + ruido
    else:
        # Con desviaciones (concentraciones fuera de rango óptimo)
        abs_teorica = k * concentracion
        # Añadir desviaciones no lineales
        desviacion = np.random.normal(0, 0.02) + 0.01 * (concentracion - 3)**2
        return abs_teorica + desviacion

def calcular_fd_muestra(alicuota, volumen_aforo):
    """Calcula el factor de dilución de la muestra"""
    if alicuota is None or volumen_aforo is None:
        return None
    return volumen_aforo / alicuota

def verificar_rango_optimo(concentracion):
    """Verifica si la concentración está en rango óptimo (1-5 mg/L)"""
    return 1.0 <= concentracion <= 5.0

# ============================================================================
# ESTILOS CSS
# ============================================================================

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .wine-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #ddd;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .wine-card:hover {
        transform: scale(1.05);
        border-color: #DC143C;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.3);
    }
    .wine-card.selected {
        border-color: #DC143C;
        background-color: #FFF5F5;
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.3);
    }
    .section-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #DC143C;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #8B0000 0%, #DC143C 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(220, 20, 60, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# APLICACIÓN PRINCIPAL
# ============================================================================

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🍷 LABORATORIO VIRTUAL - QUÍMICA ANALÍTICA</h1>
            <h3>Determinación de Hierro en Vinos por Absorción Atómica</h3>
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
            "Seleccione una etapa:",
            [
                "🏠 Inicio",
                "1️⃣ Preparación Patrón Madre",
                "2️⃣ Curva de Calibración", 
                "3️⃣ Preparación de Muestra",
                "4️⃣ Medición AA",
                "5️⃣ Resultados"
            ],
            key="navegacion"
        )

    # Páginas
    if pagina == "🏠 Inicio":
        mostrar_inicio()
    elif pagina == "1️⃣ Preparación Patrón Madre":
        mostrar_patron_madre()
    elif pagina == "2️⃣ Curva de Calibración":
        mostrar_curva_calibracion()
    elif pagina == "3️⃣ Preparación de Muestra":
        mostrar_preparacion_muestra()
    elif pagina == "4️⃣ Medición AA":
        mostrar_medicion_aa()
    elif pagina == "5️⃣ Resultados":
        mostrar_resultados()

# ============================================================================
# PÁGINAS
# ============================================================================

def mostrar_inicio():
    st.markdown("## 🎯 Objetivo de la Práctica")
    st.markdown("""
    <div class="section-box">
    Determinar la concentración de hierro (Fe) en diferentes muestras de vino 
    mediante <b>Espectroscopía de Absorción Atómica (AA)</b>, utilizando el 
    método de curva de calibración.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔬 Fundamento Teórico")
        st.markdown("""
        La **Absorción Atómica** es una técnica analítica que mide la absorción 
        de radiación electromagnética por átomos libres en estado fundamental.
        
        **Ley de Beer-Lambert:**
        ```
        A = ε × b × c
        ```
        Donde:
        - A = Absorbancia
        - ε = Coeficiente de absorción molar
        - b = Longitud del camino óptico
        - c = Concentración
        
        **Longitud de onda para Fe:** 248.3 nm
        """)
    
    with col2:
        st.markdown("### 📋 Procedimiento General")
        st.info("""
        **Etapas del análisis:**
        
        1. **Preparación de Patrón Madre**
           - Pesar Sal de Mohr
           - Preparar solución patrón de Fe
        
        2. **Curva de Calibración**
           - Preparar 3-7 patrones (1-5 mg/L)
           - Medir absorbancias
        
        3. **Preparación de Muestra**
           - Seleccionar vino
           - Realizar dilución apropiada
        
        4. **Medición por AA**
           - Determinar absorbancia
        
        5. **Cálculos y Resultados**
        """)

    st.markdown("### 🍷 Muestras de Vino Disponibles")
    
    cols = st.columns(4)
    
    for i, (nombre, datos) in enumerate(VINOS_DATABASE.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="wine-card">
                <div style="font-size: 48px;">{datos['imagen']}</div>
                <h4>{nombre}</h4>
                <p style="color: {datos['color']}; font-weight: bold;">
                    {datos['descripcion']}
                </p>
            </div>
            """, unsafe_allow_html=True)

def mostrar_patron_madre():
    st.markdown("## 1️⃣ Preparación de Solución Patrón Madre de Fe")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar una solución patrón madre de Fe a partir de Sal de Mohr 
    [(NH₄)₂Fe(SO₄)₂·6H₂O] para posteriormente preparar los patrones de la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎮 Simulador de Pesado y Aforo")
    
    # Aquí iría el HTML del simulador de pesado (lo crearemos después)
    st.info("🖱️ **Instrucciones:** Usa el simulador para pesar la Sal de Mohr y aforar en el balón")
    
    # Simulador simplificado con inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚖️ Pesado de Sal de Mohr")
        masa_pesada = st.number_input(
            "Masa pesada (g):",
            min_value=0.20,
            max_value=5.00,
            value=None,
            step=0.0001,
            format="%.4f",
            help="Rango recomendado: 0.2 - 5.0 g"
        )
        
        if masa_pesada:
            st.success(f"✅ Masa registrada: {masa_pesada:.4f} g")
            st.session_state.masa_sal_mohr = masa_pesada
    
    with col2:
        st.markdown("#### 🧪 Aforo del Balón")
        volumen_balon = st.selectbox(
            "Volumen del balón aforado (mL):",
            [None, 50, 100, 250, 500, 1000],
            format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
        )
        
        if volumen_balon:
            st.success(f"✅ Volumen seleccionado: {volumen_balon} mL")
            st.session_state.volumen_aforo_patron = volumen_balon
    
    # Cálculos
    if st.session_state.masa_sal_mohr and st.session_state.volumen_aforo_patron:
        st.markdown("---")
        st.markdown("### 🧮 Cálculos Automáticos")
        
        conc_patron_madre = calcular_concentracion_patron_madre(
            st.session_state.masa_sal_mohr,
            st.session_state.volumen_aforo_patron
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Masa Sal de Mohr", f"{st.session_state.masa_sal_mohr:.4f} g")
        
        with col2:
            st.metric("Volumen Aforo", f"{st.session_state.volumen_aforo_patron} mL")
        
        with col3:
            st.metric(
                "Concentración Patrón Madre",
                f"{conc_patron_madre:.2f} mg/L",
                help="Concentración de Fe en la solución patrón madre"
            )
        
        # Verificar si es adecuado para hacer patrones
        if conc_patron_madre < 50:
            st.warning("⚠️ La concentración del patrón madre es baja. Será difícil preparar patrones en el rango 1-5 mg/L")
        elif conc_patron_madre > 500:
            st.info("💡 La concentración del patrón madre es alta. Necesitarás alícuotas pequeñas para los patrones")
        else:
            st.success("✅ Concentración del patrón madre adecuada para preparar la curva de calibración")
        
        st.session_state.conc_patron_madre = conc_patron_madre

def mostrar_curva_calibracion():
    st.markdown("## 2️⃣ Preparación de Curva de Calibración")
    
    if st.session_state.masa_sal_mohr is None:
        st.warning("⚠️ Primero debes preparar el patrón madre en la Etapa 1")
        return
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Preparar entre 3 y 7 soluciones patrón con concentraciones en el rango de 
    <b>1 a 5 mg/L</b> para construir la curva de calibración.
    </div>
    """, unsafe_allow_html=True)
    
    conc_madre = st.session_state.conc_patron_madre
    
    st.info(f"💡 Concentración del patrón madre: **{conc_madre:.2f} mg/L**")
    
    # Selector de número de patrones
    num_patrones = st.selectbox(
        "¿Cuántos patrones deseas preparar?",
        [3, 5, 7],
        help="Se recomienda mínimo 5 puntos para una buena curva"
    )
    
    st.markdown("### 🧪 Preparación de Patrones")
    
    patrones_data = []
    
    for i in range(num_patrones):
        st.markdown(f"#### Patrón {i+1}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            alicuota = st.number_input(
                f"Alícuota patrón madre (mL):",
                min_value=0.1,
                max_value=50.0,
                value=None,
                step=0.1,
                key=f"alicuota_{i}"
            )
        
        with col2:
            vol_aforo = st.selectbox(
                f"Volumen aforo (mL):",
                [None, 10, 25, 50, 100],
                format_func=lambda x: "Seleccione..." if x is None else f"{x} mL",
                key=f"aforo_{i}"
            )
        
        if alicuota and vol_aforo:
            conc_patron = calcular_concentracion_patron(conc_madre, alicuota, vol_aforo)
            
            with col3:
                st.metric("Concentración", f"{conc_patron:.3f} mg/L")
            
            with col4:
                if verificar_rango_optimo(conc_patron):
                    st.success("✅ En rango")
                else:
                    st.error("❌ Fuera de rango")
            
            patrones_data.append({
                'patron': i+1,
                'alicuota': alicuota,
                'volumen': vol_aforo,
                'concentracion': conc_patron,
                'en_rango': verificar_rango_optimo(conc_patron)
            })
    
    if len(patrones_data) == num_patrones:
        st.session_state.patrones_preparados = patrones_data
        
        # Resumen
        st.markdown("---")
        st.markdown("### 📊 Resumen de Patrones Preparados")
        
        df = pd.DataFrame(patrones_data)
        st.dataframe(df, use_container_width=True)
        
        # Verificar cuántos están en rango
        en_rango = sum([p['en_rango'] for p in patrones_data])
        
        if en_rango == num_patrones:
            st.success(f"✅ Todos los patrones ({en_rango}/{num_patrones}) están en el rango óptimo (1-5 mg/L)")
        else:
            st.warning(f"⚠️ Solo {en_rango}/{num_patrones} patrones están en el rango óptimo")

def mostrar_preparacion_muestra():
    st.markdown("## 3️⃣ Preparación de Muestra de Vino")
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Seleccionar una muestra de vino y preparar una dilución adecuada para que la 
    concentración final esté dentro del rango de la curva de calibración (1-5 mg/L).
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🍷 Selección de Muestra")
    
    # Mostrar vinos disponibles
    cols = st.columns(4)
    
    for i, (nombre, datos) in enumerate(VINOS_DATABASE.items()):
        with cols[i]:
            if st.button(
                f"{datos['imagen']}\n\n**{nombre}**\n\n{datos['descripcion']}",
                key=f"vino_{i}",
                use_container_width=True
            ):
                st.session_state.vino_seleccionado = nombre
    
    if st.session_state.vino_seleccionado:
        vino = VINOS_DATABASE[st.session_state.vino_seleccionado]
        
        st.success(f"✅ Vino seleccionado: **{st.session_state.vino_seleccionado}**")
        
        # Simulador de dilución
        st.markdown("### 🧪 Preparación de Dilución")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alicuota_vino = st.number_input(
                "Alícuota de vino (mL):",
                min_value=0.1,
                max_value=50.0,
                value=None,
                step=0.1,
                help="Volumen de vino a tomar"
            )
        
        with col2:
            volumen_aforo_muestra = st.selectbox(
                "Volumen de aforo (mL):",
                [None, 10, 25, 50, 100, 250],
                format_func=lambda x: "Seleccione..." if x is None else f"{x} mL"
            )
        
        if alicuota_vino and volumen_aforo_muestra:
            st.session_state.alicuota_vino = alicuota_vino
            st.session_state.volumen_aforo_muestra = volumen_aforo_muestra
            
            # Calcular factor de dilución y concentración esperada
            fd = volumen_aforo_muestra / alicuota_vino
            conc_real_vino = vino['concentracion_fe']
            conc_diluida = conc_real_vino / fd
            
            st.markdown("---")
            st.markdown("### 📊 Análisis de la Dilución")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Factor de Dilución", f"{fd:.2f}x")
            
            with col2:
                st.metric("Concentración Esperada", f"{conc_diluida:.3f} mg/L")
            
            with col3:
                if verificar_rango_optimo(conc_diluida):
                    st.success("✅ En rango óptimo")
                else:
                    if conc_diluida < 1.0:
                        st.error("❌ Muy diluido (< 1 mg/L)")
                    else:
                        st.error("❌ Muy concentrado (> 5 mg/L)")
            
            st.session_state.conc_muestra_diluida = conc_diluida

def mostrar_medicion_aa():
    st.markdown("## 4️⃣ Medición por Absorción Atómica")
    
    if not st.session_state.patrones_preparados:
        st.warning("⚠️ Primero debes preparar la curva de calibración en la Etapa 2")
        return
    
    st.markdown("""
    <div class="section-box">
    <h3>📋 Objetivo</h3>
    Realizar las mediciones de absorbancia de los patrones y la muestra en el 
    espectrómetro de absorción atómica.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔬 Simulador de Espectrómetro AA")
    
    # Aquí iría el simulador visual del AA (lo haremos después)
    
    tab1, tab2 = st.tabs(["📊 Medición de Patrones", "🍷 Medición de Muestra"])
    
    with tab1:
        st.markdown("#### Medición de Patrones para Curva de Calibración")
        
        patrones = st.session_state.patrones_preparados
        
        if st.button("🔥 Medir Todos los Patrones", key="medir_patrones"):
            # Verificar si los patrones están en rango
            todos_en_rango = all([p['en_rango'] for p in patrones])
            
            resultados_patrones = []
            
            for patron in patrones:
                conc = patron['concentracion']
                # Generar absorbancia basado en si están en rango
                abs_val = generar_absorbancia(conc, curva_lineal=todos_en_rango)
                
                resultados_patrones.append({
                    'Patrón': patron['patron'],
                    'Concentración (mg/L)': conc,
                    'Absorbancia': abs_val
                })
            
            st.session_state.mediciones_aa['patrones'] = resultados_patrones
            
            df_resultados = pd.DataFrame(resultados_patrones)
            st.dataframe(df_resultados, use_container_width=True)
            
            # Gráfico
            fig = px.scatter(
                df_resultados,
                x='Concentración (mg/L)',
                y='Absorbancia',
                title='Curva de Calibración',
                trendline='ols'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if todos_en_rango:
                st.success("✅ Curva de calibración lineal - Patrones en rango óptimo")
            else:
                st.warning("⚠️ Curva con desviaciones - Algunos patrones fuera de rango")
    
    with tab2:
        st.markdown("#### Medición de Muestra de Vino")
        
        if st.session_state.vino_seleccionado and hasattr(st.session_state, 'conc_muestra_diluida'):
            if st.button("🔥 Medir Muestra", key="medir_muestra"):
                conc_diluida = st.session_state.conc_muestra_diluida
                en_rango = verificar_rango_optimo(conc_diluida)
                
                # Generar absorbancia
                abs_muestra = generar_absorbancia(conc_diluida, curva_lineal=en_rango)
                
                st.session_state.mediciones_aa['muestra'] = {
                    'vino': st.session_state.vino_seleccionado,
                    'absorbancia': abs_muestra,
                    'concentracion_diluida': conc_diluida
                }
                
                st.metric("Absorbancia de la Muestra", f"{abs_muestra:.4f}")
                
                if en_rango:
                    st.success("✅ Absorbancia dentro del rango de la curva")
                else:
                    if conc_diluida < 1.0:
                        st.error("❌ Absorbancia muy baja - Muestra muy diluida")
                    else:
                        st.error("❌ Absorbancia muy alta - Muestra muy concentrada")
        else:
            st.info("Primero prepara la muestra en la Etapa 3")

def mostrar_resultados():
    st.markdown("## 5️⃣ Resultados y Cálculos")
    
    if 'patrones' not in st.session_state.mediciones_aa:
        st.warning("⚠️ Primero debes realizar las mediciones en la Etapa 4")
        return
    
    st.markdown("### 📊 Curva de Calibración Final")
    
    df_patrones = pd.DataFrame(st.session_state.mediciones_aa['patrones'])
    
    # Regresión lineal
    x = df_patrones['Concentración (mg/L)'].values
    y = df_patrones['Absorbancia'].values
    
    # Calcular pendiente e intercepto
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    # Coeficiente de determinación R²
    yhat = p(x)
    ybar = np.mean(y)
    ssreg = np.sum((yhat - ybar)**2)
    sstot = np.sum((y - ybar)**2)
    r2 = ssreg / sstot
    
    # Mostrar ecuación
    st.markdown(f"""
    **Ecuación de la recta:**
    
    A = {z[0]:.4f} × C + {z[1]:.4f}
    
    **Coeficiente de determinación:** R² = {r2:.4f}
    """)
    
    # Gráfico mejorado
    fig = go.Figure()
    
    # Puntos experimentales
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        name='Patrones',
        marker=dict(size=10, color='red')
    ))
    
    # Línea de regresión
    x_line = np.linspace(min(x), max(x), 100)
    y_line = p(x_line)
    
    fig.add_trace(go.Scatter(
        x=x_line,
        y=y_line,
        mode='lines',
        name='Regresión lineal',
        line=dict(color='blue', dash='dash')
    ))
    
    # Muestra (si existe)
    if 'muestra' in st.session_state.mediciones_aa:
        abs_muestra = st.session_state.mediciones_aa['muestra']['absorbancia']
        conc_muestra = st.session_state.mediciones_aa['muestra']['concentracion_diluida']
        
        fig.add_trace(go.Scatter(
            x=[conc_muestra],
            y=[abs_muestra],
            mode='markers',
            name='Muestra',
            marker=dict(size=15, color='green', symbol='star')
        ))
    
    fig.update_layout(
        title='Curva de Calibración para Fe por AA',
        xaxis_title='Concentración (mg/L)',
        yaxis_title='Absorbancia',
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Evaluación de la curva
    if r2 >= 0.995:
        st.success(f"✅ Excelente linealidad (R² = {r2:.4f})")
    elif r2 >= 0.99:
        st.info(f"✓ Buena linealidad (R² = {r2:.4f})")
    else:
        st.warning(f"⚠️ Linealidad aceptable (R² = {r2:.4f}) - Revisa los patrones")
    
    # Cálculo de concentración de la muestra
    if 'muestra' in st.session_state.mediciones_aa:
        st.markdown("---")
        st.markdown("### 🧮 Cálculo de Concentración en la Muestra")
        
        abs_muestra = st.session_state.mediciones_aa['muestra']['absorbancia']
        vino_nombre = st.session_state.mediciones_aa['muestra']['vino']
        
        # Calcular concentración a partir de la curva
        conc_calculada_diluida = (abs_muestra - z[1]) / z[0]
        
        # Factor de dilución
        fd = st.session_state.volumen_aforo_muestra / st.session_state.alicuota_vino
        
        # Concentración en el vino original
        conc_vino_original = conc_calculada_diluida * fd
        
        # Concentración real del vino
        conc_real = VINOS_DATABASE[vino_nombre]['concentracion_fe']
        
        # Error relativo
        error_relativo = abs((conc_vino_original - conc_real) / conc_real) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Absorbancia Medida", f"{abs_muestra:.4f}")
        
        with col2:
            st.metric("Conc. en Dilución", f"{conc_calculada_diluida:.3f} mg/L")
        
        with col3:
            st.metric("Factor de Dilución", f"{fd:.2f}x")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Concentración Calculada\n(Vino original)",
                f"{conc_vino_original:.2f} mg/L",
                help="Concentración de Fe calculada en el vino sin diluir"
            )
        
        with col2:
            st.metric(
                "Concentración Real",
                f"{conc_real:.2f} mg/L",
                help="Valor real de Fe en el vino"
            )
        
        with col3:
            if error_relativo < 5:
                delta_color = "normal"
                st.metric("Error Relativo", f"{error_relativo:.2f}%", delta=None, delta_color=delta_color)
                st.success("✅ Excelente precisión")
            elif error_relativo < 10:
                st.metric("Error Relativo", f"{error_relativo:.2f}%")
                st.info("✓ Buena precisión")
            else:
                st.metric("Error Relativo", f"{error_relativo:.2f}%")
                st.warning("⚠️ Error alto - Revisa el procedimiento")
        
        # Análisis detallado
        st.markdown("---")
        st.markdown("### 📝 Análisis del Resultado")
        
        with st.expander("Ver cálculos detallados", expanded=True):
            st.markdown(f"""
            **Paso 1: Cálculo de concentración en la dilución**
            
            Usando la ecuación de la recta:
            
            C = (A - b) / m
            
            C = ({abs_muestra:.4f} - {z[1]:.4f}) / {z[0]:.4f} = {conc_calculada_diluida:.3f} mg/L
            
            ---
            
            **Paso 2: Corrección por factor de dilución**
            
            C_original = C_diluida × FD
            
            C_original = {conc_calculada_diluida:.3f} × {fd:.2f} = {conc_vino_original:.2f} mg/L
            
            ---
            
            **Paso 3: Evaluación del resultado**
            
            - Vino analizado: **{vino_nombre}**
            - Concentración calculada: **{conc_vino_original:.2f} mg/L**
            - Concentración real: **{conc_real:.2f} mg/L**
            - Error relativo: **{error_relativo:.2f}%**
            """)
        
        # Recomendaciones
        if error_relativo > 10:
            st.markdown("#### 💡 Posibles causas del error elevado:")
            
            conc_diluida = st.session_state.mediciones_aa['muestra']['concentracion_diluida']
            
            if not verificar_rango_optimo(conc_diluida):
                if conc_diluida < 1.0:
                    st.warning("""
                    - ❌ La dilución fue **excesiva** (concentración < 1 mg/L)
                    - 💡 Recomendación: Usar un factor de dilución menor
                    - 📊 La absorbancia quedó por debajo del rango óptimo de la curva
                    """)
                else:
                    st.warning("""
                    - ❌ La dilución fue **insuficiente** (concentración > 5 mg/L)
                    - 💡 Recomendación: Usar un factor de dilución mayor
                    - 📊 La absorbancia quedó por encima del rango óptimo de la curva
                    """)
            
            if r2 < 0.995:
                st.warning("""
                - ❌ La curva de calibración tiene **baja linealidad**
                - 💡 Recomendación: Asegurar que todos los patrones estén en rango 1-5 mg/L
                - 📊 Algunos patrones pueden estar fuera del rango óptimo
                """)
    
    # Tabla resumen final
    st.markdown("---")
    st.markdown("### 📊 Tabla Resumen de Resultados")
    
    resumen_data = {
        "Parámetro": [
            "Masa Sal de Mohr",
            "Volumen Patrón Madre",
            "Conc. Patrón Madre",
            "Número de Patrones",
            "R² de la Curva",
            "Pendiente (m)",
            "Intercepto (b)",
        ],
        "Valor": [
            f"{st.session_state.masa_sal_mohr:.4f} g",
            f"{st.session_state.volumen_aforo_patron} mL",
            f"{st.session_state.conc_patron_madre:.2f} mg/L",
            f"{len(st.session_state.patrones_preparados)}",
            f"{r2:.4f}",
            f"{z[0]:.4f}",
            f"{z[1]:.4f}",
        ]
    }
    
    if 'muestra' in st.session_state.mediciones_aa:
        resumen_data["Parámetro"].extend([
            "Vino Analizado",
            "Alícuota Vino",
            "Factor de Dilución",
            "Absorbancia Muestra",
            "Conc. Calculada",
            "Conc. Real",
            "Error Relativo"
        ])
        resumen_data["Valor"].extend([
            vino_nombre,
            f"{st.session_state.alicuota_vino} mL",
            f"{fd:.2f}x",
            f"{abs_muestra:.4f}",
            f"{conc_vino_original:.2f} mg/L",
            f"{conc_real:.2f} mg/L",
            f"{error_relativo:.2f}%"
        ])
    
    df_resumen = pd.DataFrame(resumen_data)
    st.table(df_resumen)
    
    # Botón de descarga
    csv = df_resumen.to_csv(index=False)
    st.download_button(
        label="📥 Descargar Resultados (CSV)",
        data=csv,
        file_name="resultados_fe_vinos_aa.csv",
        mime="text/csv"
    )

# ============================================================================
# EJECUTAR APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    main()

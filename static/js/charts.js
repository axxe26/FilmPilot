// Obtener los datos de generos enviados desde el template 
const labelsEl = document.getElementById("genre-labels-data");
const countsEl = document.getElementById("genre-counts-data");

// Crear grafico de barras con generos mas vistos
if (labelsEl && countsEl) {
    const labels = JSON.parse(labelsEl.textContent);
    const counts = JSON.parse(countsEl.textContent);

    // Niveles de transparencia para diferenciar las barras
    const alphas = [0.85, 0.70, 0.55, 0.40, 0.28];

    new Chart(document.getElementById('genresChart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: labels.map((_, i) =>
                    `rgba(229, 9, 20, ${alphas[i] || 0.2})`
                ),
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#898781', font: { size: 12 } },
                    border: { display: false }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#ffffff', font: { size: 13 } },
                    border: { display: false }
                }
            }
        }
    });
}

// Crear grafico de estado del contenido del usuario
function initStatusChart() {

    // Obtener datos y elemento canva
    const labelsEl = document.getElementById("status-labels-data");
    const countsEl = document.getElementById("status-counts-data");
    const canvas   = document.getElementById('statusChart');

    // Verificar que existan los elementos necesarios
    if (!labelsEl || !countsEl || !canvas) return;

    // Evitar que inicialice el grafico mas de una vez
    if (canvas.dataset.initialized) return;
    canvas.dataset.initialized = 'true';

    const labels = JSON.parse(labelsEl.textContent);
    const counts = JSON.parse(countsEl.textContent);

    // Generar el grafico tipo dona
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.85)',   // Watching → azul
                    'rgba(34, 197, 94, 0.85)',    // Completed → verde
                    'rgba(245, 197, 24, 0.85)',   // Planned → amarillo
                    'rgba(239, 68, 68, 0.85)',    // Dropped → rojo
                ],
                borderColor: 'rgba(18, 18, 18, 0.8)',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        color: '#ffffff',
                        font: { size: 13 },
                        padding: 20,
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` ${ctx.label}: ${ctx.parsed} items`
                    }
                }
            }
        }
    });
}

// Inicializar el grafico una la pagina termina de cargar
document.addEventListener("DOMContentLoaded", () => {
    initStatusChart();
});
import { configurarControles } from "./controles.js";

const W = 600;
const H = 600;
const COLOR = [0, 143, 57]

const canvas = document.getElementById("pantalla");
const ctx = canvas.getContext("2d");

canvas.width = W
canvas.height = H

let dx = 0.0;
let dy = 0.0
let dz = 0.5

let angulo_xz = 0;
let angulo_yz = 0;

let is_rotando = false;

let figuras = [];

configurarControles(canvas, 
    function(dx, dy){
        angulo_xz += dx * 0.005;
        angulo_yz -= dy * 0.005;
    },
    function(){
        is_rotando = !is_rotando;
    }
);

async function cargarFiguras() {
    const respuesta = await fetch("./rosa_real/objeto.json");
    if (!respuesta.ok) {
        throw new Error("No se pudo cargar figuras.json");
    }
    const nombres = await respuesta.json();
    const figuras = [];
    for (const nombre of nombres) {
        const figura = await cargarFigura("./rosa_real/" + nombre);
        figuras.push(figura);
    }
    return figuras;
}

async function cargarFigura(ruta) {
    const respuesta = await fetch(ruta);

    if (!respuesta.ok){
        throw new Error('No se pudo cargar: ${ruta}');
    }
    const contenido = await respuesta.text();
    const vertices = [];
    const aristas = [];

    let color = [0, 143, 57];

    const lineas = contenido.split("\n");

    for (const linea of lineas) {

        const d = linea.trim().split(/\s+/);

        if (d[0] === "c") {
            color = [
                Number(d[1]),
                Number(d[2]),
                Number(d[3])
            ];
        }

        else if (d[0] === "v") {
            vertices.push([
                Number(d[1]),
                Number(d[2]),
                Number(d[3])
            ]);
        }

        else if (d[0] === "e") {
            aristas.push([
                Number(d[1]),
                Number(d[2])
            ]);
        }
    }
    return {vertices, aristas, color};

}

async function iniciar() {
    figuras = await cargarFiguras();
    console.log("Figuras cargadas:", figuras.length);
    requestAnimationFrame(loop);
}

function pantalla(p){
    const x = (p[0] + 1) / 2 * W;
    const y = (1 - p[1]) / 2 * H;
    return [x, y];
}

function proyectar(p){
    const x = p[0];
    const y = p[1];
    const z = p[2];
    return [x/z, y/z];
}

function trasladar(p, dx, dy, dz){
    return [p[0] + dx, p[1] + dy, p[2] + dz];
}


function rotar(p, angulo_xz, angulo_yz){
    let c = Math.cos(angulo_xz);
    let s = Math.sin(angulo_xz);
    p = [p[0]*c - p[2]*s, p[1], p[0]*s + p[2]*c];

    c = Math.cos(angulo_yz);
    s = Math.sin(angulo_yz);
    return[p[0], p[1]*c - p[2]*s, p[1]*s + p[2]*c];
}

function rotacion_auto(r, angulo_xz, angulo_yz, dt){
    if (r == true){
        return [angulo_xz + Math.PI/2*dt, angulo_yz + 0];
    }
    return [angulo_xz, angulo_yz];
}

function punto(p, color=COLOR, s=5){
    const [x, y] = pantalla(proyectar(p));
    ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    ctx.fillRect(x-s/2, y-s/2, s, s);
}

function linea(p1, p2, color=COLOR) {
    const [x1, y1] = pantalla(proyectar(p1));
    const [x2, y2] = pantalla(proyectar(p2));

    ctx.strokeStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    ctx.lineWidth = 2;

    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
}

function actualizar(dt){
    [angulo_xz, angulo_yz] = rotacion_auto(is_rotando, angulo_xz, angulo_yz, dt);
}

function render() {
    ctx.fillStyle = "black";
    ctx.fillRect(0, 0, W, H);

    for (const figura of figuras) {

        const vertices = figura.vertices;
        const aristas = figura.aristas;
        const color = figura.color;

        const movidos = [];

        for (const p of vertices) {

            const rotado = rotar(p, angulo_xz, angulo_yz);

            const trasladado = trasladar(rotado, dx, dy, dz);

            movidos.push(trasladado);}
        for (const arista of aristas) {
            const i = arista[0];
            const j = arista[1];
            linea(movidos[i], movidos[j], color);}

        for (const p of movidos) {
            punto(p, color);}
    }
}

let tiempoAnterior = null;

function loop(tiempoActual){
    if (tiempoAnterior === null){
        tiempoAnterior = tiempoActual;
    }

    const dt = (tiempoActual - tiempoAnterior)/1000;
    tiempoAnterior = tiempoActual;

    actualizar(dt);
    render();

    requestAnimationFrame(loop);
}
iniciar().catch(console.error);
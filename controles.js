export function configurarControles(canvas, alArrastrar, alTocar) {

    let arrastrando = false;
    let anteriorX = 0;
    let anteriorY = 0;

    let inicioX = 0;
    let inicioY = 0;
    let deslizando = false;

    const tolerancia = 10;

    canvas.addEventListener("pointerdown", function(evento) {
        arrastrando = true;
        deslizando = false;

        anteriorX = evento.clientX;
        anteriorY = evento.clientY;

        inicioX = evento.clientX;
        inicioY = evento.clientY;

        canvas.setPointerCapture(evento.pointerId);
    });

    canvas.addEventListener("pointermove", function(evento) {
        if (!arrastrando) {
            return;
        }

        if (evento.pointerType === "mouse" && evento.buttons ===0){
            arrastrando = false;
            return;
        }

        const movimientoX = evento.clientX - anteriorX;
        const movimientoY = evento.clientY - anteriorY;

        const distanciaX = evento.clientX - inicioX;
        const distanciaY = evento.clientY - inicioY;

        if (Math.hypot(distanciaX, distanciaY) > tolerancia) {
            deslizando = true;
        }

        if (deslizando) {
            alArrastrar(movimientoX, movimientoY);
        }

        anteriorX = evento.clientX;
        anteriorY = evento.clientY;
    });

    canvas.addEventListener("pointerup", function(evento) {
        if (!arrastrando) {
            return;
        }

        if (!deslizando) {
            alTocar();
        }

        arrastrando = false;

        if (canvas.hasPointerCapture(evento.pointerId)){
            canvas.releasePointerCapture(evento.pointerId);
        }
    });

    canvas.addEventListener("pointercancel", function(evento) {
        arrastrando = false;
    });
}
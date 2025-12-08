// archivo JS general (puedes agregar funciones globales aquí)
console.log('CLUB EL META - frontend activo');

// Ejemplo: refrescar stats en admin automáticamente cada 60s
if (window.location.pathname === '/admin') {
  setInterval( async () => {
    const resp = await fetch('/api/stats');
    if (resp.ok) {
      // recargar la página o actualizar los elementos
      location.reload();
    }
  }, 60000);
}

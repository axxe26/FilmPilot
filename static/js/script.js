
// Inicializar todos los eventos cuando la pagina ha cargado
document.addEventListener("DOMContentLoaded", () => {

    // Hero con cambio automatico de imagenes
    let currentIndex = 0;

    const bg1 = document.querySelector(".hero-bg");
    const bg2 = document.querySelector(".hero-bg.next");

    let isFirstActive = true;

    // Solo corre el hero si existen ambos fondos en esta página
    if (bg1 && bg2 && typeof images !== "undefined" && images.length) {

        // imagen inicial
        bg1.style.backgroundImage = `url('${images[0]}')`;

        function changeBackground() {
            currentIndex = (currentIndex + 1) % images.length;

            if (isFirstActive) {
                // bg2 entra
                bg2.style.backgroundImage = `url('${images[currentIndex]}')`;
                bg2.style.opacity = "1";
                bg1.style.opacity = "0";
            } else {
                // bg1 entra
                bg1.style.backgroundImage = `url('${images[currentIndex]}')`;
                bg1.style.opacity = "1";
                bg2.style.opacity = "0";
            }

            // alternar fondos
            isFirstActive = !isFirstActive;
        }

        setInterval(changeBackground, 5000);
    }

    // Carruseles
    document.querySelectorAll(".carousel-wrapper").forEach(wrapper => {

        const carousel = wrapper.querySelector(".carousel");
        const leftArrow = wrapper.querySelector(".left-arrow");
        const rightArrow = wrapper.querySelector(".right-arrow");

        if (!carousel || !leftArrow || !rightArrow) return;

        rightArrow.addEventListener("click", () => {
            carousel.scrollBy({ left: 300, behavior: "smooth" });
        });

        leftArrow.addEventListener("click", () => {
            carousel.scrollBy({ left: -300, behavior: "smooth" });
        });
    });

    // Contenido por genero
    const grid = document.getElementById("content-grid");
    const genreMenu = document.getElementById("genreMenu");


    if (genreMenu && grid) {

        // Cargar el contenido correspondiente al genero seleccionado
        function loadGenre(item) {

            
            genreMenu.querySelectorAll(".genre-item").forEach(i => {
                i.classList.remove("active");
            });

            
            item.classList.add("active");

            const genreId = item.dataset.id;

            fetch(`/api/genre/${genreId}/`)
                .then(res => res.json())
                .then(data => {

                    grid.style.opacity = "0";

                    setTimeout(() => {

                        grid.innerHTML = "";

                        data.forEach(content => {

                            const img = content.backdrop_path || content.poster_path;

                            if (!img) return;

                            grid.innerHTML += `
                                <div class="grid-item">
                                    <img src="https://image.tmdb.org/t/p/w500${img}">
                                </div>
                            `;

                        });

                        grid.style.opacity = "1";

                    }, 200);

                });
        }

        // Permitir seleccionar un genero desde el menu
        genreMenu.addEventListener("click", (e) => {

            const item = e.target.closest(".genre-item");

            if (!item) return;

            loadGenre(item);

        });

        // Cargar automaticamente el primer genero al inciar la pagina
        const firstGenre = genreMenu.querySelector(".genre-item");

        if (firstGenre) {
            loadGenre(firstGenre);
        }

        // Confiracion del desplazamiento horizontal del menu de generos
        const leftBtn = document.querySelector(".genre-arrow.left");
        const rightBtn = document.querySelector(".genre-arrow.right");

        if (rightBtn) {
            rightBtn.addEventListener("click", () => {
                genreMenu.scrollBy({ left: 300, behavior: "smooth" });
            });
        }

        if (leftBtn) {
            leftBtn.addEventListener("click", () => {
                genreMenu.scrollBy({ left: -300, behavior: "smooth" });
            });
        }
    }

    // Modal de registro
    const modal = document.querySelector(".modal-overlay");
    const openBtn = document.getElementById("openModal");

    // 
    if (modal && openBtn) {

        openBtn.addEventListener("click", () => {
            modal.classList.add("active");
        });

        const closeBtn = modal.querySelector("#closeModal");
        if (closeBtn) {
            closeBtn.addEventListener("click", () => {
                modal.classList.remove("active");
            });
        }

        const closeBtnUp = modal.querySelector("#closeModalUp");
        if (closeBtnUp) {
            closeBtnUp.addEventListener("click", () => {
                modal.classList.remove("active");
            });
        }
    }

    // Modal de inicio de sesion
    const loginBtn = document.getElementById("loginModalOverlay");
    const openLoginBtn = document.getElementById("openLoginModal");
    

    if (loginBtn && openLoginBtn) {

        openLoginBtn.addEventListener("click", () => {
            loginBtn.classList.add("active");
        });

        const closeLoginBtn = loginBtn.querySelector("#closeLoginModalBtn");
        if (closeLoginBtn) {
            closeLoginBtn.addEventListener("click", () => {
                loginBtn.classList.remove("active");
            });

        }

        const closeLoginUp = loginBtn.querySelector("#closeLoginModal");
        if (closeLoginUp) {
            closeLoginUp.addEventListener("click", () => {
                 loginBtn.classList.remove("active");
            });

        }

        
    }

    // Formulario de inicio de sesion 
    const loginForm = document.getElementById("modal-form");
    const loadingScreen = document.getElementById("loading-screen");

    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            loadingScreen.style.display = "flex";

            const formData = new FormData(loginForm);
            fetch("/login/", {
                method: "POST",
                body: formData
            })
            .then(res => {
                if (res.ok) {
                    window.location.href = "/loading/";
                } else {
                    return res.text().then(text => { throw new Error(text) });
                }
            })
            .catch(err => {
                loadingScreen.style.display = "none";
                alert("Login failed: " + err.message);
            });
        });
    }

});
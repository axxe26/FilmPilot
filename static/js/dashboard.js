// Inicializar todos los evento cuando el documento cargue
document.addEventListener("DOMContentLoaded", () => {
    // Navegacion entre secciones de dashboard
    const links = document.querySelectorAll("a[data-section]");

    links.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();

            const target = link.dataset.section;

            document.querySelectorAll(".section").forEach(sec => {
                sec.classList.remove("active");
            });

            document.getElementById(target).classList.add("active");

            if(target === "home-section"){
                homeDashboard.style.display = "block";

                document.querySelectorAll(".media-content").forEach(content => {
                    content.classList.remove("active");
                });
            }

            document.querySelectorAll(".sidebar a").forEach(a => {
                a.classList.remove("active");

            });
            
            link.classList.add("active")

            localStorage.setItem("activeSection", target);
        });
    });

    // Cambio entre pestañas (peliculas, tv y anime)
    const tabs = document.querySelectorAll("[data-media]");
    const homeDashboard = document.getElementById("home-dashboard");

    tabs.forEach(tab => {
        tab.addEventListener("click", function(e) {

            e.preventDefault();

            homeDashboard.style.display = "none";

            document.querySelectorAll(".media-content").forEach(content => {
                content.classList.remove("active");
            });

            document.querySelectorAll("[data-media]").forEach(btn => {
                btn.classList.remove("active");
            })

            const media = this.dataset.media;

            const mediaContent = document.getElementById(`${media}-content`);

            mediaContent.classList.add("active");

            this.classList.add("active")

            // Carga los resultados por defecto (All Genres) la primera
            // vez que se abre esta pestaña, para que no quede vacía.
            if (!mediaContent.dataset.loaded) {
                mediaContent.dataset.loaded = "true";

                if (media === "movies") applyFilters();
                else if (media === "tv") applyFiltersTV();
                else if (media === "anime") applyFiltersAnime();
            }
        });
    });

    // Card destacada con rotacion
    const data = JSON.parse(
        document.getElementById("contente-data").textContent
    );

    const img = document.getElementById("featured-img");
    const title = document.getElementById("featured-title");
    const genres = document.getElementById("featured-genres");

    let index = 0;

    function changeCard() {

        const item = data[index];

        const url = `https://image.tmdb.org/t/p/w780${item.backdrop_path || item.poster_path}`;

        const card = document.getElementById("featured-card");

        card.style.opacity = "0";

        setTimeout(() => {
            img.src = url;
            title.textContent = item.title || item.name;
            genres.textContent = item.genres;
            card.style.opacity = "1";
        }, 300);

        index = (index + 1) % data.length;
    }

    changeCard();
    setInterval(changeCard, 4000);



    // Configuracion del carrusel
    document.querySelectorAll(".carousel-wrapper").forEach(wrapper => {

    const carousel = wrapper.querySelector(".carousel");
    const track = wrapper.querySelector(".carousel-track");
    const leftZone = wrapper.querySelector(".left-zone");
    const rightZone = wrapper.querySelector(".right-zone");
    const leftArrow = wrapper.querySelector(".left-arrow");
    const rightArrow = wrapper.querySelector(".right-arrow");

    let scrollInterval;



    rightArrow.addEventListener("click", () => {
        carousel.scrollBy({ left: 300, behavior: "smooth" });
    });

    leftArrow.addEventListener("click", () => {
        carousel.scrollBy({ left: -300, behavior: "smooth" });
    });

    });

    // Sidebar
    const logo = document.getElementById("toggle-sidebar");
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content")

    logo.addEventListener("click", () => {
        sidebar.classList.toggle("closed");
        mainContent.classList.toggle("expanded");
    })

    // Buscador global
    const searchBtn = document.getElementById("search-btn")
    const searchContainer = document.querySelector(".search-container")
    const searchInput = document.querySelector(".search-input")

    searchBtn.addEventListener("click", () => {
        searchContainer.classList.toggle("active")

        if (searchContainer.classList.contains("active")) {
            searchInput.focus();
        }

    });

   

    const searchDropdown = document.createElement("div");
    searchDropdown.className = "search-results-dropdown";
    searchContainer.appendChild(searchDropdown);

    let searchDebounce;

    // Renderizar los resultados obtenidos en la busqueda
    function renderSearchResults(results) {

        if (!results.length) {
            searchDropdown.innerHTML =
                '<p class="search-no-results">No results found</p>';
            searchDropdown.classList.add("active");
            return;
        }

        searchDropdown.innerHTML = results.map(item => {

            const poster = item.poster_path
                ? `https://image.tmdb.org/t/p/w92${item.poster_path}`
                : DEFAULT_POSTER;

            const badge = item.media_type === "movie"
                ? "Movie"
                : (item.is_anime ? "Anime" : "TV");

            const year = item.release_date
                ? item.release_date.slice(0, 4)
                : "";

            return `
                <div
                    class="search-result-item"
                    data-id="${item.id}"
                    data-type="${item.media_type}"
                >
                    <img src="${poster}" alt="${item.title}">
                    <div class="search-result-info">
                        <p class="search-result-title">${item.title}</p>
                        <p class="search-result-meta">
                            ${badge}${year ? " · " + year : ""}
                        </p>
                    </div>
                </div>
            `;
        }).join("");

        searchDropdown.classList.add("active");
    }

    // Realizar la busqueda global mientras el usuario escribe
    if (searchInput) {
        searchInput.addEventListener("input", () => {

            clearTimeout(searchDebounce);

            const query = searchInput.value.trim();

            if (!query) {
                searchDropdown.classList.remove("active");
                searchDropdown.innerHTML = "";
                return;
            }

            searchDebounce = setTimeout(() => {
                fetch(`/search/global/?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => renderSearchResults(data.results))
                    .catch(err => console.error("Global search error:", err));
            }, 300);
        });
    }

    // Redirigir al detalle relacionado al contenido
    searchDropdown.addEventListener("click", (e) => {
        const item = e.target.closest(".search-result-item");
        if (!item) return;

        window.location.href = `/details/${item.dataset.type}/${item.dataset.id}/`;
    });

    document.addEventListener("click", (e) => {
        if (!searchContainer.contains(e.target)) {
            searchDropdown.classList.remove("active");
        }
    });

    // Modal de perfil
    const profilModal = document.getElementById("profileModal");

    document
        .getElementById("openProfileModal")
        .addEventListener("click", () => {
            profilModal.style.display = "flex";
    });

    document
        .getElementById("closeProfileModal")
        .addEventListener("click", () => {
            profilModal.style.display = "none";
    });

    document
        .getElementById("closeProfileModalBtn")
        .addEventListener("click", () => {
            profilModal.style.display = "none";
    });

    // Permitir seleccionar y previsualizar una nueva foto de perfil
    const changePictureBtn = document.getElementById("change-picture-btn");
    const profilePictureInput = document.getElementById("profilePicture");
    const profilePreview = document.getElementById("profilePicturePreview")

    changePictureBtn.addEventListener("click", () => {
        profilePictureInput.click();

    });


    profilePictureInput.addEventListener("change", function () {
        const file = this.files[0];

        if (file) {
            profilePreview.src = URL.createObjectURL(file);
        }
    });

    // Filtro de paliculas
     function applyFilters() {

        const genre = document.getElementById("genre-filter").value;
        const popularity = document.getElementById("popularity-filter").value;
        const releaseDate = document.getElementById("release-date-filter").value;
        const upcoming = document.getElementById("upcoming-filter").value;
        const search = document.getElementById("search-movies-input").value;

        fetch(
            `/movies/filter/?genre=${genre}&popularity=${popularity}&release_date=${releaseDate}&upcoming=${upcoming}&search=${search}`
        )

        .then(response => {
            console.log(response);
            return response.json();
        })

    
        .then(data => {
            renderMovies(data.results);
            console.log(data.results.length);
        });
    }
    // Mostrar las peliculas obtenidas en la interfaz
    function renderMovies(movies) {

        const container = 
            document.getElementById("movies-selection-container");

        container.innerHTML= "";

        movies.forEach(movie => {

            const poster = 
                movie.poster_path
                ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                : DEFAULT_POSTER;

            container.innerHTML += `
                <div 
                    class="movie-card"
                    data-id="${movie.id}"
                    data-type="movie"
                >
                    <img src="${poster}" alt="${movie.title}">
                </div>
            `;
        });
    }

    // Filtros de series
    function applyFiltersTV() {

        const tv_genre = document.getElementById("tv-genre-filter").value;
        const tv_popularity = document.getElementById("tv-popularity-filter").value;
        const tv_releaseDate = document.getElementById("tv-release-date-filter").value;
        const tv_upcoming = document.getElementById("tv-upcoming-filter").value;
        const tv_search = document.getElementById("search-tv-input").value;

        fetch(
            `/tv/filter/?genre=${tv_genre}&popularity=${tv_popularity}&release_date=${tv_releaseDate}&upcoming=${tv_upcoming}&search=${tv_search}`
        )

        .then(response => {
            console.log(response);
            return response.json();
        })

    
        .then(data => {
            renderTV(data.results);
            console.log(data.results.length);
        });
    }

    // Muestra las series obtenidas en la interfaz
    function renderTV(tvList) {

        const container = 
            document.getElementById("tv-selection-container");

        container.innerHTML= "";

        tvList.forEach(tv => {

            const poster = 
                tv.poster_path
                ? `https://image.tmdb.org/t/p/w500${tv.poster_path}`
                : DEFAULT_POSTER;

            container.innerHTML += `
                <div
                    class="tv-card"
                    data-id="${tv.id}"
                    data-type="tv"
                >
                    <img src="${poster}" alt="${tv.name}">
                </div>
            `;
        });
    }

    // Consultar los animes segun filtros seleccionados
    function applyFiltersAnime() {

        const genre = document.getElementById("anime-genre-filter").value;
        const popularity = document.getElementById("anime-popularity-filter").value;
        const releaseDate = document.getElementById("anime-release-date-filter").value;
        const search = document.getElementById("search-anime-input").value;

        fetch(`/anime/filter/?genre=${genre}&popularity=${popularity}&release_date=${releaseDate}&search=${search}`)
            .then(res => res.json())
            .then(data => renderAnime(data.results));
    }

    // Mostrar animes obtenidos en la interfaz
    function renderAnime(list) {

        const container = document.getElementById("anime-selection-container");
        container.innerHTML = "";

        list.forEach(anime => {

            const poster =
                anime.poster_path ||
                anime.backdrop_path
                    ? `https://image.tmdb.org/t/p/w500${anime.poster_path || anime.backdrop_path}`
                    : DEFAULT_POSTER;

            container.innerHTML += `
                <div 
                    class="anime-card"
                    data-id="${anime.id}"
                    data-type="tv"
                >
                    <img src="${poster}" alt="${anime.name || anime.title}">
                </div>
            `;
        });
    }

    document.addEventListener("click", (e) => {

        const card = e.target.closest(
            "[data-id][data-type]"  
        );

        if (!card) return;

        const id = card.dataset.id;
        const type = card.dataset.type;

        window.location.href =
            `/details/${type}/${id}/`;
    });


    // Eventos de los filtros 

    document.getElementById("genre-filter")
    .addEventListener("change", applyFilters);

    document.getElementById("popularity-filter")
    .addEventListener("change", applyFilters);

    document.getElementById("release-date-filter")
    .addEventListener("change", applyFilters);

    document.getElementById("search-movies-input")
    .addEventListener("input", applyFilters);


    document.getElementById("tv-genre-filter")
    .addEventListener("change", applyFiltersTV);

    document.getElementById("tv-popularity-filter")
    .addEventListener("change", applyFiltersTV);

    document.getElementById("tv-release-date-filter")
    .addEventListener("change",applyFiltersTV);

    document.getElementById("tv-upcoming-filter")
    .addEventListener("change", applyFiltersTV);

    document.getElementById("search-tv-input")
    .addEventListener("input", applyFiltersTV);



    document.getElementById("anime-genre-filter")
    .addEventListener("change", applyFiltersAnime);

    document.getElementById("anime-popularity-filter")
    .addEventListener("change", applyFiltersAnime);

    document.getElementById("anime-release-date-filter")
    .addEventListener("change", applyFiltersAnime);

    document.getElementById("search-anime-input")
    .addEventListener("input", applyFiltersAnime);


    // Restaura la seccion activa del dashboard
    const savedSection = localStorage.getItem("activeSection");

    if (savedSection) {
        document.querySelectorAll(".section").forEach(sec => {
            sec.classList.remove("active");
        });

        const target = document.getElementById(savedSection);
        if (target) target.classList.add("active");

        document.querySelectorAll(".sidebar a").forEach(a => {
            a.classList.remove("active");
        });

        const activeLink = document.querySelector(`a[data-section="${savedSection}"]`);
        if (activeLink) activeLink.classList.add("active");

        if (savedSection === "home-section") {
            homeDashboard.style.display = "block";
        } else {
            homeDashboard.style.display = "none";
        }
    }

    // dropdown borrar visualmente la actividad reciente
    const dropdownBtn  = document.getElementById('dropdownBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');

    if (dropdownBtn && dropdownMenu) {
        dropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            dropdownMenu.classList.remove('active');
        });
    }

    // borrar historia
    const clearBtn = document.getElementById('clearHistoryBtn');

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            // Guardar timestamp del borrado
            localStorage.setItem('activityClearedAt', Date.now().toString());

            // Limpiar visualmente
            const recentItem = document.querySelector('.recent-item');
            if (recentItem) {
                recentItem.innerHTML = '<p class="no-activity">No hay actividad reciente 🎬</p>';
            }

            dropdownMenu.classList.remove('active');
        });
    }

    // Filtrar al recargar
    const clearedAt = localStorage.getItem('activityClearedAt');

    if (clearedAt) {
        const clearedTimestamp = parseInt(clearedAt);
        const recentItem = document.querySelector('.recent-item');

        if (recentItem) {
            const entries = recentItem.querySelectorAll('.recent-entry');
            let visibleCount = 0;

            entries.forEach(entry => {
                const entryDate = entry.dataset.date;
                if (!entryDate) {
                    entry.remove();
                    return;
                }

                // Convierte la fecha del entry a timestamp
                const entryTimestamp = new Date(entryDate).getTime();

                if (entryTimestamp <= clearedTimestamp) {
                    entry.remove();  
                } else {
                    visibleCount++;  
                }
            });

            if (visibleCount === 0) {
                recentItem.innerHTML = '<p class="no-activity">No hay actividad reciente 🎬</p>';
            }
        }
    }

});